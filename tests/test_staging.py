import tempfile
import unittest
from pathlib import Path
from evidencegate.demo import prepare
from evidencegate.staging import check_staging

class StagingTests(unittest.TestCase):
    def test_actual_zip_http_canaries_and_drift_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            result=prepare(temp,'correct');report=check_staging(Path(temp)/'correct',result['receipt'])
            self.assertEqual(report['status'],'STAGING_ACCEPTED');self.assertEqual(report['billing_canaries'],18)
            self.assertEqual(report['checks_passed'],22);self.assertTrue(all(c['passed'] for c in report['checks']))
            self.assertIn('govern',report['performed_lifecycle_work'])
    def test_wrong_source_never_starts_staging(self):
        with tempfile.TemporaryDirectory() as temp:
            result=prepare(temp,'wrong')
            with self.assertRaises(ValueError):check_staging(Path(temp)/'wrong',result['receipt'])
