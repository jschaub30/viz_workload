#!/bin/bash

[ -z "$WORKLOAD_NAME" ] && echo "WORKLOAD_NAME not defined" && exit 1

CWD=`pwd`
RUNDIR=$CWD/rundir/$WORKLOAD_NAME/$(date +"%Y%m%d-%H%M%S")
mkdir -p $RUNDIR
echo $RUNDIR # DO NOT REMOVE

