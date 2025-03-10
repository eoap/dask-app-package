from __future__ import annotations
from typing import List, Tuple, TypeAlias
import numpy as np
import pandas as pd
import stackstac
import pystac_client
import planetary_computer
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.eo import EOExtension
from pystac_client.item_search import ItemSearch
from pystac.item_collection import ItemCollection
import xrspatial.multispectral as ms
from time import sleep
from pystac import Catalog, Item, CatalogType
from rasterio.enums import Resampling

from loguru import logger
from dask_gateway import Gateway
import traceback
import os
import sys
import click
import rioxarray # noqa: F401
import rio_stac

BBox: TypeAlias = tuple[float, float, float, float]
RGBBands: TypeAlias = Tuple[str, str, str]


def create_catalog(items: List[Item]) -> Catalog:
    """
    Create a STAC catalog from a list of STAC items.
    """
    catalog = Catalog(
        id="monthly-mosaics",
        description="Monthly mosaics of Sentinel-2 data",
        title="Monthly Mosaics",
    )

    for item in items:
        catalog.add_item(item)

    return catalog

def create_monthly_stac_item(start_time: str, end_time: str, monthly_mosaic: str) -> Item:
    """
    Create a STAC item for a monthly mosaic.
    """
    item = rio_stac.stac.create_stac_item(
        source=monthly_mosaic,
        input_datetime=start_time,
        id=f"monthly-mosaic-{to_datetime_str(start_time)}-{to_datetime_str(end_time)}",
        asset_roles=["data", "visual"],
        asset_href=os.path.basename(monthly_mosaic),
        asset_name="data",
        with_proj=True,
        with_raster=True,
    )
   
    return item

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

def to_datetime_str(date) -> str:

    return pd.to_datetime(date).strftime("%Y-%m")

def get_item_collection(aoi: BBox, start_date: str, end_date: str, collection: str, max_items: int, max_cloud_cover: int) -> ItemCollection:
    
    items = []

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
    )
    search: ItemSearch = stac.search(
        bbox=[float(c) for c in aoi.split(",")],
        datetime=f"{start_date}/{end_date}",
        collections=[collection],
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
        limit=10,
        max_items=max_items,
    )

    for page in search.pages():
        page_items = (page.items)
        logger.info(f"Fetched page with {len(page_items)} items")

        items.extend([planetary_computer.sign(item) for item in page_items])
        sleep(10)
    
    return ItemCollection(items=items)

def main(start_date:str, end_date:str, aoi: BBox, bands: RGBBands, collection: str, resolution:int, max_items: int, max_cloud_cover: int) -> None:

    logger.info(f"Area of interest: {aoi}")
    logger.info(f"Time of interest: {start_date} to {end_date}")

    items = get_item_collection(aoi=aoi, start_date=start_date, end_date=end_date, collection=collection, max_items=max_items, max_cloud_cover=max_cloud_cover)
  
    logger.info(f"Found {len(items)} items")

    epsg = extract_epsg_from_items(items)
    
    logger.info(f"found epsg code: {epsg}")
    
    logger.info(f"Using bands: {bands}")
    assets = [get_asset_key_from_band(items[0], band) for band in bands]
    
    logger.info(f"bands mapped to asset keys: {' '.join(assets)}")
    

    data = (
        stackstac.stack(
            items,
            assets=assets,
            chunksize=(10, 3, 512, 512),
            resolution=resolution,
            epsg=epsg
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )

    logger.info(f"Using chunk size: {data.chunks} for {data.shape}")
    data = data.persist()

    # Step 1: Create a new coordinate for grouping (YYYY-MM format)
    data = data.assign_coords(year_month=("time", data.time.dt.strftime("%Y-%m").data))

    # Step 2: Group by year-month and compute monthly median
    grouped = data.groupby("year_month")
    monthly = grouped.median().compute()

    # Step 3: Extract time ranges (start and end dates per month)
    time_ranges = {
        year_month: (
            time_values.min(),  # Start date
            time_values.max()   # End date
        )
        for year_month, time_values in {
            year_month: pd.to_datetime(data.time.sel(time=data.year_month == year_month).values)
            for year_month in monthly.year_month.values
        }.items()
    }

    logger.info(time_ranges)


    mosaic_items = []

    for year_month, image in zip(time_ranges.keys(), monthly):
        start_time, end_time = time_ranges[year_month]

        # Convert image to true color
        image = ms.true_color(*image)
        image = image.transpose("band", "y", "x")  # Ensure correct dimension order
        image = image.rio.write_crs(f"EPSG:{epsg}", inplace=True)
        image = image.rio.set_spatial_dims("x", "y", inplace=True)

        logger.info(f"Processing mosaic for {year_month}: {start_time} - {end_time}")

        # Create output directory
        output_dir = f"monthly-mosaic-{year_month}"
        os.makedirs(output_dir, exist_ok=True)

        # Save the raster
        output_file = os.path.join(output_dir, f"monthly-mosaic-{year_month}.tif")
        image.rio.to_raster(
            output_file,
            driver="COG",
            dtype="uint8",
            compress="deflate",
            blocksize=256,
            overview_resampling=Resampling.nearest,
        )

        # Generate STAC Item
        mosaic_items.append(create_monthly_stac_item(start_time, end_time, output_file))
        logger.info(f"Saved monthly mosaic: {output_file}")


    catalog = create_catalog(mosaic_items)
    catalog.normalize_hrefs("catalog.json")
    catalog.save(CatalogType.SELF_CONTAINED)

@click.command()
@click.option("--start-date", "start_date", required=True, help="Start date expressed as YYYY-MM-DD")
@click.option("--end-date", "end_date", required=True, help="End date expressed as YYYY-MM-DD")
@click.option("--aoi", "aoi", required=True, help="Area of interest expressed as a bounding box")
@click.option("--bands", "bands", required=True, multiple=True, help="Command band name")
@click.option("--collection", "collection", required=True, help="Collection ID")
@click.option("--resolution", "resolution", default=100, help="Target resolution in meters")
@click.option("--max-items", "max_items", default=100, help="Maximum number of items to search")
@click.option("--max-cloud-cover", "max_cloud_cover", default=25, help="Maximum cloud cover percentage")
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
