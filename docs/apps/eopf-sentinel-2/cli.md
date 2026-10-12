# Command-Line Interface (CLI)

This module provides a command-line interface for executing the Sentinel-2 processing workflow. Built using the `click` library, the CLI allows users to easily trigger the processing from their terminal, making it suitable for scripting and integration into automated workflows.

## Installation

The PDE editor installs both course applications at startup. For a separate
Python 3.12 environment, run these commands from the repository root:

```bash
uv venv --python 3.12
uv pip sync --require-hashes requirements-notebooks.txt requirements-build.txt
uv pip install --no-deps --no-build-isolation -e cloudless-mosaic -e eopf-sentinel-2
```

Editable installation reflects source changes locally; rebuild workers from the
same source when changing processing code.

## Environment Variables

Before running the CLI, ensure that the `DASK_CLUSTER` environment variable is set to contain an existing gateway cluster name (not the gateway URL). This is crucial for the application to connect to the distributed processing environment.

## Basic Usage and Help

To view the available commands, options, and a comprehensive help message for the eopf-sentinel-2-proc command, execute:
```bash

eopf-sentinel-2-proc --help
```
This will output the following information:
```bash
Usage: eopf-sentinel-2-proc [OPTIONS]

Options:
  --item-url TEXT  STAC Item URL  [required]
  --window-size INTEGER RANGE  Optional centred processing window in pixels.
  --help           Show this message and exit.
```
## Running the Processing Command


To run the processing, use the `eopf-sentinel-2-proc` command followed by the `--item-url` option and the URL of your desired Sentinel-2 STAC item:
```bash
eopf-sentinel-2-proc --item-url "https://stac.core.eopf.eodc.eu/collections/sentinel-2-l1c/items/S2B_MSIL1C_20250113T103309_N0511_R108_T32TLQ_20250113T122458"
```

Explanation of the item-url parameter:

* `--item-url TEXT`: This is a required option. It expects a `TEXT` value which must be a valid URL pointing to a Sentinel-2 STAC Item. This STAC Item provides all the necessary metadata and asset links (expected in Zarr format) for the module to locate and process the Sentinel-2 data.

Use `--window-size 1024` for bounded acceptance on the original real acquisition.
Omit this option to process the full tile. The result records the window and
derives its STAC footprint from the output raster; full-tile capacity has not
been accepted.
