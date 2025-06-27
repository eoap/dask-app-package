# Sentinel-2 Data Processing Module

This documentation provides an overview of a Python module for processing Sentinel-2 imagery, optimized for efficient execution on distributed infrastructure via Dask Gateway.

## Overview

This module is designed to tackle the computational demands of large-scale geospatial data analysis. It achieves scalability and out-of-core processing by synergistically integrating:

* `Xarray`: For labeled multi-dimensional array manipulation.

* `Dask`: Enabling parallel and distributed computation.

* `Zarr`: Providing cloud-native, chunked array storage for efficient I/O.

The module supports STAC _(SpatioTemporal Asset Catalog)_ compliant datasets through pystac facilitating access to Sentinel-2 data. 

The core processing pipeline includes robust functionality for:

* Vegetation and Water Index Computation: Generating essential indices like NDVI, NDWI, and NBR for environmental monitoring.

* Color-Balanced Composite Imagery: Producing various composite images (e.g., RGB, CIR, SWIR) for enhanced visualization and analysis.

## Key Features & Benefits

* **Distributed Processing**: Leverages Dask Gateway for scalable execution on Kubernetes clusters, allowing for processing of large Sentinel-2 datasets that exceed single-machine memory limits.

* **CWL Workflow Integration**: Includes a Common Workflow Language (CWL) workflow, optimized for distributed execution with a custom `DaskGatewayRequirements` extension, enabling orchestration via Calrissian.

* **Cloud-Native Data Handling**: Utilizes the Zarr format for efficient, chunked data storage, ideal for cloud environments and parallel access.

* **STAC Compliance**: Seamlessly integrates with STAC catalogs for data discovery and access.

* **Comprehensive Outputs**: Generates a suite of valuable vegetation and water indices, along with various color-corrected composite images and a new STAC item referencing the generated products.

## Getting Started

Refer to the [Execution Guide](execute.md) for detailed instructions on setting up the distributed cluster, running the module directly or via Calrissian CWL workflows, and understanding input/output data specifications.