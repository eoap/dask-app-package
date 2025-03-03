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
      clustermaxCore: 7
      clusterMaxMemory: "16G"
      
  baseCommand: ["cloudless-mosaic"]
  # this CLI invokes cloudless-mosaic --start-date 2020-10-01 --end-date 2020-12-31 --aoi -122.27508544921875,47.54687159892238,-121.96128845214844,47.745787772920934 --bands nir --bands red --bands green --collection sentinel-2-l2a --resolution 100
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
      type: string[]
      inputBinding:
        position: 1
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
  outputs:
    stac-catalog:
      type: Directory
      outputBinding:
        glob: .

