# cloudless-mosaic application package

The authoritative standalone CWL v1.2 document is
[`cwl-workflows/cloudless-mosaic.cwl`](https://github.com/eoap/dask-app-package/blob/feature/pde-typed-cwl/cwl-workflows/cloudless-mosaic.cwl).
It embeds its input types, metadata and mandatory Dask Gateway requirement.

Generate an input/output and type reference from the checked-out document:

```bash
python scripts/cwl-docs.py --output /tmp/dask-cwl-docs
```

For typed real-data execution, use the corresponding job in `acceptance/jobs/`
and run `scripts/run-cwl-acceptance.py` in the Kubernetes acceptance controller.
The release artifacts contain image digests; source defaults target 2.0.0.
