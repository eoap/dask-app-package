# Sentinel-2 Monthly Mosaic Generator

This project generates monthly median mosaics from Sentinel-2 imagery using STAC data sources. It is designed to be a robust and scalable solution for creating cloud-less composite imagery for various Earth observation applications.

## Overview

The `cloudless_mosaic` module addresses the challenges of large-scale geospatial processing by combining data handling and distributed computing technologies. It seamlessly integrates:

* `xarray`: For efficient handling of multi-dimensional array data, crucial for geospatial rasters.

* `dask`: To enable parallel and out-of-core computations, allowing processing of datasets larger than available memory.

* `zarr`: For cloud-native, chunked array storage, optimizing data retrieval and write operations.

* `stackstac`: To create Dask-backed Xarray DataArrays directly from STAC items, streamlining the data loading process.

## Key Features & Benefits

* **Automated Monthly Mosaics**: Generates high-quality, cloud-filtered monthly median mosaics from Sentinel-2 data.

* **Scalable Processing**: Leverages Dask for distributed parallel processing, enabling efficient handling of vast Sentinel-2 archives.

* **Cloud-Optimized Outputs**: Produces Cloud-Optimized GeoTIFFs (COGs) for efficient storage, streaming, and analysis in cloud environments.

* **Flexible Data Filtering**: Supports filtering by time range, area of interest (AOI), specific bands, and maximum cloud cover, allowing tailored mosaic generation.

* **CWL Workflow Integration**: Includes a Common Workflow Language (CWL) workflow, enabling automated, reproducible, and portable execution within CWL-compatible runners like Calrissian.

## Getting Started

To begin using the `cloudless_mosaic` module, please refer to the [Execution Guide](execute.md) for detailed instructions on setting up the distributed cluster environment, running the module via its command-line interface or orchestrating it through CWL workflows.