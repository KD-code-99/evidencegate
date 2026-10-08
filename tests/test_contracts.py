import copy
import json
from pathlib import Path
import tempfile
import unittest
from evidencegate.polynomial import compare, extract, Unsupported
from evidencegate.audit import audit, replay
from sampleapp.billing import invoice_total

class OrdinaryApplicationTests(unittest.TestCase):
    def test_zero_shipping_examples(self):
        for units,price in ((1,20),(2,15),(5,10)):
            self.assertEqual(invoice_total(units,price,0),units*price)

class IndependentContractTests(unittest.TestCase):
    def test_equivalence_is_symbolic_and_not_a_sample_claim(self):
        r=compare('(x+y)**3','x**3+3*x*x*y+3*x*y*y+y**3',['x','y'])
        self.assertEqual(r['status'],'PROVED_EQUIVALENT');self.assertEqual(r['residual_coefficients'],[])
    def test_wrong_refactor_has_independent_witness(self):
        r=compare('units*unit_price+shipping','units*(unit_price+shipping)',['units','unit_price','shipping'])
        self.assertEqual(r['status'],'REFUTED')
        p=r['counterexample']
        self.assertNotEqual(p['units']*p['unit_price']+p['shipping'],p['units']*(p['unit_price']+p['shipping']))
    def test_rejects_float_semantics_calls_and_conditionals(self):
        for expr in ('x/2','0.5*x','abs(x)','x if x>0 else -x','x//2','True*x'):
            with self.subTest(expr=expr),self.assertRaises((Unsupported,SyntaxError)):compare('x',expr,['x'])
    def test_source_extraction_rejects_additional_effects(self):
        with self.assertRaises(Unsupported):extract('def f(x):\n    print(x)\n    return x','f',['x'])
        self.assertEqual(extract('def f(x):\n    return x*x','f',['x']),'x * x')
    def test_receipt_replay_binds_the_source(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d);(dst/'sampleapp').mkdir();(dst/'sampleapp/billing.py').write_bytes((root/'sampleapp/billing.py').read_bytes());(dst/'contracts.json').write_bytes((root/'contracts.json').read_bytes())
            r=audit(dst);self.assertEqual(replay(dst,r)['status'],'REPLAY_PASSED')
            (dst/'sampleapp/billing.py').write_text('def invoice_total(units, unit_price, shipping):\n    return units*(unit_price+shipping)\n')
            with self.assertRaises(ValueError):replay(dst,r)
            self.assertEqual(audit(dst)['status'],'BLOCKED')
    def test_modified_receipt_cannot_unlock_release(self):
        root=Path(__file__).resolve().parents[1];r=audit(root);bad=copy.deepcopy(r);bad['results'][0]['actual']='0'
        with self.assertRaises(ValueError):replay(root,bad)

if __name__=='__main__':unittest.main()
