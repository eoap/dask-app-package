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
      entry: "import json\nimport os\nimport sys\nfrom dask_gateway import Gateway\n\
        \ncount = int(sys.argv[1])\nwith Gateway(os.environ[\"DASK_GATEWAY_URL\"])\
        \ as gateway:\n    cluster = gateway.connect(os.environ[\"DASK_CLUSTER\"])\n\
        \    client = cluster.get_client()\n    client.wait_for_workers(2, timeout=120)\n\
        \    futures = client.map(lambda number: number * number, range(count))\n\
        \    result = sum(client.gather(futures))\n    assert result == sum(number\
        \ * number for number in range(count))\n    workers = sorted(client.scheduler_info()[\"\
        workers\"])\n    assert len(workers) == 2\n    with open(\"report.json\",\
        \ \"w\") as stream:\n        json.dump({\"sum_of_squares\": result, \"count\"\
        : count, \"workers\": workers, \"cluster\": cluster.name}, stream, indent=2)\n\
        \    client.close()\n    # Cluster shutdown belongs to Calrissian's dispose\
        \ sidecar.\n"
$namespaces:
  s: https://schema.org/
  calrissian: https://calrissian-cwl.github.io/schema#
s:softwareVersion: 2.0.0
s:codeRepository: https://github.com/eoap/dask-app-package
s:license: https://spdx.org/licenses/MIT.html
s:author:
- '@type': s:Person
  s:name: Leonardo Mizzoni
  s:givenName: Leonardo
  s:familyName: Mizzoni
  s:email: leonardo.mizzoni@terradue.com
  s:affiliation: &id001
    '@type': s:Organization
    s:name: Terradue
    s:url: https://www.terradue.com
s:name: Dask Gateway lifecycle acceptance
s:description: Run real distributed tasks on two gateway workers; Calrissian creates
  and disposes the cluster.
s:dateCreated: '2025-01-01'
s:softwareHelp:
  '@type': s:CreativeWork
  s:name: Dask application package training
  s:url: https://eoap.github.io/dask-app-package/
s:publisher: *id001
