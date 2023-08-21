#!/usr/bin/env python

'''
Input:  environmental variables
        required: 'WORKLOAD_CMD', 'WORKLOAD_NAME', 'DESCRIPTION'
        optional: 'WORKLOAD_DIR', 'RUN_ID', 'SOURCES'
Output: summary (json) file
'''

import sys
import os
import glob
import shutil
import json
import datetime as dt
import collections

def setup_directories(summary):
    '''
    Setup directory structure
    '''
    # Copy app
    try:
        shutil.copytree(os.path.join('..', 'app'),
                        os.path.join(summary['rundir'], 'html'))
    except OSError: # Raised when a directory already exists
        pass

    # Create data directories
    for name in ['data/raw', 'data/final', 'scripts']:
        directory = os.path.join(summary['rundir'], name)
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Copy script files
    directory = os.path.join(summary['rundir'], 'scripts')
    for filename in glob.glob('*.*'):
        shutil.copy(filename, directory)

    # Create 'data' symlink
    symlink = os.path.join(summary['rundir'], 'html', 'data')
    if not os.path.exists(symlink):
        os.symlink('../data', symlink)

    # Create 'latest' symlink
    symlink = os.path.join('rundir', summary['workload_name'], 'latest')
    try:
        os.remove(symlink)  # remove link from last run
    except OSError:
        pass
    os.symlink(os.path.basename(summary['rundir']), symlink)

def create_simple(meas_type, run_id):
    '''
    Create top level object for measurement summary
    '''
    obj = {}
    obj['type'] = meas_type
    obj['filename'] = "../data/raw/%s.%s.txt" % (run_id, meas_type)
    return obj

def create_chartdata(run_id, meas_type, hosts):
    '''
    Populate an object with chart metadata (e.g. title, filenames,
    monitor type, chart type)
    '''
    with open('metadata.json', 'r') as fid:
        metadata = json.load(fid)

    obj = metadata[meas_type]
    obj['hosts'] = hosts

    title = obj['title']
    chart_type = obj['type']

    for host in hosts:
        obj[host] = {}
        obj[host]['rawFilename'] = "../data/raw/%s.%s.%s" % (
            run_id, host, obj['monitor'])
        obj[host]['csvFilename'] = "../data/final/%s.%s.%s.csv" % (
            run_id, host, meas_type)
        if chart_type == 'heatmap':
            obj[host]['jsonFilename'] = "../data/final/%s.%s.%s.json" % (
                run_id, host, meas_type)
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rundir = os.path.join(script_dir, "rundir", summary['workload_name'], timestamp)
    summary['rundir'] = rundir

    try:
        hosts = os.environ['HOSTS'].split(' ')
        hosts = [h.strip('"').strip("'") for h in hosts]
    except KeyError:
        hosts.append(os.uname()[1].split('.')[0])   # short hostname
    summary['hosts'] = hosts

    try:
        summary['all_monitors'] = os.environ['MEASUREMENTS'].strip().split(' ')
    except KeyError:
        sys.stderr.write('MEASUREMENTS not set in environment. Exiting...\n')
        sys.exit(1)

    return summary

def main():
    '''
    Create all directories, save summary object
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
    details = collections.OrderedDict()

    for meas_type in summary['all_monitors']:
        if meas_type == 'sys-summary':
            for meas_type in ['cpu', 'io', 'mem', 'net']:
                details[meas_type] = create_chartdata(summary['run_id'],
                                                      meas_type,
                                                      summary['hosts'])
        elif meas_type == 'gpu':
            for meas_type in ['gpu.avg', 'gpu.pow', 'gpu.gpu', 'gpu.mem']:
                details[meas_type] = create_chartdata(summary['run_id'],
                                                      meas_type,
                                                      summary['hosts'])
        elif meas_type == "interrupts":
            for meas_type in ['system', 'interrupts']:
                details[meas_type] = create_chartdata(summary['run_id'],
                                                      meas_type,
                                                      summary['hosts'])
        elif meas_type == "pcie":
            for suffix in ['ing_util', 'egr_util', 'ing_size', 'egr_size',
                           'd_ing_util', 'd_egr_util', 'd_ing_size',
                           'd_egr_size']:
                meas_type = 'pcie.' + suffix
                details[meas_type] = create_chartdata(summary['run_id'],
                                                      meas_type,
                                                      summary['hosts'])
        elif meas_type == "nvprof":
            for suffix in ['size']:
                meas_type = 'nvprof.' + suffix
                details[meas_type] = create_chartdata(summary['run_id'],
                                                      meas_type,
                                                      summary['hosts'])
        else:
            details[meas_type] = create_chartdata(summary['run_id'],
                                                  meas_type, summary['hosts'])


    detail_fn = os.path.join(summary['rundir'], 'html', summary['run_id']
                             + '.json')
    with open(detail_fn, 'w') as fid:
        fid.write(json.dumps(details, indent=4))


    print(summary['rundir'])  # Used by the calling shell script

if __name__ == '__main__':
    main()
