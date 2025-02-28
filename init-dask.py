# this code is responsible for creating a Dask cluster
# it's executed by the CWL runner in the context of the Dask Gateway extension
# this is for the prototyping purposes only
import os
import argparse
from loguru import logger
from dask_gateway import Gateway

# read the arguments containing the target file path for the Dask cluster name
parser = argparse.ArgumentParser()
parser.add_argument("--target", type=str, required=True)
parser.add_argument("--gateway-url", type=str, required=True)
parser.add_argument("--image", type=str, required=True)
parser.add_argument("--worker-cores", type=float, required=True, default=0.5)
parser.add_argument("--worker-cores-limit", type=float, required=True, default=1)
parser.add_argument("--worker-memory", type=int, required=True, default=2)
parser.add_argument("--max-cores", type=int, required=True, default=5)
parser.add_argument("--max-ram", type=int, required=True, default=16)
args = parser.parse_args()

target = args.target
gateway_url = args.gateway_url
image = args.image
worker_cores = args.worker_cores
worker_cores_limit = args.worker_cores_limit
worker_memory = args.worker_memory
max_cores = args.max_cores
max_ram = args.max_ram

logger.info(f"Creating Dask cluster and saving the name to {target}")

gateway = Gateway(gateway_url)

cluster_options = gateway.cluster_options()

cluster_options['image'] = image
cluster_options['worker_cores'] = worker_cores
cluster_options['worker_cores_limit'] = worker_cores_limit
cluster_options['worker_memory'] = f"{worker_memory} G"
#cluster_options["worker_extra_pod_labels"] = {"group": "dask"}

logger.info(f"Cluster options: {cluster_options}")
logger.info(dir(cluster_options))
cluster = gateway.new_cluster(cluster_options, shutdown_on_close=False)

# resource requirements
#worker_cores = 0.5
#worker_cores_limit = 1 # would come from DaskGateway.Requirement.ResourceRequirement.worker_cores_limit (or worker_cores)
#worker_memory = 2 # would come from DaskGateway.Requirement.ResourceRequirement.worker_memory
logger.info(f"Resource requirements: {worker_cores} cores, {worker_memory} GB RAM")

# scale cluster
# max_cores = 5 # would come from DaskGateway.Requirement.ResourceRequirement.max_cores
# max_ram = 16  # would come from DaskGateway.Requirement.ResourceRequirement.max_ram
logger.info(f"Resource limits: {max_cores} cores, {max_ram} GB RAM")

workers = int(min(max_cores // worker_cores_limit, max_ram // worker_memory))
logger.info(f"Scaling cluster to {workers} workers")
cluster.scale(workers)


# save the cluster name to a file
with open(target, "w") as f:
    f.write(f"export DASK_CLUSTER={cluster.name}")
logger.info(f"Cluster name {cluster.name} saved to {target}")
