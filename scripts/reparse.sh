#!/bin/bash
# Run this from the scripts directory in case of problem during data collection

RUNDIR='..'
MEASUREMENTS=`python -c "import json; print(' '.join(json.load(open('../html/summary.json'))[0]['all_monitors']))"`
HOSTS=`python -c "import json; print(' '.join(json.load(open('../html/summary.json'))[0]['hosts']))"`

RUN_IDS=`python -c "import json; print(' '.join([x['run_id'] for x in json.load(open('../html/summary.json'))]))"`
for RUN_ID in $RUN_IDS; do
  export RUN_ID
  for HOST in $HOSTS; do
    for MONITOR in $MEASUREMENTS; do
      echo "Parsing $MONITOR on host $HOST"
      ./parse-monitor.sh $MONITOR $HOST ${RUNDIR}/data/raw
    done
  done
done
