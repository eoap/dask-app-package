"""Validate schema.org metadata with transpiler-mate's actual model.

CWL parsing/extension validation belongs to cwl-docs.py and pinned Calrissian.
The generic cwl2oci loader does not accept mandatory DaskGatewayRequirement.
"""

from pathlib import Path

import yaml
from pyld import jsonld
from transpiler_mate.api import SoftwareApplication

for path in Path("cwl-workflows").glob("*.cwl"):
    document = yaml.safe_load(path.read_text())
    metadata = {key: value for key, value in document.items() if key.startswith("s:")}
    expanded = jsonld.compact(metadata, {}, options={"expandContext": document["$namespaces"]})
    application = SoftwareApplication.model_validate(expanded, by_alias=True)
    assert application.software_version == "2.0.0"
    assert document["s:codeRepository"].rstrip("/") == "https://github.com/eoap/dask-app-package"
    print(f"Validated transpiler-mate metadata model: {path}")
