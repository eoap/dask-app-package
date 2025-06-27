# Command-Line Interface (CLI)

This module provides a command-line interface for executing the Sentinel-2 processing workflow. Built using the `click` library, the CLI allows users to easily trigger the processing from their terminal, making it suitable for scripting and integration into automated workflows.

## Installation

To enable the command-line entry point and install the necessary dependencies, navigate to the module's root directory and run the following commands:
```bash
cd eopf-sentinel-2/
pip install -e .
```

The `pip install -e .` command installs the package in "editable" mode, meaning any changes to the source code will be immediately reflected without needing to reinstall.

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
  --help           Show this message and exit.
```
## Running the Processing Command


To run the processing, use the `eopf-sentinel-2-proc` command followed by the `--item-url` option and the URL of your desired Sentinel-2 STAC item:
```bash
eopf-sentinel-2-proc --item-url "https://stac.core.eopf.eodc.eu/collections/sentinel-2-l1c/items/S2B_MSIL1C_20250113T103309_N0511_R108_T32TLQ_20250113T122458"
```

Explanation of the item-url parameter:

* `--item-url TEXT`: This is a required option. It expects a `TEXT` value which must be a valid URL pointing to a Sentinel-2 STAC Item. This STAC Item provides all the necessary metadata and asset links (expected in Zarr format) for the module to locate and process the Sentinel-2 data.