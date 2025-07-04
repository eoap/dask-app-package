from __future__ import annotations
import os
import sys
import click
import traceback
from shutil import move
import dask
import pystac
import xarray as xr
import numpy as np
from loguru import logger
from dask_gateway import Gateway
from rio_color.operations import parse_operations
import rasterio
from rasterio.enums import Resampling


def apply_rio_color(channel, c_red, c_green, c_blue, ops):
    arr = np.stack([
        np.clip(np.nan_to_num(c_red, nan=0), 0, 1),
        np.clip(np.nan_to_num(c_green, nan=0), 0, 1),
        np.clip(np.nan_to_num(c_blue, nan=0), 0, 1)
    ], axis=0)
    for func in parse_operations(ops):
        arr = func(arr)
    return (arr[channel, :, :] * 255).astype(np.uint8)


def make_channel_func(channel):
    def func(c_red, c_green, c_blue, ops):
        return apply_rio_color(channel, c_red, c_green, c_blue, ops)
    return func


apply_rio_color_red = make_channel_func(0)
apply_rio_color_green = make_channel_func(1)
apply_rio_color_blue = make_channel_func(2)


def normalized_difference(band1, band2):
    return (band1 - band2) / (band1 + band2)


def compute_index(band1, band2, epsg) -> xr.DataArray:
    index = xr.apply_ufunc(
        normalized_difference,
        band1,
        band2,
        output_dtypes=[np.float32],
        dask="parallelized",
    )
    return index.rio.write_crs(epsg, inplace=True)


def apply_color_correction(bands: tuple[xr.DataArray, xr.DataArray, xr.DataArray], ops: str, epsg: int) -> xr.DataArray:
    red, green, blue = bands
    corrected = [
        xr.apply_ufunc(f, red, green, blue, kwargs={"ops": ops}, dask="parallelized", output_dtypes=[np.uint8])
        for f in (apply_rio_color_red, apply_rio_color_green, apply_rio_color_blue)
    ]
    rgb = xr.concat(corrected, dim='band')
    rgb.rio.write_crs(epsg, inplace=True)
    rgb.rio.set_spatial_dims('x', 'y', inplace=True)
    return rgb


def build_overviews(path: str, levels: list[int] = [2, 4, 8, 16]):
    with rasterio.open(path, "r+") as dst:
        dst.build_overviews(levels, Resampling.average)
        dst.update_tags(ns='rio_overview', resampling='average')


def main(item_url: str) -> None:
    logger.info("Processing started...")
    item = pystac.read_file(item_url)
    logger.info(f"Processing item {item.id}")

    remote_product_path = item.assets["product"].href
    dt = xr.open_datatree(remote_product_path, engine="zarr", chunks={}, decode_timedelta=True)

    epsg = dt.attrs["stac_discovery"]["properties"]["proj:epsg"]

    # Bands
    red = dt["measurements/reflectance/r10m"]["b04"].chunk({"x": 512, "y": 512}).persist()
    green = dt["measurements/reflectance/r10m"]["b03"].chunk({"x": 512, "y": 512}).persist()
    blue = dt["measurements/reflectance/r10m"]["b02"].chunk({"x": 512, "y": 512})
    nir = dt["measurements/reflectance/r10m"]["b08"].chunk({"x": 512, "y": 512}).persist()
    # swir16 = dt["measurements/reflectance/r20m"]["b11"].chunk({"x": 512, "y": 512})
    # swir22 = dt["measurements/reflectance/r20m"]["b12"].chunk({"x": 512, "y": 512})
    # swir16_resampled = swir16.interp(x=red["x"], y=red["y"], method="nearest").chunk({"x": 512, "y": 512}).persist()
    # swir22_resampled = swir22.interp(x=red["x"], y=red["y"], method="nearest").chunk({"x": 512, "y": 512}).persist()


    # Vegetation indexes
    logger.info("Define vegetation indexes")
    ndvi = compute_index(nir, red, epsg)
    ndwi = compute_index(green, nir, epsg)
    # ndmir = compute_index(swir16_resampled, swir22_resampled, epsg)
    # nbdr = compute_index(nir, swir22_resampled, epsg)
    # ndwi2 = compute_index(nir, swir16_resampled, epsg)
    # mndwi = compute_index(green, swir16_resampled, epsg)
    # ndbi = compute_index(swir16_resampled, nir, epsg)

    # Color correction
    ops = "gamma b 1.85, gamma rg 1.95"
    logger.info("Define composites")
    rgb = apply_color_correction((red, green, blue), ops, epsg)
    # vea = apply_color_correction((swir16_resampled, swir22_resampled, red), ops, epsg)
    civ = apply_color_correction((nir, red, green), ops, epsg)
    # law = apply_color_correction((nir, swir16_resampled, red), ops, epsg)
    # sir = apply_color_correction((swir22_resampled, nir, red), ops, epsg)
    # fcu = apply_color_correction((swir22_resampled, swir16_resampled, red), ops, epsg)
    # atp = apply_color_correction((swir22_resampled, swir16_resampled, nir), ops, epsg)

    # Write GeoTIFFs
    logger.info("Compute GeoTIFFs")
    ndvi_tif = "ndvi.tif"
    ndwi_tif = "ndwi.tif"
    ndmir_tif = "ndmir.tif"
    nbdr_tif = "nbdr.tif"
    ndwi2_tif = "ndwi2.tif"
    mndwi_tif = "mndwi.tif"
    ndbi_tif = "ndbi.tif"
    rgb_tif = "overview-rgb.tif"
    vea_tif = "overview-vea.tif"
    civ_tif = "overview-civ.tif"
    law_tif = "overview-law.tif"
    sir_tif = "overview-sir.tif"
    fcu_tif = "overview-fcu.tif"
    atp_tif = "overview-atp.tif"

    tasks = [
        ndvi.compute().astype("float32").rio.to_raster(ndvi_tif, driver="GTiff", compress="LZW"),
        ndwi.compute().astype("float32").rio.to_raster(ndwi_tif, driver="GTiff", compress="LZW"),
        # ndmir.compute().astype("float32").rio.to_raster(ndmir_tif, driver="GTiff", compress="LZW"),
        # nbdr.compute().astype("float32").rio.to_raster(nbdr_tif, driver="GTiff", compress="LZW"),
        # ndwi2.compute().astype("float32").rio.to_raster(ndwi2_tif, driver="GTiff", compress="LZW"),
        # mndwi.compute().astype("float32").rio.to_raster(mndwi_tif, driver="GTiff", compress="LZW"),
        # ndbi.compute().astype("float32").rio.to_raster(ndbi_tif, driver="GTiff", compress="LZW"),
        rgb.compute().rio.to_raster(rgb_tif, driver="GTiff", compress="LZW"),
        # vea.compute().rio.to_raster(vea_tif, driver="GTiff", compress="LZW"),
        civ.compute().rio.to_raster(civ_tif, driver="GTiff", compress="LZW"),
        # law.compute().rio.to_raster(law_tif, driver="GTiff", compress="LZW"),
        # sir.compute().rio.to_raster(sir_tif, driver="GTiff", compress="LZW"),
        # fcu.compute().rio.to_raster(fcu_tif, driver="GTiff", compress="LZW"),
        # atp.compute().rio.to_raster(atp_tif, driver="GTiff", compress="LZW"),
    ]


    dask.compute(*tasks)

    # STAC output
    logger.info("Create STAC Item")
    out_item = pystac.Item(
        id=item.id + "-processed",
        bbox=item.bbox,
        geometry=item.geometry,
        datetime=item.datetime,
        properties=item.properties,
    )

    asset_map = {
        "overview-rgb": (rgb_tif, ["visual"]),
        # "overview-vea": (vea_tif, ["visual"]),
        "overview-civ": (civ_tif, ["visual"]),
        # "overview-law": (law_tif, ["visual"]),
        # "overview-sir": (sir_tif, ["visual"]),
        # "overview-fcu": (fcu_tif, ["visual"]),
        # "overview-atp": (atp_tif, ["visual"]),
        "ndvi": (ndvi_tif, ["data"]),
        "ndwi": (ndwi_tif, ["data"]),
        # "ndmir": (ndmir_tif, ["data"]),
        # "nbdr": (nbdr_tif, ["data"]),
        # "ndwi2": (ndwi2_tif, ["data"]),
        # "mndwi": (mndwi_tif, ["data"]),
        # "ndbi": (ndbi_tif, ["data"]),
    }

    for asset_id, (path, roles) in asset_map.items():
        out_item.add_asset(
            asset_id,
            pystac.Asset(href=path, media_type=pystac.MediaType.GEOTIFF, roles=roles),
        )

    catalog = pystac.Catalog(
        id="processing-results",
        description="Sentinel-2 RGB composites and vegetation indexes",
        title="Sentinel-2 RGB composites and vegetation indexes",
    )

    catalog.add_item(out_item)
    catalog.normalize_hrefs("catalog.json")
    catalog.save(pystac.CatalogType.SELF_CONTAINED)

    # Build overviews and move outputs
    logger.info("Add overviews")
    os.makedirs(out_item.id, exist_ok=True)
    for asset_id, _ in asset_map.items():
        build_overviews(f"{asset_id}.tif")
        move(f"{asset_id}.tif", os.path.join(out_item.id, f"{asset_id}.tif"))


@click.command()
@click.option("--item-url", "item_url", required=True, help="STAC Item URL")
def start(item_url):
    gateway = Gateway()
    cluster_name = os.environ.get("DASK_CLUSTER")
    logger.info(f"Connecting to the Dask cluster: {cluster_name}")
    cluster = gateway.connect(cluster_name=cluster_name)

    try:
        client = cluster.get_client()
        logger.info(f"Dask Dashboard: {client.dashboard_link}")
        main(item_url)
        logger.info("Computation completed successfully!")
    except Exception as e:
        logger.error("Failed to run the script: {}", e)
        logger.error(traceback.format_exc())
    finally:
        sys.exit(0)
