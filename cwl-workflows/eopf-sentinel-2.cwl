cwlVersion: v1.2

$namespaces:
  s: https://schema.org/
  calrissian: https://calrissian-cwl.github.io/schema#

s:softwareVersion: 1.4.1
schemas:
  - http://schema.org/version/9.0/schemaorg-current-http.rdf

$graph:
- class: Workflow
  id: main
  requirements: 
    InlineJavascriptRequirement: {}
    NetworkAccess:
      networkAccess: true
    ScatterFeatureRequirement: {}
  inputs:
    item-url:
      type: string
  outputs:
    stac-catalog:
      outputSource: eopf-sentinel-2/stac-catalog
      type: Directory
  steps:
    eopf-sentinel-2:
      in: 
        item-url: item-url
      out: 
      - stac-catalog
      run:
        "#eopf-sentinel-2"

- class: CommandLineTool
  id: eopf-sentinel-2
  requirements:
    DockerRequirement: 
      dockerPull: ghcr.io/eoap/dask-app-package/eopf-sentinel-2:1.0.0
    EnvVarRequirement:
      envDef: {}
    calrissian:DaskGatewayRequirement:
      workerCores: 1
      workerCoresLimit: 1
      workerMemory: "2G"
      clusterMaxCore: 24
      clusterMaxMemory: "48G"
      
  baseCommand: ["eopf-sentinel-2"]
  arguments: []
  inputs:
    item-url:
      type: string
      inputBinding:
        position: 1
        prefix: "--item-url"
  outputs:
    stac-catalog:
      type: Directory
      outputBinding:
        glob: .

