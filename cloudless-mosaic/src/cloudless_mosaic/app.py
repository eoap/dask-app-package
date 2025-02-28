import numpy as np
import xarray as xr

import matplotlib.pyplot as plt

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


def main(**kwargs):
    
    start_date = kwargs["start_date"]
    end_date = kwargs["end_date"]
    area_of_interest = {
        "type": "Polygon",
        "coordinates": [
            [
                [-122.27508544921875, 47.54687159892238],
                [-121.96128845214844, 47.54687159892238],
                [-121.96128845214844, 47.745787772920934],
                [-122.27508544921875, 47.745787772920934],
                [-122.27508544921875, 47.54687159892238],
            ]
        ],
    }
    bbox = rasterio.features.bounds(area_of_interest)

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = stac.search(
        bbox=bbox,
        datetime=f"{start_date}/{end_date}",
        collections=["sentinel-2-l2a"],
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
    images = xr.concat(images, dim="time")

    print(images.head())

    images = images.rio.write_crs("EPSG:4326", inplace=True)
    images = images.rio.set_spatial_dims("x", "y", inplace=True)

    # Save the monthly mosaic as a multi-band GeoTIFF
    output_file = "monthly_mosaic.tif"
    images.rio.to_raster(
        output_file,
        driver="COG",
        dtype="uint8",
        compress="deflate",
        blocksize=256,
        overview_resampling=Resampling.nearest,
    )

    print(f"Saved monthly mosaic as {output_file}")


if __name__ == "__main__":

    a

    # Create argument parser
    parser = argparse.ArgumentParser(description="Compute monthly mosaic")
    parser.add_argument(
        "--start_date", type=str, required=True, help="Start date of the search"
    )
    parser.add_argument(
        "--end_date", type=str, required=True, help="End date of the search"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    print(args)
    parser.print_help()
    if not args.start_date or not args.end_date:
        parser.print_help()
        sys.exit(1)
    # gateway = Gateway()

    # with open("/shared/dask_cluster_name.txt", "r") as f:
    #     cluster_name = f.read().strip()
    # cluster_name = os.environ.get("DASK_CLUSTER")

    # logger.info(f"Connecting to the Dask cluster: {cluster_name}")

    # cluster = gateway.connect(cluster_name=cluster_name)

    try:
        # client = cluster.get_client()
        # logger.info(f"Dask Dashboard: {client.dashboard_link}")
        logger.info("Running the monthly mosaic")
        start_time = time.time()
        main(args.start_date, args.end_date)
        logger.info("Monthly mosaic computation completed successfully!")
    except Exception as e:
        logger.error("Failed to run the script: {}", e)
        logger.error(traceback.format_exc())
    finally:
        sys.exit(0)