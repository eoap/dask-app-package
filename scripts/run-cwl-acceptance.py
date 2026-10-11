"""Execute both typed application packages through real Calrissian and Dask."""
from pathlib import Path
from datetime import datetime, timezone
import os,json,subprocess,sys,yaml
from urllib.parse import urlparse,unquote
root=Path(__file__).resolve().parents[1]
run=Path('/calrissian/dask-scientific')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
for lesson in ['cloudless-mosaic','eopf-sentinel-2']:
    folder=run/lesson;folder.mkdir(parents=True)
    document=yaml.safe_load((root/'cwl-workflows'/f'{lesson}.cwl').read_text())
    image=os.environ.get('DASK_IMAGE',document['requirements']['DockerRequirement']['dockerPull'])
    document['requirements']['DockerRequirement']['dockerPull']=image
    document['requirements']['ResourceRequirement']={'ramMin':2048,'coresMin':1}
    requirement=document['requirements']['calrissian:DaskGatewayRequirement']
    requirement['clusterMaxCores']=2
    requirement['clusterMaxMemory']='2G'
    requirement['workerMemory']='1G'
    target=folder/'application.cwl';target.write_text(yaml.safe_dump(document,sort_keys=False))
    with (folder/'outputs.json').open('w') as outputs,(folder/'execution.log').open('w') as log:
        subprocess.run(['/opt/calrissian-venv/bin/calrissian','--dask-gateway-url',os.environ['DASK_GATEWAY_ADDRESS'],'--max-ram','4G','--max-cores','2','--pod-serviceaccount','calrissian-sa','--outdir',str(folder/'results'),'--tmp-outdir-prefix',str(folder/'tmp')+'/','--tool-logs-basepath',str(folder/'logs'),'--usage-report',str(folder/'usage.json'),str(target),str(root/'acceptance/jobs'/f'{lesson}.yaml')],stdout=outputs,stderr=log,check=True,env={**os.environ,'CWLTOOL_OPTIONS':''})
    result=json.loads((folder/'outputs.json').read_text())['stac-catalog']
    location=urlparse(result['location']);assert location.scheme=='file',result
    subprocess.run([sys.executable,str(root/'scripts/check-results.py'),'--catalog',str(Path(unquote(location.path))/'catalog.json')],check=True)
    print(f'Accepted typed Calrissian scientific case: {lesson}',flush=True)
