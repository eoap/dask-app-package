from __future__ import annotations
from typing import List, Tuple, TypeAlias
import numpy as np
import pandas as pd
import stackstac
import pystac_client
import planetary_computer
from pystac.extensions.projection import ProjectionExtension

import xrspatial.multispectral as ms

from pystac import Item
from rasterio.enums import Resampling

from loguru import logger
from dask_gateway import Gateway
import traceback
import os
import sys
import click
import rioxarray # noqa: F401

BBox: TypeAlias = tuple[float, float, float]
RGBBands: TypeAlias = Tuple[str, str, str]

from pystac.extensions.eo import EOExtension

def get_asset_key_from_band(item: Item, common_band_name: str):
    """
    Extract the correct asset key from STAC items using the EO extension.
    """
    
    eo = EOExtension.ext(item)  # Load EO extension
    for asset_key, asset in eo.get_assets().items():
        for band in asset.ext.eo.bands:
            if band.common_name in [common_band_name]:
                return asset_key
        
    return None  # Return None if no matching asset is found

def determine_optimal_chunk_size(data_shape):
    """
    Determine an optimal chunk size based on dataset dimensions.
    """
    y_size, x_size = data_shape[-2], data_shape[-1]
    chunk_size = max(512, min(4096, min(y_size // 4, x_size // 4)))
    return chunk_size

def extract_epsg_from_items(items: List[Item]):
    """
    Extract EPSG code from STAC items.
    """
    for item in items:
        proj = ProjectionExtension.ext(item)  # Load projection extension
        
        epsg = proj.epsg  # Extract EPSG code
        
        if epsg:
            return epsg
    return 4326  # Default to WGS 84 if no EPSG found

def main(start_date:str, end_date:str, aoi: BBox, bands: RGBBands, collection: str, resolution:int) -> None:

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
    logger.info(f"found {len(items)} items")

    logger.info(f"{items[0].get_self_href()}")
    
    epsg = extract_epsg_from_items(items)
    
    logger.info(f"found epsg code: {epsg}")
    
    assets = [get_asset_key_from_band(items[0], band) for band in bands]
    logger.info(assets)
    sample_data = stackstac.stack(items, assets=assets, resolution=resolution, epsg=epsg)
    optimal_chunk_size = determine_optimal_chunk_size(sample_data.shape)
    logger.info(f"chunk size: {optimal_chunk_size}")

    data = (
        stackstac.stack(
            items,
            assets=assets,
            chunksize=optimal_chunk_size,
            resolution=resolution,
            epsg=epsg
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )

    data = data.persist()
    grouped = data.groupby("time.month")
    monthly = grouped.median().compute()
    #unique_times = [pd.to_datetime(data.time.sel(time=data.time.dt.month == month).values[0]) for month in monthly.month.values]
    unique_times = [pd.to_datetime(data.time.sel(time=data.time.dt.month == month).values) for month in monthly.month.values]

    logger.info(unique_times)
    for time_index, image in zip(unique_times, monthly):
    

    #for time_index, image in zip(monthly.time.values, monthly):
        image = ms.true_color(*image)
        image = image.transpose("band", "y", "x")  # Ensure correct dimension order
        image = image.rio.write_crs(f"EPSG:{epsg}", inplace=True)
        image = image.rio.set_spatial_dims("x", "y", inplace=True)

        start_time = min(time_index).strftime("%Y-%m-%d")
        end_time = max(time_index).strftime("%Y-%m-%d")
        logger.info(f"{start_time} {end_time}")

        #date_str = pd.to_datetime(time_index).strftime("%Y-%m")
        output_file = f"monthly_mosaic_{start_time}-{end_time}.tif"
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
@click.option("--collection", "collection", required=True, help="")
@click.option("--resolution", "resolution", default=100, help="")
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
