# Calrissian CWL Extension: DaskGatewayRequirement

## Overview

The `DaskGatewayRequirement` is a custom CWL extension developed for the Calrissian CWL runner, enabling dynamic provisioning of Dask clusters through Dask Gateway on Kubernetes. This extension allows a CommandLineTool to declare runtime needs for distributed processing resources (e.g., cores, memory) via a standard CWL ProcessRequirement.

When used in a workflow step, Calrissian will:

* Provision a Dask cluster with the specified resource limits.
* Run the CWL tool with access to this Dask cluster.
* Shutdown the cluster after tool execution completes.

## Schema

The `DaskGatewayRequirement` is defined in the following custom schema:

```yaml
$base: https://calrissian-cwl.github.io/schema#
$namespaces:
  cwl: "https://w3id.org/cwl/cwl#"
$graph:
  - $import: https://w3id.org/cwl/CommonWorkflowLanguage.yml

  - name: DaskGatewayRequirement
    type: record
    extends: cwl:ProcessRequirement
    inVocab: false
    doc: "Indicates that a process requires a Dask cluster procured via [Dask Gateway](https://gateway.dask.org/) runtime."
    fields:
      class:
        type: 'string'
        doc: "Always 'DaskGatewayRequirement'"
        jsonldPredicate:
          "_id": "@type"
          "_type": "@vocab"
      workerCores:
        type: ['int', 'cwl:Expression']
        doc: Number of cpu-cores available for a Dask worker.
      workerCoresLimit:
        type: ['int', 'cwl:Expression']
        doc: Maximum number of cpu-cores available for a Dask worker.
      workerMemory:
        type: ['string', 'cwl:Expression']
        doc: Maximum memory (e.g., '4G') per Dask worker.
      clusterMaxCores:
        type: ['int', 'cwl:Expression']
        doc: Cluster-wide core count upper limit.
      clusterMaxMemory:
        type: ['string', 'cwl:Expression']
        doc: Cluster-wide memory upper limit.
```

## Example Usage in CommandLineTool

```yaml
cwlVersion: v1.2
$namespaces:
  s: https://schema.org/
  calrissian: https://calrissian-cwl.github.io/schema#
s:softwareVersion: 1.4.1
schemas:
  - http://schema.org/version/9.0/schemaorg-current-http.rdf

class: CommandLineTool
id: eopf-sentinel-2
requirements:
  DockerRequirement:
    dockerPull: ttl.sh/eopf-sentinel-2:2h@sha256:...
  EnvVarRequirement:
    envDef: {}
  calrissian:DaskGatewayRequirement:
    workerCores: 1
    workerCoresLimit: 1
    workerMemory: "4G"
    clusterMaxCore: 5
    clusterMaxMemory: "20G"
baseCommand: ["eopf-sentinel-2-proc"]
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
```

## Runtime Behavior

When Calrissian encounters a `DaskGatewayRequirement`, the following workflow is triggered:

- **Cluster Provisioning** - Calrissian connects to the Dask Gateway specified by the CLI flag `--dask-gateway-url` and provisions a Dask cluster matching the requested cores and memory.
- **Tool Execution** - The CommandLineTool is launched with environment variables or context pointing to the Dask cluster (e.g., DASK_SCHEDULER_ADDRESS). This allows the tool to use Dask's distributed scheduler as needed.
- **Cluster Teardown** - Once execution finishes, Calrissian shuts down the Dask cluster, ensuring efficient resource usage.

## CLI Integration

A new CLI option is introduced in Calrissian to support this functionality:

```bash
--dask-gateway-url <URL>
```

**Description:**

Specifies the base URL of the Dask Gateway (e.g., https://dask-gateway.example.com). This option is optional but required when using DaskGatewayRequirement.

### Notes

This extension assumes that the tool being run is compatible with Dask and can use a Dask cluster.

The resource requests (workerCores, workerMemory, etc.) can also be dynamic via CWL expressions.

Error handling for failed cluster creation or shutdown is included in Calrissian’s internal execution flow.

