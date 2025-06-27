# Execution Guide

This guide details how to execute the processing module, leveraging Dask for parallel processing in a distributed cluster environment and Calrissian for CWL workflow orchestration.

## Distributed Cluster Setup

To enable parallel processing with Dask, a Dask Gateway object is required to create a Dask Cluster.

#### Prerequisites

* **Dask Gateway Deployment**: It is assumed that a Dask Gateway is already deployed and accessible. The [dev-platform-eoap repository](https://github.com/eoap/dev-platform-eoap/tree/main/dask-gateway) provides a streamlined method for deploying Dask Gateway on Kubernetes, which can then be integrated with a Code-Server for module execution.

Once the Dask Gateway is available, you can proceed with running the processing module:

* **Direct Execution**: The [provided Jupyter Notebook](https://github.com/eoap/dask-app-package/blob/main/eopf-sentinel-2/notebook.ipynb) demonstrates how to execute the module directly using its main function.

* **Command-Line Interface (CLI)**: Alternatively, the module can be executed via its [CLI](cli.md) interface, offering a more traditional command-line approach.


## Calrissian CWL Execution

This module includes a Common Workflow Language (CWL) workflow, optimized for parallel processing on a Dask Cluster. A new CWL extension, DaskGatewayRequirements, has been developed to enable CWL runners like Calrissian to leverage Dask's distributed computing capabilities.

### Environment Setup:

Ensure the environment described in the [Distributed Cluster Setup](#distributed-cluster-setup) section is established.

### Execution Methods:

The [workflow file](https://github.com/eoap/dask-app-package/releases/download/1.0.1/eopf-sentinel-2.1.0.1.cwl) can be executed using Calrissian in two primary ways:

* #### Direct Calrissian Command

Execute the workflow directly using the calrissian command:
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
    https://github.com/eoap/dask-app-package/releases/download/1.0.1/eopf-sentinel-2.1.0.1.cwl \
    --input-url "https://stac.core.eopf.eodc.eu/collections/sentinel-2-l1c/items/S2B_MSIL1C_20250113T103309_N0511_R108_T32TLQ_20250113T122458"
```
* #### Kubernetes Job Submission

For robust and scalable execution, you can submit the workflow as a Kubernetes Job:

```yaml
---
apiVersion: batch/v1
kind: Job
metadata:
  name: calrissian-sentinel2
spec:
  ttlSecondsAfterFinished: 60
  template:
    spec:
      serviceAccountName: default
      securityContext:
        runAsUser: 0
        runAsGroup: 0
      containers:
        - name: calrissian
          image: calrissian:0.19.0
          command: ["calrissian"]
          args:
            - --debug
            - --stdout 
            - /calrissian/results.json
            - --stderr 
            - /calrissian/app.log
            - --max-ram 
            - 16G
            - --max-cores 
            - "8"
            - --tmp-outdir-prefix 
            - /calrissian/tmp/ 
            - --outdir
            - /calrissian/results
            - --usage-report 
            - /calrissian/usage.json
            - --tool-logs-basepath 
            - /calrissian/logs
            - --dask-gateway-url
            - "http://traefik-dask-gateway.eoap-dask-gateway.svc.cluster.local:80"
            - https://github.com/eoap/dask-app-package/releases/download/1.0.1/eopf-sentinel-2.1.0.1.cwl
            - --item-url 
            - "https://stac.core.eopf.eodc.eu/collections/sentinel-2-l1c/items/S2B_MSIL1C_20250113T103309_N0511_R108_T32TLQ_20250113T122458"
          volumeMounts:
            - name: calrissian-volume
              mountPath: /calrissian
          env:
            - name: CALRISSIAN_POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
      restartPolicy: Never
      volumes:
        - name: calrissian-volume
          persistentVolumeClaim:
            claimName: calrissian-claim 
  backoffLimit: 3
```
**Important Note**: Ensure you are using a Calrissian image that supports DaskGateway. 

The latest version can be found [here](https://github.com/Terradue/calrissian/tree/dask-gateway)

## Input Data

The pipeline is designed to process Sentinel-2 STAC items where the assets are in Zarr format.

Example Input URL:
```bash
https://stac.core.eopf.eodc.eu/collections/sentinel-2-l1c/items/S2B_MSIL1C_20250113T103309_N0511_R108_T32TLQ_20250113T122458
```
This example STAC item references data hosted at `https://zarr.eopf.copernicus.eu/`.

## Output Data

Upon successful execution, the pipeline generates the following outputs:

* Common Vegetation and Water Indices (Zarr format):

    * `ndvi`: Normalized Difference Vegetation Index (NIR, Red)

    * `ndwi`: Normalized Difference Water Index (Green, NIR)

    * `ndmir`: Normalized Difference Moisture Index (SWIR16, SWIR22)

    * `nbr`: Normalized Burn Ratio (NIR, SWIR22)

    * `ndwi2`: (NIR, SWIR16)

    * `mndwi`: Modified Normalized Difference Water Index (Green, SWIR16)

    * `ndbi`: Normalized Difference Built-up Index (SWIR16, NIR)

* Various Color-Corrected Composite Images (Zarr format):

    * `rgb`: Natural Color Composite (Red, Green, Blue)

    * `vea`: Vegetation Analysis Composite (SWIR16, SWIR22, Red)

    * `civ`: Color Infrared Vegetation Composite (NIR, Red, Green)

    * `law`: Land/Water Composite (NIR, SWIR16, Red)

    * `sir`: Shortwave Infrared Composite (SWIR22, NIR, Red)

    * `fcu`: False Color Urban Composite (SWIR22, SWIR16, Red)

    * `atp`: Atmospheric Penetration Composite (SWIR22, SWIR16, NIR)

* Newly Created STAC Item: A new STAC item referencing the newly generated products and their assets.

