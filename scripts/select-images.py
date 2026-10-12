"""Select explicit worker/application images for acceptance or release artifacts."""

import argparse
from pathlib import Path

import yaml

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--cloudless", required=True)
parser.add_argument("--eopf", required=True)
args = parser.parse_args()
for path in Path("cwl-workflows").glob("*.cwl"):
    document = yaml.safe_load(path.read_text())
    image = args.cloudless if path.stem == "cloudless-mosaic" else args.eopf
    document["requirements"]["DockerRequirement"]["dockerPull"] = image
    path.write_text(yaml.safe_dump(document, sort_keys=False))
