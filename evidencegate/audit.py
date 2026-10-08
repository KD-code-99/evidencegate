from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .polynomial import compare, extract, Unsupported


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def audit(root, contract_path='contracts.json'):
    root=Path(root).resolve();contract_file=(root/contract_path).resolve()
    if not contract_file.is_relative_to(root):raise ValueError('Contract path is outside the project')
    contract=json.loads(contract_file.read_text());rows=[]
    if contract.get('domain')!='integers' or not isinstance(contract.get('functions'),list):raise ValueError('Declare integer-domain functions')
    for rule in contract['functions']:
        path=(root/rule['file']).resolve()
        if not path.is_relative_to(root):raise ValueError('Source path is outside the project')
        raw=path.read_bytes();source=raw.decode('utf-8')
        row={'file':rule['file'],'function':rule['function'],'source_sha256':hashlib.sha256(raw).hexdigest()}
        try:row.update(compare(rule['expected'],extract(source,rule['function'],rule['variables']),rule['variables']))
        except (Unsupported,SyntaxError) as error:row.update({'status':'UNSUPPORTED','reason':str(error)})
        rows.append(row)
    checker_dir=Path(__file__).resolve().parent
    body={'schema_version':1,'checker_sha256':{name:hashlib.sha256((checker_dir/name).read_bytes()).hexdigest() for name in ('polynomial.py','audit.py')},'contract_sha256':hashlib.sha256(contract_file.read_bytes()).hexdigest(),'status':'PASS' if rows and all(r['status']=='PROVED_EQUIVALENT' for r in rows) else 'BLOCKED',
          'results':rows,'scope':'Exact equivalence for declared integer polynomial return expressions; no claim about general Python programs.'}
    return {**body,'receipt_id':hashlib.sha256(canonical(body)).hexdigest()}


def replay(root,receipt):
    body={k:v for k,v in receipt.items() if k!='receipt_id'}
    if hashlib.sha256(canonical(body)).hexdigest()!=receipt['receipt_id']:raise ValueError('Evidence receipt was altered')
    actual=audit(root)
    if actual!=receipt:raise ValueError('The current source or contract no longer matches the checked evidence')
    return {'status':'REPLAY_PASSED','receipt_id':receipt['receipt_id'],'release_allowed':receipt['status']=='PASS'}
