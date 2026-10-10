cwlVersion: v1.2
class: CommandLineTool
id: gateway-acceptance
label: Dask Gateway lifecycle acceptance
doc: Run real distributed tasks on two gateway workers; Calrissian creates and disposes
  the cluster.
baseCommand:
- python
- acceptance.py
arguments:
- $(inputs.count)
inputs:
  count:
    type: int
    default: 100
    label: Task count
    doc: Number of integers included in the distributed sum.
outputs:
  report:
    type: File
    label: Distributed execution report
    doc: Computed sum and worker addresses.
    outputBinding:
      glob: report.json
requirements:
  DockerRequirement:
    dockerPull: ghcr.io/eoap/dask-app-package/eopf-sentinel-2:1.1.0
  InlineJavascriptRequirement: {}
  NetworkAccess:
    networkAccess: true
  ResourceRequirement:
    coresMin: 1
    ramMin: 512
  calrissian:DaskGatewayRequirement:
    workerCores: 1
    workerCoresLimit: 1
    workerMemory: 1G
    clusterMaxCores: 2
    clusterMaxMemory: 2G
  InitialWorkDirRequirement:
    listing:
    - entryname: acceptance.py
      entry: |
        import json
        import os
        import sys
        from dask_gateway import Gateway

        count = int(sys.argv[1])
        with Gateway(os.environ["DASK_GATEWAY_URL"]) as gateway:
            cluster = gateway.connect(os.environ["DASK_CLUSTER"])
            client = cluster.get_client()
            client.wait_for_workers(2, timeout=120)
            futures = client.map(lambda number: number * number, range(count))
            result = sum(client.gather(futures))
            assert result == sum(number * number for number in range(count))
            workers = sorted(client.scheduler_info()["workers"])
            assert len(workers) == 2
            with open("report.json", "w") as stream:
                json.dump({"sum_of_squares": result, "count": count, "workers": workers, "cluster": cluster.name}, stream, indent=2)
            client.close()
            # Cluster shutdown belongs to Calrissian's dispose sidecar.
$namespaces:
  s: https://schema.org/
  calrissian: https://calrissian-cwl.github.io/schema#
s:softwareVersion: 1.4.1
s:codeRepository: https://github.com/eoap/dask-app-package
s:license: https://spdx.org/licenses/MIT.html
s:author:
- class: s:Person
  s:name: Leonardo Mizzoni
  s:email: leonardo.mizzoni@terradue.com
