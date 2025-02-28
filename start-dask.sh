#!/bin/bash

python \
    /app/init-dask.py \
    --target \
    ./dask_cluster_name.txt \
    --gateway-url \
    http://traefik-dask-gateway.eoap-dask-gateway.svc.cluster.local:80 \
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
