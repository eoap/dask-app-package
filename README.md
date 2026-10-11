# Dask application packages

Learn to process real Sentinel-2 imagery with Dask Gateway and standalone CWL
v1.2 application packages. The two lessons produce monthly cloudless mosaics
from Planetary Computer acquisitions and RGB, false-colour, NDVI and NDWI
products from a real EOPF Zarr store.

## Learn on Kubernetes

Clone [dev-platform-eoap](https://github.com/eoap/dev-platform-eoap), enter its
`dask-gateway` folder and follow that module's README to deploy the editor,
Dask Gateway and disposable SeaweedFS. Minikube is one supported development
cluster; the application packages target Kubernetes with Dask Gateway.

The course notebooks are `cloudless-mosaic/notebook.ipynb` and
`eopf-sentinel-2/notebook.ipynb`. `eopf-sentinel-2/test.ipynb` is an exploratory
scratch notebook, not an accepted lesson. Use `task labs:all` for both lessons,
`task test:dask` for distributed lifecycle acceptance, and `task test:cwl` for
both typed scientific CWL jobs.

## Reproduce the Python environment

Use Python 3.12 and uv from the repository root:

```bash
uv venv --python 3.12
uv pip sync --require-hashes requirements-notebooks.txt requirements-build.txt
uv pip install --no-deps --no-build-isolation -e cloudless-mosaic -e eopf-sentinel-2
```

Connect to the configured gateway and set `DASK_CLUSTER` to an existing cluster
name before calling `cloudless-mosaic` or `eopf-sentinel-2-proc` directly. The
notebooks and Calrissian create and dispose clusters themselves.

## Typed CWL jobs

Use `cwl-workflows/cloudless-mosaic.cwl` or `cwl-workflows/eopf-sentinel-2.cwl`
with upstream Calrissian and `--dask-gateway-url`. Supply a YAML job file,
rather than scalar arguments for record inputs. Working bounded jobs are in
`acceptance/jobs/`; `project.toml` retains larger course cases. Bounding boxes
use quoted EPSG code `"4326"` and geographic longitude/latitude order.

Published release artifacts select immutable GHCR image digests. For unpublished
feature testing, explicitly select the image built from the same source and
runtime lock; do not fall back to an older course image.

## PDE acceptance and typed CWL

The feature branch uses standalone CWL v1.2 documents with embedded URI, Date,
BBox and SpectralBand schemas and documented metadata. Jobs in `project.toml`
use records for URI/date/bounding-box inputs. Use upstream Calrissian's
`clusterMaxCores` spelling and Dask Gateway 2025.4.0 with the course images.

`cwl-workflows/gateway-acceptance.cwl` runs real tasks on two workers and records
the computed result and worker addresses. This bounded test verifies upstream
Calrissian's cluster creation, execution and disposal; it is separate from the
full satellite notebook workloads. The development deployment is the `dask-gateway` module in
[dev-platform-eoap](https://github.com/eoap/dev-platform-eoap). It initializes
this course from GitHub; no sibling training checkout is needed.

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
