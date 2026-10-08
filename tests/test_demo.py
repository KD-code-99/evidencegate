import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from evidencegate.demo import prepare, package
from evidencegate.server import make_server


class DemoTests(unittest.TestCase):
    def test_wrong_change_passes_examples_but_blocks_real_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = prepare(tmp, 'wrong')
            self.assertEqual(result['ordinary_tests']['passed'], 3)
            self.assertEqual(result['receipt']['status'], 'BLOCKED')
            with self.assertRaises(ValueError): package(tmp, 'wrong')
            self.assertFalse((Path(tmp)/'wrong/artifacts/verified-billing.zip').exists())

    def test_equivalent_change_packages_and_changed_source_invalidates_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = prepare(tmp, 'correct')
            self.assertEqual(result['receipt']['status'], 'PASS')
            artifact = package(tmp, 'correct')
            with zipfile.ZipFile(artifact) as archive:
                self.assertEqual(archive.namelist(), ['sampleapp/billing.py', 'contracts.json', 'evidence/contract.json'])
            (Path(tmp)/'correct/sampleapp/billing.py').write_text('def invoice_total(units, unit_price, shipping):\n    return 0\n')
            with self.assertRaises(ValueError): package(tmp, 'correct')

    def test_unknown_program_blocks_instead_of_claiming_correctness(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = prepare(tmp, 'unsupported')
            self.assertEqual(result['receipt']['results'][0]['status'], 'UNSUPPORTED')
            self.assertFalse(result['replay']['release_allowed'])

    def test_http_uses_actual_check_and_rejects_cross_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            server=make_server(0, tmp)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            def request(path,data,origin=None):
                headers={'Content-Type':'application/json'}
                if origin:headers['Origin']=origin
                return urllib.request.urlopen(urllib.request.Request(base+path,json.dumps(data).encode(),headers))
            try:
                with request('/api/check',{'scenario':'wrong'}) as response:
                    self.assertEqual(json.load(response)['receipt']['status'],'BLOCKED')
                with self.assertRaises(urllib.error.HTTPError) as error:request('/api/package',{'scenario':'wrong'})
                self.assertEqual(error.exception.code,422)
                with self.assertRaises(urllib.error.HTTPError) as error:request('/api/check',{'scenario':'original'},'https://untrusted.example')
                self.assertEqual(error.exception.code,403)
            finally:server.shutdown();server.server_close();thread.join()
