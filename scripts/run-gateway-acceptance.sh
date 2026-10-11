#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
run_dir=/calrissian/dask-acceptance/$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$run_dir"
python - "$root" "$run_dir" <<'PYTHON'
import os,sys,yaml
from pathlib import Path
root,run_dir=map(Path,sys.argv[1:])
document=yaml.safe_load((root/'cwl-workflows/gateway-acceptance.cwl').read_text())
if os.environ.get('DASK_IMAGE'):
    document['requirements']['DockerRequirement']['dockerPull']=os.environ['DASK_IMAGE']
document['requirements']['ResourceRequirement']['coresMin']=0.25
document['requirements']['ResourceRequirement']['coresMax']=1
(run_dir/'gateway-acceptance.cwl').write_text(yaml.safe_dump(document,sort_keys=False))
PYTHON
CWLTOOL_OPTIONS= /opt/calrissian-venv/bin/calrissian --dask-gateway-url "$DASK_GATEWAY_ADDRESS" --max-ram 2G --max-cores 2 --pod-serviceaccount calrissian-sa --outdir "$run_dir/results" --tmp-outdir-prefix "$run_dir/tmp/" --tool-logs-basepath "$run_dir/logs" --usage-report "$run_dir/usage.json" "$run_dir/gateway-acceptance.cwl" > "$run_dir/outputs.json" 2> "$run_dir/execution.log" || { tail -n 60 "$run_dir/execution.log"; exit 1; }
cat "$run_dir/results/report.json"
python - <<'PY'
from dask_gateway import Gateway
import time
with Gateway() as gateway:
    for attempt in range(60):
        if not gateway.list_clusters():
            print('Dask cluster disposal passed')
            break
        time.sleep(1)
    else:
        raise RuntimeError('Dask clusters were not disposed')
PY
