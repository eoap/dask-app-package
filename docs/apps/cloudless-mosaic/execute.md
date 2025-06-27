# Execution Guide

This guide details how to execute the Sentinel-2 Monthly Mosaic Generator module, leveraging Dask for parallel processing in a distributed cluster environment and Calrissian for CWL workflow orchestration.

## Distributed Cluster Setup

To enable parallel processing with Dask, a Dask Gateway object is required to create a Dask Cluster.

### Prerequisites:

* **Dask Gateway Deployment**: It is assumed that a Dask Gateway is already deployed and accessible. The [dev-platform-eoap repository](https://github.com/eoap/dev-platform-eoap/tree/main/dask-gateway) provides a streamlined method for deploying Dask Gateway on Kubernetes, which can then be integrated with a Code-Server for module execution.

* **Dask Cluster Environment Variable**: Ensure the `DASK_CLUSTER` environment variable is set to point to your Dask cluster. For example:
```bash
export DASK_CLUSTER=eoap-dask-gateway.600b64a112eb404888df41006e19666f
```
* **Dask Worker Image**: For Dask to utilize your module's dependencies and code, a custom Docker image for the Dask workers must be built and made accessible to the Kubernetes cluster. This image should contain all the necessary Python packages and your module's code.

  * **Building and Providing the Worker Image**:
  The easiest way to build the worker image for this module is to navigate into the `cloudless-mosaic/` directory (where the Dockerfile for  the worker is located) and run a Docker build command:
    ```bash
    cd cloudless-mosaic/
    docker build -t cloudless-mosaic-worker:latest .
    ```
    Once built, this image needs to be available to your Kubernetes cluster.

  * **Using ttl.sh for Temporary Images**: For development or testing, ttl.sh provides an anonymous, ephemeral registry. This allows you to   quickly build and push a temporary, pullable image without authentication, which expires after a set duration (e.g., 1 hour).
    ```bash
    IMAGE_NAME=cloudless-mosaic-worker
    docker build -t ttl.sh/${IMAGE_NAME}:1h .
    docker push ttl.sh/${IMAGE_NAME}:1h
    echo "Temporary image available at: ttl.sh/${IMAGE_NAME}:1h"
    ```
    You would then use this ttl.sh image name in your Dask Gateway configuration or Calrissian workflow.

Once the Dask Gateway is available, you can proceed with running the processing module:

* **Direct Execution**: The [provided Jupyter Notebook](https://github.com/eoap/dask-app-package/blob/main/cloudless-mosaic/notebook.ipynb) demonstrates how to execute the module directly using its main function.

* **Command-Line Interface (CLI)**: Alternatively, the module can be executed via its [CLI](cli.md) interface, offering a more traditional command-line approach.

## Calrissian CWL Execution

This project includes a Common Workflow Language (CWL) workflow for automating the generation of Sentinel-2 monthly mosaics. The workflow leverages a `DaskGatewayRequirement` extension, enabling CWL runners like Calrissian to optimize parallel processing on a Dask cluster.

### Environment Setup:

Ensure the environment described in the [Distributed Cluster Setup](#distributed-cluster-setup) section is established, including the DASK_CLUSTER environment variable.

### Execution Method

The [workflow file](https://github.com/eoap/dask-app-package/releases/download/1.0.1/cloudless-mosaic.1.0.1.cwl) can be executed using Calrissian in two primary ways:

* #### Direct Calrissian Command

Execute the workflow directly using the calrissian command:
```bash
calrissian \
    --stdout /calrissian/results.json \
    --stderr /calrissian/app.log \
    --max-ram 16G \
    --max-cores "8" \
    --tmp-outdir-prefix /calrissian/tmp/ \
    --outdir /calrissian/results \
    --usage-report /calrissian/usage.json \
    --tool-logs-basepath /calrissian/logs \
    --pod-serviceaccount calrissian-sa \
    --dask-gateway-url "http://traefik-dask-gateway.eoap-dask-gateway.svc.cluster.local:80" \
    https://github.com/eoap/dask-app-package/releases/download/1.0.1/cloudless-mosaic.1.0.1.cwl \
    --resolution 100 \
    --start-date 2020-01-01 \
    --end-date 2020-12-31
```

* #### Kubernetes Job Submission

For robust and scalable execution, you can submit the workflow as a Kubernetes Job:

```yaml
---
apiVersion: batch/v1
kind: Job
metadata:
  name: calrissian-mosaic
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
            - https://github.com/eoap/dask-app-package/releases/download/1.0.1/cloudless-mosaic.1.0.1.cwl
            - --resolution
            - 100
            - --start-date
            - "2020-01-01"
            - --end-date 
            - "2020-12-31"
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
Important Note: Ensure you are using a Calrissian image that supports DaskGateway. The latest version can be found here.

## Input Data

The module retrieves Sentinel-2 imagery from the Planetary Computer STAC API based on the specified parameters:

* **Time Range**: Defined by `--start-date` and `--end-date`.
* **Area of Interest (AOI)**: A bounding box (min_lon,min_lat,max_lon,max_lat).
* **Bands**: Specific spectral bands to retrieve (e.g., nir, red, green).
* **Collection**: The Sentinel-2 collection to use (e.g., sentinel-2-l2a).
* *Max Cloud Cover*: Filters images to include only those below a specified cloud cover percentage.
* *Max Items*: Limits the maximum number of STAC items to process.

## Output Data

Upon successful execution, the pipeline generates the following outputs:

* **Cloud-Optimized GeoTIFFs (COGs)**: Monthly median mosaics are saved as COGs, organized into directories named `monthly-mosaic-YYYY-MM`
