#!/usr/bin/python

'''
Input:  environmental variables
        required: 'WORKLOAD_CMD', 'WORKLOAD_NAME', 'DESCRIPTION'
        optional: 'WORKLOAD_DIR', 'RUN_ID', 'SOURCES'
Output: summary (json) file
'''

import sys
import os
import shutil
import json
import datetime as dt
import create_measurement
import pprint

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
        meas['run_id'] = 'RUN1'

    timestamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    meas['timestamp'] = timestamp
    try:
        rundir = os.environ['RUNDIR']
    except KeyError:
        rundir = os.path.join("rundir", meas['workload_name'], timestamp)

    create_directories(rundir)
    symlink = os.path.join('rundir', meas['workload_name'], 'latest')
    try:
        os.remove(symlink)
    except OSError:
        pass
    os.symlink(os.path.basename(rundir), symlink)

    try:
        shutil.copytree(os.path.join('..', 'app'), os.path.join(rundir, 'html'))
        shutil.copytree(os.path.join('..', 'bower_components'), 
                os.path.join(rundir, 'html', 'bower_components'))
    except OSError as e:
        pass   # Raised when a directory already exists (when re-using rundir)

    try:
        sources = []
        hosts = os.environ['SOURCES'].split(' ')
        for host in hosts:
            sources.append(host.strip('"').strip("'"))
    except KeyError:
        sources.append(os.uname()[1].split('.')[0])   # short hostname

    meas['sources'] = sources
    summary_fn = os.path.join(rundir, 'html', 'summary.json')
    if os.path.exists(summary_fn):
        with open(summary_fn, 'r') as fid:
            all_measurements = json.loads(fid.read())
        if meas['run_id'] in [m['run_id'] for m in all_measurements]:
            sys.stderr.write("RUN_ID (%s) is not unique" % meas['run_id'])
            sys.exit(1)
        all_measurements.append(meas)
    else:
        all_measurements = [meas]
    with open(summary_fn, 'w') as fid:
        fid.write(json.dumps(all_measurements, sort_keys=True, indent=4))

    # Now create the run_id file that contains measurement details
    args = ['-r', meas['run_id'], '-s', ','.join(sources), '-d']
    details = create_measurement.create_measurement(args)

    detail_fn = os.path.join(rundir, 'html', meas['run_id'] 
            + '.json')
    with open(detail_fn, 'w') as fid:
        fid.write(json.dumps(details, sort_keys=True, indent=4))

    print rundir  # Used by the calling shell script
if __name__ == '__main__':
    main()
