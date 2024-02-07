#!/bin/bash
# 2 node demo showing typical metrics (sys-summary) and adding CPU heatmap
# cpu-heatmap and interrupts

# Required variables are WORKLOAD_NAME, DESCRIPTION, & WORKLOAD_CMD
export WORKLOAD_NAME=EXAMPLES        # A short name for this type of workload
export DESCRIPTION="Disk write --> cpu --> disk read workload on 2 hosts"  # A description of this particular workload
export MEASUREMENTS="cpu-heatmap sys-summary"

HOSTS="moose,lynx"
export HOSTS

RUNDIR=$(./create-rundir.sh)
export RUNDIR

export WORKLOAD_CMD="./mixed-workload.sh $HOSTS"   # The workload to run
./run-and-measure.sh
