class: CommandLineTool
id: main
requirements:
  DockerRequirement:
    dockerPull: ghcr.io/eoap/dask-app-package/eopf-sentinel-2:2.0.0
  EnvVarRequirement:
    envDef: {}
  calrissian:DaskGatewayRequirement:
    workerCores: 1
    workerCoresLimit: 1
    workerMemory: 4G
    clusterMaxCores: 10
    clusterMaxMemory: 40G
  SchemaDefRequirement:
    types:
    - name: '#CRS'
      type: enum
      symbols:
      - '4326'
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
        type: '#CRS'
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
  ResourceRequirement:
    ramMin: 4096
    coresMin: 1
baseCommand:
- eopf-sentinel-2-proc
arguments: []
inputs:
  item-url:
    type: '#URI'
    inputBinding:
      position: 1
      prefix: --item-url
      valueFrom: $(self.value)
    label: item-url
    doc: item url.
  window-size:
    type:
    - 'null'
    - int
    default: null
    label: Real-product window
    doc: Optional centred window in pixels; omitted to process the full acquisition.
    inputBinding:
      prefix: --window-size
outputs:
  stac-catalog:
    type: Directory
    outputBinding:
      glob: .
    label: stac-catalog
    doc: stac catalog.
label: eopf-sentinel-2
doc: Dask application package eopf-sentinel-2
cwlVersion: v1.2
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
s:name: eopf-sentinel-2
s:description: Dask application package eopf-sentinel-2
s:dateCreated: '2025-01-01'
s:softwareHelp:
  '@type': s:CreativeWork
  s:name: Dask application package training
  s:url: https://eoap.github.io/dask-app-package/
s:publisher: *id001
