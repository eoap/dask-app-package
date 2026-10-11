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

## Use the course packages

The standalone tools in `cwl-workflows/` contain the complete metadata, typed
inputs and required execution definitions. Generate their current reference
with `python scripts/cwl-docs.py`; do not copy an obsolete workflow example.
`clusterMaxCores` is plural. Worker core fields require integers in the pinned
extension schema; the upstream implementation does not evaluate expressions
in those fields. Notebook gateway options independently permit fractional CPU
requests.

Calrissian provisions an init container, a main processing container and a
cluster-disposal sidecar. The pinned implementation repeats the main container's
resource reservations for the sidecar. Acceptance requests a quarter core for
each controller container, allows a one-core burst, uses a quarter-core gateway
scheduler, and keeps two whole-core workers. Scientific controller RAM is 2 GiB;
source packages retain the larger full-workload defaults.

A successful cleanup sidecar does not prove scientific processing succeeded.
The scientific CWL output contract rejects a missing root `catalog.json`, and
acceptance opens all raster assets and checks their georeferencing and values.

Use upstream Calrissian from the PDE isolated environment, or the same immutable
commit in `requirements-validation.txt`. `scripts/run-gateway-acceptance.sh`
checks real distributed computation and disposal; `scripts/run-cwl-acceptance.py`
executes the two typed scientific jobs. Both select the tested application image
explicitly. The images include matching Python 3.12 scheduler/worker commands.

The mandatory custom requirement remains under `requirements`, not optional
`hints`. Generic cwl2oci parsing currently does not support this extension;
actual transpiler-mate metadata validation runs in a separate locked environment.
No packing command is used.
