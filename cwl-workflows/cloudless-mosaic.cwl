# Standalone application tool; preserves the original one-step workflow interface.
class: CommandLineTool
id: main
requirements:
  DockerRequirement:
    dockerPull: ghcr.io/eoap/dask-app-package/cloudless-mosaic:1.1.0
  EnvVarRequirement:
    envDef: {}
  calrissian:DaskGatewayRequirement:
    workerCores: 1
    workerCoresLimit: 1
    workerMemory: 2G
    clusterMaxCores: 24
    clusterMaxMemory: 48G
  SchemaDefRequirement:
    types:
    - name: '#URI'
      type: record
      fields:
      - name: value
        type: string
    - name: '#Date'
      type: record
      fields:
      - name: value
        type: string
    - name: '#BBox'
      type: record
      fields:
      - name: bbox
        type:
          type: array
          items: double
      - name: crs
        type: string
    - name: '#SpectralBand'
      type: enum
      symbols:
      - red
      - green
      - blue
      - nir
      - swir16
      - swir22
  InlineJavascriptRequirement: {}
  NetworkAccess:
    networkAccess: true
baseCommand:
- cloudless-mosaic
arguments: []
inputs:
  start-date:
    type: '#Date'
    inputBinding:
      position: 1
      prefix: --start-date
      valueFrom: $(self.value)
    label: start-date
    doc: start date.
    default:
      value: '2020-10-01'
  end-date:
    type: '#Date'
    inputBinding:
      position: 1
      prefix: --end-date
      valueFrom: $(self.value)
    label: end-date
    doc: end date.
    default:
      value: '2020-12-31'
  aoi:
    type: '#BBox'
    inputBinding:
      position: 1
      prefix: --aoi
      valueFrom: $(self.bbox.join(","))
    label: aoi
    doc: aoi.
    default:
      bbox:
      - -122.27508544921875
      - 47.54687159892238
      - -121.96128845214844
      - 47.745787772920934
      crs: CRS84
  bands:
    type:
      type: array
      items: '#SpectralBand'
    label: bands
    doc: bands.
    default:
    - nir
    - red
    - green
  collection:
    type: string
    inputBinding:
      position: 1
      prefix: --collection
    label: collection
    doc: collection.
    default: sentinel-2-l2a
  resolution:
    type: int
    inputBinding:
      position: 1
      prefix: --resolution
    label: resolution
    doc: resolution.
  max_items:
    type: int
    inputBinding:
      position: 1
      prefix: --max-items
    label: max_items
    doc: max_items.
    default: 1000
  max_cloud_cover:
    type: int
    inputBinding:
      position: 1
      prefix: --max-cloud-cover
    label: max_cloud_cover
    doc: max_cloud_cover.
    default: 25
outputs:
  stac-catalog:
    type: Directory
    outputBinding:
      glob: .
    label: stac-catalog
    doc: stac catalog.
label: cloudless-mosaic
doc: Dask application package cloudless-mosaic
cwlVersion: v1.2
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
