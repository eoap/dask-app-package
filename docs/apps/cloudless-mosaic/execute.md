# Execute cloudless-mosaic

## Deploy the matching runtime

Use the `dask-gateway` module in
[dev-platform-eoap](https://github.com/eoap/dev-platform-eoap). Its editor
initializes this course from GitHub. Python 3.12 and the runtime lock must match
between clients and workers. Build candidate images from the repository root:

```bash
docker build -t dask-worker:local .
```

Make that image available to your Kubernetes cluster and configure the gateway
backend and notebook `DASK_IMAGE` accordingly. The image contains both processing
applications, Dask scheduler and workers. Published release artifacts will
select accepted GHCR digests; older Python 3.10 images are incompatible.

## Run the notebook

From the platform's `dask-gateway` folder:

```bash
task labs LAB=cloudless-mosaic/notebook.ipynb KUBE_CONTEXT=<context>
```

The notebook creates two workers and closes its gateway cluster. Cloudless
acceptance limits the search to two real acquisitions at 100 m. EOPF acceptance
uses an explicit centred 1024-pixel window from the original Zarr acquisition;
omit `window-size` in a direct application job to process the full tile.

## Run typed CWL

The standalone `cwl-workflows/cloudless-mosaic.cwl` embeds its input type definitions and
requires Calrissian with Dask Gateway support. Its corresponding YAML job is
`acceptance/jobs/cloudless-mosaic.yaml`. Supply record inputs from that job rather than
scalar command-line parameters. The larger jobs in `project.toml` retain the
course defaults.

Run `task test:cwl KUBE_CONTEXT=<context>` in the platform to execute both
scientific cases. The acceptance script selects the configured candidate image,
uses bounded worker budgets, preserves logs and usage under `/calrissian`, and
checks the produced STAC/GeoTIFF artifacts. Source CWL defaults target the
intended release 2.0.0; acceptance selects the actual tested image explicitly.

The mandatory extension is `calrissian:DaskGatewayRequirement`; its core budget
field is `clusterMaxCores`. Keep the requirement mandatory and avoid packing.
