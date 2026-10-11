# Dask application package: Sentinel-2 Monthly Mosaic Generator

This project generates monthly median mosaics from Sentinel-2 imagery using STAC data sources. It retrieves Sentinel-2 data from the Planetary Computer STAC API, processes the data with Dask and Xarray, and stores the results as Cloud-Optimized GeoTIFFs (COGs) with an associated SpatioTemporal Asset Catalog (STAC).

## Python application

### Features

- Retrieves Sentinel-2 imagery based on a time range and area of interest (AOI).
- Filters images by cloud cover.
- Generates monthly median mosaics.
- Saves mosaics as Cloud-Optimized GeoTIFFs (COGs).
- Creates a STAC catalog for easy data access and discovery.
- Uses Dask for parallel processing.

### Installation

Ensure you have Python 3.8+ and the required dependencies installed. You can install them using `hatch`:

```bash
cd cloudless-mosaic
```

#### Dependencies

The project requires the following libraries, managed in a `pyproject.toml` file:

- `numpy`
- `pandas`
- `stackstac`
- `pystac-client`
- `planetary-computer`
- `pystac`
- `xrspatial`
- `rioxarray`
- `rio-stac`
- `loguru`
- `dask-gateway`
- `click`

### Usage

#### Running the Script

Use the CLI to run the script with the necessary parameters:

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
#### Environment Variables

The script connects to a Dask cluster for processing. Ensure the `DASK_CLUSTER` environment variable is set:

```bash
export DASK_CLUSTER=eoap-dask-gateway.600b64a112eb404888df41006e19666f
```

### Output

- Cloud-Optimized GeoTIFFs (COGs) stored in the `monthly-mosaic-YYYY-MM` directories.
- A STAC catalog (`catalog.json`) containing metadata for generated mosaics.

## CWL Workflow

This project also includes a CWL workflow for automating the generation of Sentinel-2 monthly mosaics. The workflow:

* Defines inputs such as start and end dates, AOI, bands, resolution, and cloud cover filtering.
* Uses a CommandLineTool to run the cloudless-mosaic application inside a Docker container.
* Executes in a distributed Dask cluster via `DaskGatewayRequirement` to optimize parallel processing.
* Outputs a STAC catalog containing the generated mosaic metadata.

The workflow file (`cwl-workflows/monthly-composite.cwl`) can be executed with a CWL-compatible runner supporting the **`DaskGatewayRequirement`**  such as `calrissian`:

```bash
calrissian \
            --stdout \
            /calrissian/results.json \
            --stderr \
            /calrissian/app.log \
            --max-ram  \
            16G \
            --max-cores  \
            "8" \
            --tmp-outdir-prefix \
            /calrissian/tmp/ \
            --outdir \
            /calrissian/results \
            --usage-report \
            /calrissian/usage.json \
            --tool-logs-basepath \
            /calrissian/logs \
            --pod-serviceaccount \
            calrissian-sa \
            --dask-gateway-url \
            "http://traefik-dask-gateway.eoap-dask-gateway.svc.cluster.local:80" \
            https://github.com/eoap/dask-app-package/releases/download/1.0.0/monthly-composite.1.0.0.cwl \
            --resolution 100 \
            --start-date 2020-01-01 \
            --end-date 2020-12-31
```

## Development platorm

Run the Application Package in a kubernetes cluster. Minikube can be an option if you have enough resources.

Clone the repository:

```
git clone https://github.com/eoap/dev-platform-eoap.git 
```

Change directory to `dask-gateway`

```
cd dask-gateway
```

Use `skaffold` to deploy Code server and Dask Gateway:


```
skaffold dev
```

Use the port-forwards to access the services. 

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/)
- [STAC Specification](https://stacspec.org/)
- [Cloud-Optimized GeoTIFF](https://www.cogeo.org/)




```
start-dask.sh
```

```
source dask_cluster_name.txt 
```


```
python bai.py --pre_fire_url "https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l2a-cogs/items/S2B_10TFK_20210713_0_L2A"           --post_fire_url "https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l2a-cogs/items/S2A_10TFK_20210718_0_L2A"
```

```
end-dask.sh
```




 cloudless-mosaic --start-date 2020-10-01 --end-date 2020-12-31 --aoi -122.27508544921875,47.54687159892238,-121.96128845214844,47.745787772920934 --bands nir --bands red --bands green --collection sentinel-2-l2a --resolution 100



 kubectl create secret docker-registry my-fake-secret \
  --docker-server=fake.registry.io \
  --docker-username=fakeuser \
  --docker-password=fakepassword \
  --docker-email=fake@example.com \
  -n eoap-dask-gateway
## PDE acceptance and typed CWL

The feature branch uses standalone CWL v1.2 documents with embedded URI, Date,
BBox and SpectralBand schemas and documented metadata. Jobs in `project.toml`
use records for URI/date/bounding-box inputs. Use upstream Calrissian's
`clusterMaxCores` spelling and Dask Gateway 2025.4.0 with the course images.

`cwl-workflows/gateway-acceptance.cwl` runs real tasks on two workers and records
the computed result and worker addresses. This bounded test verifies upstream
Calrissian's cluster creation, execution and disposal; it is separate from the
full satellite notebook workloads. The development deployment is in the sibling
`dev-platform-eoap/dask-gateway` folder.

The cloudless/EOPF documents expose their application CommandLineTool directly
with the original one-step workflow's inputs, defaults and outputs. This keeps
the packages standalone and avoids the pinned upstream Calrissian nested custom
requirement validation failure. Dask Gateway remains a mandatory requirement;
the requirement is not downgraded to an optional hint.

## 2.0.0 release preparation

This feature uses Python 3.12 for the notebook client, processing commands,
scheduler and workers, with Dask/Distributed/Gateway 2025.4.0. Build from the
repository root with `docker build -t dask-worker:local .`; the image contains
both course applications and their matching scheduler/worker commands. Runtime,
notebook, build, validation and metadata environments have separate hash locks.
The Calrissian validation lock pins the same upstream commit as PDE.

The application packages are standalone CWL v1.2 tools with mandatory
`DaskGatewayRequirement`, embedded typed inputs and complete schema.org metadata.
`python scripts/cwl-docs.py --validate` uses the pinned Calrissian extension schema;
`scripts/check-metadata.py` validates the actual transpiler-mate metadata model
in the separate metadata environment. The generic cwl2oci parser currently does
not accept this mandatory custom requirement, so it is not used to claim OCI
conversion support. No CWL packing is used.

CI runs two real-data notebook lessons and the Calrissian two-worker lifecycle
case on Kubernetes. Cloudless acceptance uses two Sentinel-2 acquisitions at
100 m resolution. EOPF acceptance uses an explicit 1024-pixel centred window
from the original real Zarr acquisition (`DASK_LAB_EOPF_WINDOW=1024`), records
that window and derives STAC geometry from the resulting GeoTIFF. Omit the
window to process the full acquisition. Both paths check readable assets,
scientific values and geographic metadata; generated pixels are not substituted.

Only accepted builds publish candidate GHCR image tags; the same dual-application
image is available under the existing cloudless and EOPF package names. Stable
publication requires an explicit main-branch workflow dispatch after acceptance.
It publishes immutable image references, standalone CWL files, locks and checksums.
