#!/bin/bash
# Example script to monitor Mellanox Infiniband network traffic

# Required variables
export WORKLOAD_NAME=EXAMPLES             # A short name for this type of workload
export DESCRIPTION="ib measurement example"
export WORKLOAD_CMD="sleep 20"
export MEASUREMENTS="sys-summary ib"

./run-and-measure.sh

