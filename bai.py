import argparse
import stackstac
import xarray as xr
import pystac
from rasterio.enums import Resampling
import rioxarray
from loguru import logger
from dask_gateway import Gateway
import traceback
import os
import sys
from time import sleep

def main(pre_fire_url, post_fire_url):

    logger.info(f"pre event {pre_fire_url}")
    logger.info(f"post event {post_fire_url}")
    # Convert the STAC items to xarray DataArray using stackstac with chunks
    pre_fire_stack = stackstac.stack(
        [
            pystac.read_file(
                pre_fire_url
            )
        ],
        assets=["B08", "B12"],  # NIR and SWIR bands
        resolution=10,
        resampling=Resampling.nearest,
        chunksize=(1, 1, 1024, 1024),
    )

    post_fire_stack = stackstac.stack(
        [
            pystac.read_file(
                post_fire_url
            )
        ],
        assets=["B08", "B12"],  # NIR and SWIR bands
        resolution=10,
        resampling=Resampling.nearest,
        chunksize=(1, 1, 1024, 1024),
    )

    pre_fire_stack = pre_fire_stack.assign_coords(band=["B08", "B12"])
    post_fire_stack = post_fire_stack.assign_coords(band=["B08", "B12"])

    # Ensure that the stacks have the same spatial dimensions
    pre_fire_stack = pre_fire_stack.sel(x=post_fire_stack.x, y=post_fire_stack.y)

    # Convert to xarray Datasets and chunk them
    pre_fire_ds = pre_fire_stack.to_dataset(dim="band").chunk(
        {"band": 1, "y": 1024, "x": 1024}
    )
    post_fire_ds = post_fire_stack.to_dataset(dim="band").chunk(
        {"band": 1, "y": 2048, "x": 2048}
    )

    # Compute the Normalized Burn Ratio (NBR)
    def compute_nbr(nir, swir):
        return (nir - swir) / (nir + swir)

    # Compute NBR for pre and post fire
    pre_fire_nbr = compute_nbr(pre_fire_ds["B08"], pre_fire_ds["B12"]).squeeze(
        "time", drop=True
    )
    post_fire_nbr = compute_nbr(post_fire_ds["B08"], post_fire_ds["B12"]).squeeze(
        "time", drop=True
    )

    # Compute the difference to get the burnt area intensity
    burnt_area_intensity = pre_fire_nbr - post_fire_nbr

    # Check the shape and dimensions before saving
    logger.info(f"Burnt area intensity shape: {burnt_area_intensity.shape}")
    logger.info(f"Burnt area intensity dims: {burnt_area_intensity.dims}")

    # Compute and save the result using Dask
    burnt_area_intensity = burnt_area_intensity.astype("float32")
    
    burnt_area_intensity = burnt_area_intensity.rio.write_crs(
        pre_fire_ds.rio.crs, inplace=True
    )
    burnt_area_intensity = burnt_area_intensity.rio.set_spatial_dims(
        "x", "y", inplace=True
    )
    # Save to a raster file
    logger.info("Writing the result to a COG file")
    burnt_area_intensity.rio.to_raster(
        "bai.tif",
        driver="COG",
        dtype="float32",
        compress="deflate",
        blocksize=256,
        overview_resampling=Resampling.nearest,
    )

if __name__ == "__main__":

    # Create argument parser
    parser = argparse.ArgumentParser(description="Compute Burnt Area Intensity")
    parser.add_argument(
        "--pre_fire_url", type=str, required=True, help="Pre-fire STAC item URL"
    )
    parser.add_argument(
        "--post_fire_url", type=str, required=True, help="Post-fire STAC item URL"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    gateway = Gateway()

    # with open("/shared/dask_cluster_name.txt", "r") as f:
    #     cluster_name = f.read().strip()
    cluster_name = os.environ.get("DASK_CLUSTER")

    logger.info(f"Connecting to the Dask cluster: {cluster_name}")

    cluster = gateway.connect(cluster_name=cluster_name)

    try:
        client = cluster.get_client()
        logger.info(f"Dask Dashboard: {client.dashboard_link}")
        logger.info("Running the burned area intensity")
        main(args.pre_fire_url, args.post_fire_url)
        logger.info("Burned area intensity computation completed successfully!")
    except Exception as e:
        logger.error("Failed to run the script: {}", e)
        logger.error(traceback.format_exc())
    finally:
        sys.exit(0)
