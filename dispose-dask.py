import time, os, sys
import argparse
from loguru import logger
from dask_gateway import Gateway

# read the arguments containing the target file path for the Dask cluster name
parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, required=True)
parser.add_argument("--gateway-url", type=str, required=True)
parser.add_argument("--signal", type=str, required=True)
args = parser.parse_args()

source = args.source
gateway_url = args.gateway_url
signal = args.signal

logger.info(f"Sidecar: Waiting for completion signal ({signal}) from main container...")

# Poll for the existence of the completion file
while not os.path.exists(signal):
    logger.info("Sidecar: Waiting for completion signal from main container...")
    time.sleep(5)

logger.info("Sidecar: Completion signal received. Shutting down Dask cluster...")

# Shut down the Dask cluster
cluster_name = os.environ.get("DASK_CLUSTER")

gateway = Gateway(gateway_url)
cluster = gateway.connect(cluster_name)
logger.info(f"Sidecar: Connected to Dask cluster: {cluster_name}")
cluster.shutdown()
logger.info("Sidecar: Dask cluster shut down successfully.")
sys.exit(0)
