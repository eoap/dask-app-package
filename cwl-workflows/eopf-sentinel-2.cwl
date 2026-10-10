# Standalone application tool; preserves the original one-step workflow interface.
class: CommandLineTool
id: main
requirements:
  DockerRequirement:
    dockerPull: ghcr.io/eoap/dask-app-package/eopf-sentinel-2:1.1.0
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
s:softwareVersion: 1.4.1
s:codeRepository: https://github.com/eoap/dask-app-package
s:license: https://spdx.org/licenses/MIT.html
s:author:
- class: s:Person
  s:name: Leonardo Mizzoni
  s:email: leonardo.mizzoni@terradue.com
