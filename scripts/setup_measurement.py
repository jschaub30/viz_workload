#!/usr/bin/python

'''
Input:  measurement file
Output: json file
'''

import sys
import os
import json
import datetime as dt

def create_directories(rundir):
    '''
    Setup directory structure
    '''
    for name in ['data/raw', 'data/final', 'html', 'scripts']:
        directory = os.path.join(rundir, name)
        if not os.path.exists(directory):
            os.makedirs(directory)


def main():
    '''
    Create/append measurement object based based on environmental variables
    '''
    meas = {}

    try:
        meas['run_id'] = os.environ['RUN_ID']
    except KeyError:
        meas['run_id'] = 'run1'

    for key in ['WORKLOAD_CMD', 'WORKLOAD_NAME', 'DESCRIPTION']:
        try:
            meas[key.lower()] = os.environ[key].strip('"').strip("'")
        except KeyError:
            sys.stderr.write("%s not found\n" % key)
            sys.exit(1)

    timestamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    try:
        rundir = os.environ['RUNDIR']
    except KeyError:
        rundir = os.path.join("rundir", meas['workload_name'], timestamp)

    create_directories(rundir)
    meas['timestamp'] = timestamp

    try:
        sources = []
        hosts = os.environ['HOSTS'].split(' ')
        for host in hosts:
            sources.append(host.strip('"').strip("'"))
    except KeyError:
        sources.append(os.uname()[1].split('.')[0])   # short hostname

    meas['sources'] = sources
    config_fn = os.path.join(rundir, 'html', 'measurements.json')
    if os.path.exists(config_fn):
        with open(config_fn, 'r') as fid:
            all_measurements = json.loads(fid.read())
        all_measurements.append(meas)
    else:
        all_measurements = [meas]
    with open(config_fn, 'w') as fid:
        fid.write(json.dumps(all_measurements))

    print rundir

if __name__ == '__main__':
    main()
