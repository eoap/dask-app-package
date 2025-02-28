#!/bin/bash

python \
    /app/init-dask.py \
    --target \
    /shared/dask_cluster_name.txt \
    --gateway-url \
    {{ .Values.daskGatewayUrl }} \
    --image \
    {{ .Values.daskWorkerImage }} \
    --worker-cores \
    "0.5" \
    --worker-memory \
    "2" \
    --worker-cores-limit \
    "1" \
    --max-cores \ 
    "5" \
    --max-ram \
    "16"
