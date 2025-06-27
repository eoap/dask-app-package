# Earth Observation Application Package with Dask (EOAP-Dask)

This repository hosts a collection of Dask-enabled Python modules for processing Earth Observation imagery, primarily focusing on Sentinel-2 data. 

Designed for scalable and efficient geospatial analysis, it leverages distributed computing using Dask on Kubernetes.

## Core Technology: [Calrissian](https://github.com/Duke-GCB/calrissian), [CWL](https://www.commonwl.org/) and [Dask](https://docs.dask.org/en/stable/index.html)

A central feature of this project is its robust integration with Calrissian, a CWL runner designed for Kubernetes. Our workflows leverage a custom `DaskGatewayRequirements` CWL extension, allowing tasks to seamlessly utilize Dask clusters managed by Dask Gateway. This setup provides:

* **Orchestrated Parallelism**: CWL workflows define the processing steps, while Calrissian orchestrates their execution across a Dask cluster, efficiently managing resources and task dependencies.

* **Scalability**: Dask Gateway dynamically scales the Dask cluster workers on Kubernetes as needed, adapting to the computational demands of large EO datasets.

* **Reproducibility & Portability**: CWL ensures workflows are standardized, reproducible, and portable across various compliant execution environments.

## Modules

This repository currently includes the following processing modules:

### eopf-sentinel-2:

* Processes individual Sentinel-2 STAC items.

* Generates vegetation/water indices and color composites.

[More details here](apps/eopf-sentinel-2/index.md)

### cloudless-mosaic:

* Generates monthly median mosaics from Sentinel-2 imagery.

* Applies cloud filtering and outputs Cloud-Optimized GeoTIFFs (COGs).

[More details here](apps/cloudless-mosaic/index.md)

## Getting Started

To dive into the setup, installation, and detailed execution instructions (including Dask worker image preparation and Calrissian usage), please refer to the comprehensive documentation for each module.