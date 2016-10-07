#!/usr/bin/python

'''
Input:  measurement file
Output: json file
'''

import sys
import os
import shutil
import json
import datetime as dt

def create_directories(rundir):
    '''
    Setup directory structure
    '''
    for name in ['data/raw', 'data/final', 'scripts']:
        directory = os.path.join(rundir, name)
        if not os.path.exists(directory):
            os.makedirs(directory)

def main():
    '''
    Create/append measurement object based based on environmental variables
    '''
    meas = {}

    # Required environmental variables
    try:
        meas['workload_dir'] = os.environ['WORKLOAD_DIR']
    except KeyError:
        meas['workload_dir'] = os.path.dirname(os.path.realpath(__file__))

    for key in ['WORKLOAD_CMD', 'WORKLOAD_NAME', 'DESCRIPTION']:
        try:
            meas[key.lower()] = os.environ[key].strip('"').strip("'")
        except KeyError:
            sys.stderr.write("%s not found\n" % key)
            sys.exit(1)

    # Optional environmental variables
    try:
        meas['run_id'] = os.environ['RUN_ID']
    except KeyError:
        meas['run_id'] = 'run1'

    timestamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    meas['timestamp'] = timestamp
    try:
        rundir = os.environ['RUNDIR']
    except KeyError:
        rundir = os.path.join("rundir", meas['workload_name'], timestamp)

    create_directories(rundir)

    try:
        shutil.copytree(os.path.join('..', 'app'), os.path.join(rundir, 'html'))
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    except OSError as e:
        print('Directory not copied. Error: %s' % e)

    try:
        sources = []
        hosts = os.environ['SOURCES'].split(' ')
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
