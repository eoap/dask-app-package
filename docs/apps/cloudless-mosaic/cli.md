# Command-Line Interface (CLI)

The `cloudless_mosaic` module provides a user-friendly command-line interface (CLI) to configure and run the Sentinel-2 monthly mosaic generation workflow. Built with the `click` library, the CLI simplifies the execution process and supports various parameters for customized outputs.

## Installation

To install the `cloudless_mosaic` application and its command-line entry point, navigate to the module's root directory (cloudless-mosaic/) and run the following commands:
```bash
cd cloudless-mosaic/
pip install -e .
```
The `pip install -e .` command installs the package in "editable" mode, meaning any changes to the source code will be immediately reflected without needing to reinstall.

## Environment Variables

Before running the CLI, ensure that the `DASK_CLUSTER` environment variable is set to point to your Dask cluster's address. This is crucial for the application to connect to the distributed processing environment.

## Basic Usage and Help

To view the available options and a comprehensive help message for the cloudless-mosaic command, execute:
```bash

cloudless-mosaic --help
```

This will output details on how to use the command and all its supported parameters.

## Running the Monthly Mosaic Generation

Use the `cloudless-mosaic` command with the necessary parameters to generate Sentinel-2 monthly median mosaics. Below is an example demonstrating a typical command execution:

```bash
cloudless-mosaic \
    --start-date 2020-10-01 \
    --end-date 2020-12-31 \
    --aoi -122.27508544921875,47.54687159892238,-121.96128845214844,47.745787772920934 \
    --bands nir \
    --bands red \
    --bands green \
    --collection sentinel-2-l2a \
    --resolution 100 \
    --max-items 1000 \
    --max-cloud-cover 25
```

Parameter Descriptions:

* `--start-date YYYY-MM-DD`: The start date for retrieving Sentinel-2 imagery.

* `--end-date YYYY-MM-DD`: The end date for retrieving Sentinel-2 imagery.

* `--aoi MIN_LON,MIN_LAT,MAX_LON,MAX_LAT`: The Area of Interest defined as a bounding box (e.g., -122.27,47.54,-121.96,47.74).

* `--bands TEXT`: Specifies the Sentinel-2 spectral bands to include in the mosaic (e.g., nir, red, green). Repeat the --bands flag for each desired band.

* `--collection TEXT`: The Sentinel-2 collection to query (e.g., sentinel-2-l1c or sentinel-2-l2a).

* `--resolution INTEGER`: The spatial resolution of the output mosaic in meters.

* `--max-items INTEGER`: The maximum number of STAC items (individual Sentinel-2 scenes) to consider for mosaic generation within the specified AOI and time range.

* `--max-cloud-cover INTEGER`: The maximum acceptable cloud cover percentage for Sentinel-2 scenes to be included in the mosaic. Scenes exceeding this threshold will be filtered out.