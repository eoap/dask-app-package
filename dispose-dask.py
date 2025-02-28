import time, os, sys
import argparse
from loguru import logger
from dask_gateway import Gateway

# read the arguments containing the target file path for the Dask cluster name
parser = argparse.ArgumentParser()
parser.add_argument("--gateway-url", type=str, required=True)
args = parser.parse_args()

gateway_url = args.gateway_url

# Shut down the Dask cluster
cluster_name = os.environ.get("DASK_CLUSTER")

gateway = Gateway(gateway_url)
cluster = gateway.connect(cluster_name)
logger.info(f"Connected to Dask cluster: {cluster_name}")
cluster.shutdown()
logger.info("Dask cluster shut down successfully.")
sys.exit(0)
