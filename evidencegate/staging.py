"""Verify a real ZIP, run its owned billing service, and measure canaries/drift."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
from itertools import product
import json
from pathlib import Path
import tempfile
import threading
import urllib.error
import urllib.request
import zipfile
from .audit import replay
from .packaging import verified_package
from .polynomial import parse, extract, evaluate

class BillingHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,status,body):
        raw=json.dumps(body).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def intact(self):
        try:return replay(self.server.project,self.server.receipt)['release_allowed']
        except (ValueError,OSError):return False
    def do_GET(self):
        if self.path!='/health':return self.reply(404,{'error':'Not found'})
        ok=self.intact();return self.reply(200 if ok else 503,{'status':'verified' if ok else 'source_drift','receipt_id':self.server.receipt['receipt_id']})
    def do_POST(self):
        if self.path!='/invoice':return self.reply(404,{'error':'Not found'})
        if not self.intact():return self.reply(503,{'error':'Source or contract drift blocks billing'})
        try:
            size=int(self.headers.get('Content-Length',0))
            if not 0<size<=2048:raise ValueError('Input size limit')
            data=json.loads(self.rfile.read(size));variables=self.server.variables
            if not isinstance(data,dict) or set(data)!=set(variables):raise ValueError('Supply the three declared integer arguments')
            values=[data[v] for v in variables]
            if any(type(v) is not int or not 0<=v<=10**12 for v in values):raise ValueError('Billing arguments must be nonnegative bounded integers')
            return self.reply(200,{'total':str(evaluate(self.server.polynomial,values)),'receipt_id':self.server.receipt['receipt_id']})
        except (ValueError,TypeError) as error:return self.reply(422,{'error':str(error)})

def service(project,receipt,port=0):
    replay(project,receipt)
    if receipt['status']!='PASS':raise ValueError('A blocked package cannot start a billing service')
    rule=json.loads((Path(project)/'contracts.json').read_text())['functions'][0]
    if rule['function']!='invoice_total' or rule['variables']!=['units','unit_price','shipping']:raise ValueError('This runtime supports the declared invoice contract only')
    server=ThreadingHTTPServer(('127.0.0.1',port),BillingHandler);server.project=Path(project);server.receipt=receipt;server.variables=rule['variables']
    server.polynomial=parse(extract((server.project/rule['file']).read_text(),rule['function'],rule['variables']),rule['variables'])
    return server

def check_staging(project,receipt):
    artifact=verified_package(project,receipt);checks=[]
    with tempfile.TemporaryDirectory(prefix='evidencegate-stage-') as temp:
        staging=Path(temp)
        with zipfile.ZipFile(artifact) as archive:
            allowed={'sampleapp/billing.py','contracts.json','evidence/contract.json'}
            if set(archive.namelist())!=allowed:raise ValueError('Unexpected package contents')
            for name in allowed:
                target=staging/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(name))
        embedded=json.loads((staging/'evidence/contract.json').read_text());replay(staging,embedded)
        server=service(staging,embedded);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with urllib.request.urlopen(url+'/health',timeout=5) as response:checks.append({'check':'package_startup','passed':json.load(response)['status']=='verified'})
            for units,price,shipping in product((1,2,5),(0,17),(0,3,10)):
                payload={'units':units,'unit_price':price,'shipping':shipping}
                request=urllib.request.Request(url+'/invoice',json.dumps(payload).encode(),{'Content-Type':'application/json'})
                with urllib.request.urlopen(request,timeout=5) as response:actual=json.load(response)['total']
                expected=str(units*price+shipping);checks.append({'check':'billing_canary','input':payload,'expected':expected,'actual':actual,'passed':expected==actual})
            original=(staging/'sampleapp/billing.py').read_bytes()
            (staging/'sampleapp/billing.py').write_text('def invoice_total(units, unit_price, shipping):\n    return units * (unit_price + shipping)\n')
            for method in ('health','invoice'):
                request=urllib.request.Request(url+'/'+method,None if method=='health' else b'{"units":2,"unit_price":17,"shipping":3}',{'Content-Type':'application/json'})
                try:urllib.request.urlopen(request,timeout=5);code=200
                except urllib.error.HTTPError as error:code=error.code
                checks.append({'check':'drift_blocks_'+method,'http_status':code,'passed':code==503})
            (staging/'sampleapp/billing.py').write_bytes(original)
            with urllib.request.urlopen(url+'/health',timeout=5) as response:checks.append({'check':'restored_source_replays','passed':json.load(response)['status']=='verified'})
        finally:server.shutdown();server.server_close();thread.join()
    if not all(c['passed'] for c in checks):raise ValueError('Staging acceptance or drift governance failed')
    return {'status':'STAGING_ACCEPTED','receipt_id':receipt['receipt_id'],'package_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),
            'checks':checks,'checks_passed':len(checks),'billing_canaries':sum(c['check']=='billing_canary' for c in checks),
            'performed_lifecycle_work':['verify','package','configure','monitor','govern'],
            'production_release':'Human approval remains required.',
            'scope':'Executed ephemeral local HTTP staging from an actual verified ZIP. Not a cloud deployment or GitLab Duo session.'}
