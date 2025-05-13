from __future__ import annotations
import os
import sys
import click
import traceback
import pystac
import xarray as xr
import numpy as np
from loguru import logger
from dask_gateway import Gateway
from rio_color.operations import parse_operations

def apply_rio_color(channel, c_red, c_green, c_blue, ops):
    arr = np.stack([np.clip(c_red, 0, 1), 
                    np.clip(c_green, 0, 1), 
                    np.clip(c_blue, 0, 1)], axis=0)
    assert arr.shape[0] == 3
    assert np.nanmin(arr) >= 0, "Input values must be >= 0"
    assert np.nanmax(arr) <= 1, "Input values must be <= 1"
    for func in parse_operations(ops):
        arr = func(arr)
    return (arr[channel, :, :] * 255).astype(np.uint8)

def apply_rio_color_red(c_red, c_green, c_blue, ops):
    return apply_rio_color(0, c_red, c_green, c_blue, ops)

def apply_rio_color_green(c_red, c_green, c_blue, ops):
    return apply_rio_color(1, c_red, c_green, c_blue, ops)

def apply_rio_color_blue(c_red, c_green, c_blue, ops):
    return apply_rio_color(2, c_red, c_green, c_blue, ops)

def normalized_difference(band1, band2):
    return (band1 - band2) / (band1 + band2)

def main(item_url:str) -> None:

    logger.info(f"Processing started...")

    item = pystac.read_file(item_url)

    logger.info(f"Processing item {item.id}")
    
    remote_product_path = item.get_assets().get("product").href 

    dt = xr.open_datatree(remote_product_path, engine="zarr", chunks={})

    red = dt["measurements/reflectance/r10m"]["b04"].chunk({"x": 512, "y": 512})
    green = dt["measurements/reflectance/r10m"]["b03"].chunk({"x": 512, "y": 512})
    blue = dt["measurements/reflectance/r10m"]["b02"].chunk({"x": 512, "y": 512})
    nir = dt["measurements/reflectance/r10m"]["b08"].chunk({"x": 512, "y": 512})
    swir16 = dt["measurements/reflectance/r20m"]["b11"].chunk({"x": 512, "y": 512})

    epsg = f"EPSG:{dt.attrs.get('stac_discovery').get('properties').get('proj:epsg')}"

    swir16_resampled = swir16.interp(x=red["x"], y=red["y"], method="nearest").chunk({"x": 512, "y": 512})

    ndvi = xr.apply_ufunc(
        normalized_difference,
        red,
        nir,
        output_dtypes=[np.float32],
        dask="parallelized",
    )

    ndvi = ndvi.rio.write_crs(epsg, inplace=True)

    ndwi = xr.apply_ufunc(
        normalized_difference,
        green,
        nir,
        output_dtypes=[np.float32],
        dask="parallelized",
    )

    ndwi = ndwi.rio.write_crs(epsg, inplace=True)

    ops = "gamma b 1.85, sigmoidal rgb 35 0.13"# , saturation 1.15"

    # Apply the color correction using Dask and xarray
    color_corrected_red = xr.apply_ufunc(
        apply_rio_color_red,
        red, green, blue,
        kwargs={"ops": ops},
        output_dtypes=[np.uint8],
        dask="parallelized",
    )

    color_corrected_green = xr.apply_ufunc(
        apply_rio_color_green,
        red, green, blue,
        kwargs={"ops": ops},
        output_dtypes=[np.uint8],
        dask="parallelized",
    )

    color_corrected_blue = xr.apply_ufunc(
        apply_rio_color_blue,
        red, green, blue,
        kwargs={"ops": ops},
        output_dtypes=[np.uint8],
        dask="parallelized",
    )

    # Combine the corrected channels into a single array
    rgb = xr.concat([color_corrected_red, color_corrected_green, color_corrected_blue], dim='band')

    # Set attributes for GeoTIFF
    rgb = rgb.rio.write_crs(epsg, inplace=True)
    rgb = rgb.rio.set_spatial_dims('x', 'y', inplace=True)

   

    ops = "gamma b 1.85, gamma rg 1.95"

    color_corrected_red = xr.apply_ufunc(
        apply_rio_color_red,
        swir16_resampled, nir, red,
        kwargs={"ops": ops},
        output_dtypes=[np.uint8],
        dask="parallelized",
    )

    color_corrected_green = xr.apply_ufunc(
        apply_rio_color_green,
        swir16_resampled, nir, red,
        kwargs={"ops": ops},
        output_dtypes=[np.uint8],
        dask="parallelized",
    )

    color_corrected_blue = xr.apply_ufunc(
        apply_rio_color_blue,
        swir16_resampled, nir, red,
        kwargs={"ops": ops},
        output_dtypes=[np.uint8],
        dask="parallelized",
    )

    # Combine the corrected channels into a single array
    vea = xr.concat([color_corrected_red, color_corrected_green, color_corrected_blue], dim='band')

    # Set attributes for GeoTIFF
    vea = vea.rio.write_crs(f"EPSG:{dt.attrs.get('stac_discovery').get('properties').get('proj:epsg')}", inplace=True)
    vea = vea.rio.set_spatial_dims('x', 'y', inplace=True)

    # Trigger the computation and save as GeoTIFF
    logger.info("Compute RGB composite")
    rgb.compute().rio.to_raster('overview-rgb.tif')
    logger.info("Compute NDVI")
    ndvi.compute().rio.to_raster('ndvi.tif')
    logger.info("Compute NDWI")
    ndwi.compute().rio.to_raster('ndwi.tif')
    logger.info("Compute VEA composite")
    vea.compute().rio.to_raster('overview-vea.tif')

    out_item = pystac.Item(
        id=item.id + "-processed",
        bbox=item.bbox,
        geometry=item.geometry,
        datetime=item.datetime,
        properties=item.properties,
    )

    out_item.add_asset(
        "overview_rgb",
        pystac.Asset(
            href="overview-rgb.tif",
            media_type=pystac.MediaType.GEOTIFF,
            roles=["visual"],
        ),
    )
    out_item.add_asset(
        "ndvi",
        pystac.Asset(
            href="ndvi.tif",
            media_type=pystac.MediaType.GEOTIFF,
            roles=["data"],
        ),
    )
    out_item.add_asset(
        "ndwi",
        pystac.Asset(
            href="ndwi.tif",
            media_type=pystac.MediaType.GEOTIFF,
            roles=["data"],
        ),
    )
    out_item.add_asset(
        "overview_vea",
        pystac.Asset(
            href="overview-vea.tif",
            media_type=pystac.MediaType.GEOTIFF,
            roles=["visual"],
        ),
    )

    catalog = pystac.Catalog(
        id="processing-results",
        description="Sentinel-2 RGB mosaics and vegetation indexes",
        title="Sentinel-2 RGB mosaics and vegetation indexes",
    )

    catalog.add_item(out_item)
    catalog.normalize_hrefs("catalog.json")
    catalog.save(pystac.CatalogType.SELF_CONTAINED)

@click.command()
@click.option("--item-url", "item_url", required=True, help="STAC Item URL")
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