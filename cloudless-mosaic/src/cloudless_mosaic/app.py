from __future__ import annotations
from typing import Dict, Any, List, Tuple, TypeAlias
import numpy as np
import xarray as xr


import rasterio.features
from rasterio.enums import Resampling
import stackstac
import pystac_client
import planetary_computer

import xrspatial.multispectral as ms
import argparse
from rasterio.enums import Resampling
from loguru import logger
from dask_gateway import Gateway
import traceback
import os
import sys
import time
import click
from loguru import logger

BBox: TypeAlias = tuple[float, float, float]
RGBBands: TypeAlias = Tuple[str, str, str]

def main(start_date:str, end_date:str, aoi: BBox, bands: RGBBands, collection: str) -> None:

    
    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = stac.search(
        bbox=aoi,
        datetime=f"{start_date}/{end_date}",
        collections=[collection],
        query={"eo:cloud_cover": {"lt": 25}},
    )

    items = search.item_collection()
    print(len(items))

    # Reason for pystac version 1.11.0
    # https://github.com/gjoseph92/stackstac/issues/262
    # Solution (Not merged yet)
    # https://github.com/gjoseph92/stackstac/pull/264 

    data = (
        stackstac.stack(
            items,
            assets=["B04", "B03", "B02"],  # red, green, blue
            chunksize=4096,
            resolution=100,
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )

    data = data.persist()


    monthly = data.groupby("time.month").median().compute()

    images = [ms.true_color(*x) for x in monthly]
    #images = xr.concat(images, dim="time")

    print(images.head())

    for index, image in enumerate(images):
        image = image.rio.write_crs("EPSG:4326", inplace=True)
        image = image.rio.set_spatial_dims("x", "y", inplace=True)

        # Save the monthly mosaic as a multi-band GeoTIFF
        output_file = f"monthly_mosaic-{monthly[index]}.tif"
        image.rio.to_raster(
            output_file,
            driver="COG",
            dtype="uint8",
            compress="deflate",
            blocksize=256,
            overview_resampling=Resampling.nearest,
        )

        print(f"Saved monthly mosaic as {output_file}")


@click.command()
@click.option("--start-date", "start_date", required=True, help="")
@click.option("--end-date", "end_date", required=True, help="")
@click.option("--aoi", "aoi", required=True, help="")
@click.option("--bands", "bands", required=True, multiple=True, help="")
def start(**kwargs):

    gateway = Gateway()

    cluster_name = os.environ.get("DASK_CLUSTER")

    logger.info(f"Connecting to the Dask cluster: {cluster_name}")

    cluster = gateway.connect(cluster_name=cluster_name)

    try:
        client = cluster.get_client()
        logger.info(f"Dask Dashboard: {client.dashboard_link}")
        logger.info("Running the app")
        main(**kwargs)
        logger.info("Computation completed successfully!")
    except Exception as e:
        logger.error("Failed to run the script: {}", e)
        logger.error(traceback.format_exc())
    finally:
        sys.exit(0)

# if __name__ == "__main__":
#     start()