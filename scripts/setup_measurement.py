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
import pprint

def setup_directories(summary):
    '''
    Setup directory structure
    '''
    for name in ['data/raw', 'data/final', 'scripts']:
        directory = os.path.join(summary['rundir'], name)
        if not os.path.exists(directory):
            os.makedirs(directory)
    symlink = os.path.join('rundir', summary['workload_name'], 'latest')
    try:
        os.remove(symlink)
    except OSError:
        pass
    os.symlink(os.path.basename(summary['rundir']), symlink)

    try:
        shutil.copytree(os.path.join('..', 'app'), 
            os.path.join(summary['rundir'], 'html'))
        shutil.copytree(os.path.join('..', 'bower_components'), 
                os.path.join(summary['rundir'], 'html', 'bower_components'))
    except OSError as e:
        pass   # Raised when a directory already exists (when re-using rundir)

def create_simple(meas_type, run_id):
    '''
    Create top level object for measurement summary
    '''
    obj = {}
    obj['type'] = meas_type
    obj['filename'] = "../data/raw/%s.%s.txt" % (run_id, meas_type)
    return obj

def create_timeseries(run_id, monitor, meas_type, hosts):
    '''
    Create timeseries measurement object with properties for 'hosts' and filenames for
    data from each host
    '''
    obj = {}
    title = ''

    if monitor == 'dstat':
        if meas_type == 'cpu':
            title = 'System CPU [%]'
        elif meas_type == 'mem':
            title = 'Memory [GB]'
        elif meas_type == 'io':
            title = 'IO [GB/sec]'
        elif meas_type == 'net':
            title = 'Network [GB/sec]'

    obj = {
            'type':'timeseries',
            'hosts': hosts,
            'monitor': monitor,
            'title': title
            }
    for host in hosts:
        obj[host] = {}
        obj[host]['rawFilename'] = "../data/raw/%s.%s.%s.%s.txt" % (
            run_id, host, monitor, meas_type)
        obj[host]['finalFilename'] = "../data/final/%s.%s.%s.%s.csv" % (
            run_id, host, monitor, meas_type)
    return obj

def load_environment():
    '''
    Create measurement object based based on environmental variables
    '''
    summary = {}
    # Required environmental variables
    try:
        summary['workload_dir'] = os.environ['WORKLOAD_DIR']
    except KeyError:
        summary['workload_dir'] = os.path.dirname(os.path.realpath(__file__))

    for key in ['WORKLOAD_CMD', 'WORKLOAD_NAME', 'DESCRIPTION']:
        try:
            summary[key.lower()] = os.environ[key].strip('"').strip("'")
        except KeyError:
            sys.stderr.write("%s not found\n" % key)
            sys.exit(1)

    # Optional environmental variables
    try:
        summary['run_id'] = os.environ['RUN_ID']
    except KeyError:
        summary['run_id'] = 'RUN1'

    timestamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    summary['timestamp'] = timestamp
    try:
        rundir = os.environ['RUNDIR']
    except KeyError:
        rundir = os.path.join("rundir", summary['workload_name'], timestamp)
    summary['rundir'] = rundir

    try:
        hosts = os.environ['HOSTS'].split(' ')
        hosts = [h.strip('"').strip("'") for h in hosts]
    except KeyError:
        hosts.append(os.uname()[1].split('.')[0])   # short hostname
    summary['hosts'] = hosts

    return summary

def main():
    '''
    '''
    summary = load_environment()
    # Create directories and copy app
    setup_directories(summary)

    # Add paths to summmary files
    for meas_type in ['time', 'stdout', 'stderr']:
        summary[meas_type] = create_simple(meas_type, summary['run_id'])

    # Write summary.json file
    summary_fn = os.path.join(summary['rundir'], 'html', 'summary.json')
    if os.path.exists(summary_fn):
        # Read and append to existing summary array
        with open(summary_fn, 'r') as fid:
            all_measurements = json.loads(fid.read())
        if summary['run_id'] in [m['run_id'] for m in all_measurements]:
            sys.stderr.write("RUN_ID (%s) is not unique" % summary['run_id'])
            sys.exit(1)
        all_measurements.append(summary)
    else:
        all_measurements = [summary]
    with open(summary_fn, 'w') as fid:
        fid.write(json.dumps(all_measurements, sort_keys=True, indent=4))


    # Write <run_id>.json details file
    details = {}
    for meas_type in ['cpu', 'mem', 'io', 'net']:
        details[meas_type] = create_timeseries(summary['run_id'], 'dstat', 
                meas_type, summary['hosts'])

    detail_fn = os.path.join(summary['rundir'], 'html', summary['run_id'] 
            + '.json')
    with open(detail_fn, 'w') as fid:
        fid.write(json.dumps(details, sort_keys=True, indent=4))


    print summary['rundir']  # Used by the calling shell script

if __name__ == '__main__':
    main()
