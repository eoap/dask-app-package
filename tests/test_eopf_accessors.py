"""Guard the clean-process accessor registration exposed by EO acceptance."""

import subprocess
import sys
import unittest


class EopfAccessorTests(unittest.TestCase):
    def test_index_retains_crs_in_a_fresh_process(self):
        subprocess.run(
            [
                sys.executable,
                "-c",
                """
from eopf_sentinel_2.app import compute_index
import numpy as np
import xarray as xr
coords = {"y": [20.0, 10.0], "x": [10.0, 20.0]}
first = xr.DataArray(np.full((2, 2), 3.0), dims=("y", "x"), coords=coords)
second = xr.DataArray(np.ones((2, 2)), dims=("y", "x"), coords=coords)
index = compute_index(first, second, 32632)
np.testing.assert_allclose(index.values, 0.5)
assert index.rio.crs.to_epsg() == 32632
""",
            ],
            check=True,
        )
