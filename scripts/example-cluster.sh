#!/bin/bash
# This script demonstrates how to run a workload on 2 nodes in a cluster.
# It's recommended that you setup password-less ssh between all
# machines in your cluster prior to running this script.
# and access/view all resulting data from the same web page

# Required variables
export WORKLOAD_NAME=EXAMPLE-CLUSTER      # A short name for this type of workload
export DESCRIPTION="CPU load on 2 nodes"  # A description of this particular workload
export WORKLOAD_CMD="./load_cpu.sh"       # The workload to run

# Optional variables
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay in seconds between each measurement
export VERBOSE=0                    # Verbosity level 0|1|2  Higher==more messages

# To run on hosts other than the local node, export the "SOURCES" variable
# We will simulate this by running on "localhost" and the string returned by "hostname"
export SOURCES="localhost $(hostname)"    # space delimited

./run-and-measure.sh

