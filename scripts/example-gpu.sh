#!/bin/bash

# Required variables
export WORKLOAD_NAME=EXAMPLES
export DESCRIPTION="Nvidia host-to-device bandwidthTest example"

# Find the 'bandwidthTest' binary installed on local system
FILES=`find /usr/local/cuda/ -name bandwidthTest`
for FN in $FILES; do
    COUNT=`ls -l $FN | perl -pe "s/[rwx-]+([rwx-]) .*/\1/" | wc -l`
    # directories return COUNT > 1
    if [ $COUNT -eq 1 ]; then
        # check if file is executable
        [ `ls -l $FN | perl -pe "s/[rwx-]+([rwx-]) .*/\1/"` == 'x' ] && \
            FOUND=1 && break
    fi
done

if [ -z $FOUND ]; then
    echo "bandwidthTest binary not found.  You may need to compile this at:"
    echo "$ cd /usr/local/cuda/samples/1_Utilities/bandwidthTest"
    echo "$ sudo make"
    exit 1
fi

export WORKLOAD_CMD="$FN --mode=shmoo"

# Optional variables
export MEASUREMENTS="sys-summary gpu"

export RUNDIR=`./create-rundir.sh`

for ITER in `seq 4`; do
  export RUN_ID="ITER${ITER}"
  ./run-and-measure.sh
done

