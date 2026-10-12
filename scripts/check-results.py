"""Check real GeoTIFF assets, scientific values, and catalog geometry."""

import argparse
from pathlib import Path

import numpy as np
import pystac
import rasterio
from rasterio.warp import transform_bounds

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--catalog", type=Path, action="append")
args = parser.parse_args()
for source in args.catalog or [
    root / "cloudless-mosaic/catalog.json",
    root / "eopf-sentinel-2/catalog.json",
]:
    catalog = pystac.Catalog.from_file(str(source))
    items = list(catalog.get_all_items())
    assert items, source
    for item in items:
        assert item.bbox and item.assets
        for name, asset in item.assets.items():
            with rasterio.open(asset.get_absolute_href()) as src:
                assert src.crs and src.width > 0 and src.height > 0
                bbox = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
                assert np.allclose(bbox, item.bbox, atol=0.002), (bbox, item.bbox)
                sample = src.read(
                    1, out_shape=(min(128, src.height), min(128, src.width)), masked=True
                ).compressed()
                assert sample.size and np.isfinite(sample).any(), name
                if name in ["ndvi", "ndwi"]:
                    finite = sample[np.isfinite(sample)]
                    assert finite.min() >= -1.001 and finite.max() <= 1.001, name
            print(f"Accepted real georeferenced asset: {asset.get_absolute_href()}")
