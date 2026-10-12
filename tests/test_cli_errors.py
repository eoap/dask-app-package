"""Regression checks for failed scientific Dask jobs returning success."""

import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from cloudless_mosaic import app as cloudless
from eopf_sentinel_2 import app as eopf


class FailedProcessing(unittest.TestCase):
    def test_eopf_failure_returns_nonzero(self):
        with (
            patch.object(eopf, "Gateway", return_value=MagicMock()),
            patch.object(eopf, "main", side_effect=RuntimeError("processing failed")),
        ):
            result = CliRunner().invoke(
                eopf.start, ["--item-url", "https://example.test/item.json"]
            )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("processing failed", result.output)

    def test_cloudless_failure_returns_nonzero(self):
        with (
            patch.object(cloudless, "Gateway", return_value=MagicMock()),
            patch.object(cloudless, "main", side_effect=RuntimeError("processing failed")),
        ):
            result = CliRunner().invoke(
                cloudless.start,
                [
                    "--start-date",
                    "2020-10-01",
                    "--end-date",
                    "2020-12-31",
                    "--aoi",
                    "0,0,1,1",
                    "--bands",
                    "red",
                    "--bands",
                    "green",
                    "--bands",
                    "blue",
                    "--collection",
                    "sentinel-2-l2a",
                ],
            )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("processing failed", result.output)


class ProjectionMetadata(unittest.TestCase):
    def test_current_projection_code(self):
        self.assertEqual(eopf.projection_epsg({"proj:code": "EPSG:32632"}), 32632)

    def test_legacy_projection_epsg(self):
        self.assertEqual(eopf.projection_epsg({"proj:epsg": 32632}), 32632)

    def test_missing_projection_is_an_error(self):
        with self.assertRaises(ValueError):
            eopf.projection_epsg({})


if __name__ == "__main__":
    unittest.main()


class StacBandLookup(unittest.TestCase):
    def test_asset_common_name_is_read_from_asset_extension(self) -> None:
        from datetime import UTC, datetime

        from pystac import Asset, Item
        from pystac.extensions.eo import Band, EOExtension

        item = Item("lookup", None, None, datetime(2026, 1, 1, tzinfo=UTC), {})
        asset = Asset("https://example.invalid/red.tif", roles=["data"])
        item.add_asset("B04", asset)
        EOExtension.ext(asset, add_if_missing=True).bands = [
            Band.create(name="B04", common_name="red")
        ]
        self.assertEqual(cloudless.get_asset_key_from_band(item, "red"), "B04")
        self.assertIsNone(cloudless.get_asset_key_from_band(item, "nir"))

    def test_rgb_validation_rejects_a_single_band(self) -> None:
        with patch.object(cloudless, "Gateway", return_value=MagicMock()):
            result = CliRunner().invoke(
                cloudless.start,
                [
                    "--start-date",
                    "2020-10-01",
                    "--end-date",
                    "2020-12-31",
                    "--aoi",
                    "0,0,1,1",
                    "--bands",
                    "red",
                    "--collection",
                    "sentinel-2-l2a",
                ],
            )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Exactly three bands", result.output)
