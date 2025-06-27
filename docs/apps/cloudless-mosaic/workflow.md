# CWL Workflow for cloudless-mosaic module
```yaml
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
    start-date:
      type: string
      default: "2020-10-01"
    end-date:
      type: string
      default: "2020-12-31"
    aoi:
      type: string
      default: "-122.27508544921875,47.54687159892238,-121.96128845214844,47.745787772920934"
    bands:
      type: string[]
      default: ["nir", "red", "green"]
    collection:
      type: string
      default: "sentinel-2-l2a"
    resolution:
      type: int
    max_items: 
      type: int
      default: 1000
    max_cloud_cover:
      type: int
      default: 25
  outputs:
    stac-catalog:
      outputSource: step_monthly_composite/stac-catalog
      type: Directory
  steps:
    step_monthly_composite:
      in: 
        start-date: start-date
        end-date: end-date
        aoi: aoi
        bands: bands
        collection: collection
        resolution: resolution
        max_items: max_items
        max_cloud_cover: max_cloud_cover
      out: 
      - stac-catalog
      run:
        "#cloudless-mosaic"

- class: CommandLineTool
  id: cloudless-mosaic
  requirements:
    DockerRequirement: 
      dockerPull: ghcr.io/eoap/dask-app-package/cloudless-mosaic:1.0.0
    EnvVarRequirement:
      envDef: {}
    calrissian:DaskGatewayRequirement:
      workerCores: 1
      workerCoresLimit: 1
      workerMemory: "2G"
      clusterMaxCore: 24
      clusterMaxMemory: "48G"
      
  baseCommand: ["cloudless-mosaic"]
  arguments: []
  inputs:
    start-date:
      type: string
      inputBinding:
        position: 1
        prefix: "--start-date"
    end-date:
      type: string
      inputBinding:
        position: 1
        prefix: "--end-date"
    aoi:
      type: string
      inputBinding:
        position: 1
        prefix: "--aoi"
    bands:
      type:
      - "null"
      - type: array
        items: string
        inputBinding:
          prefix: "--bands"
    collection:
      type: string
      inputBinding:
        position: 1
        prefix: "--collection"
    resolution:
      type: int
      inputBinding:
        position: 1
        prefix: "--resolution"
    max_items:
      type: int
      inputBinding:
        position: 1
        prefix: "--max-items"
    max_cloud_cover:
      type: int
      inputBinding:
        position: 1
        prefix: "--max-cloud-cover"
  outputs:
    stac-catalog:
      type: Directory
      outputBinding:
        glob: .
```