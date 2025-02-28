#!/bin/bash

 python \
      dispose-dask.py \
      --gateway-url \
        http://traefik-dask-gateway.eoap-dask-gateway.svc.cluster.local:80
