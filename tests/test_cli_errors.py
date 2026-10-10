"""Regression checks for failed scientific Dask jobs returning success."""
import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cloudless_mosaic import app as cloudless
from eopf_sentinel_2 import app as eopf

class FailedProcessing(unittest.TestCase):
    def test_eopf_failure_returns_nonzero(self):
        with patch.object(eopf, 'Gateway', return_value=MagicMock()), patch.object(eopf, 'main', side_effect=RuntimeError('processing failed')):
            result = CliRunner().invoke(eopf.start, ['--item-url', 'https://example.test/item.json'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('processing failed', result.output)

    def test_cloudless_failure_returns_nonzero(self):
        with patch.object(cloudless, 'Gateway', return_value=MagicMock()), patch.object(cloudless, 'main', side_effect=RuntimeError('processing failed')):
            result = CliRunner().invoke(cloudless.start, ['--start-date','2020-10-01','--end-date','2020-12-31','--aoi','0,0,1,1','--bands','red','--collection','sentinel-2-l2a'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('processing failed', result.output)

class ProjectionMetadata(unittest.TestCase):
    def test_current_projection_code(self):
        self.assertEqual(eopf.projection_epsg({"proj:code": "EPSG:32632"}), 32632)

    def test_legacy_projection_epsg(self):
        self.assertEqual(eopf.projection_epsg({"proj:epsg": 32632}), 32632)

    def test_missing_projection_is_an_error(self):
        with self.assertRaises(ValueError):
            eopf.projection_epsg({})

if __name__ == '__main__':
    unittest.main()
