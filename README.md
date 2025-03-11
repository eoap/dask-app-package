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