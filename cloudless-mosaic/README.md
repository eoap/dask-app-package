
## Create a shell with hatch

Create a shell with:

```
hatch shell dev
```

Then the cloudless-mosaic cli is available. Check it with:

```
cloudless-mosaic --help
```


```
cloudless-mosaic --start-date 2020-10-01 --end-date 2020-12-31 --aoi -122.27508544921875,47.54687159892238,-121.96128845214844,47.745787772920934 --bands nir --bands red --bands green --collection sentinel-2-l2a --resolution 100
```



 calrissian --debug \
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





calrissian --debug \
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
            --start-date 2020-12-01 \
            --end-date 2020-12-31 \
            --bbox -9.822,37.862,-7.734,39.673


```
resolution: 100 
start-date: "2020-12-01"
end-date: "2020-12-31"
bbox: "-9.822,37.862,-7.734,39.673"
```

# add create configmap

```
  - verbs:
      - create
      - delete
    apiGroups:
      - ''
    resources:
      - configmaps
```

 calrissian --debug \
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
            cwl-workflows/monthly-composite.cwl \
            --resolution 100