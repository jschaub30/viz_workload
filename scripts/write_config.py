#!/usr/bin/python

'''
Input:  measurement file
Output: json file
'''

import sys
import os
import json
import datetime as dt


def main(args):
    '''
    Writes a json measurement object based on measurement file
    '''
    meas_fn = args[0]
    with open(meas_fn, 'r') as fid:
        lines = fid.readlines()
    environ = {}
    for line in lines:
          (key, _, value) = line.partition("=")
          environ[key] = value.split('#')[0].strip()
    meas = {}

    try:
        meas['run_id'] = environ['RUN_ID']
    except KeyError:
        meas['run_id'] = 'run1'


    try:
        meas['workload_command'] = environ['WORKLOAD_CMD'].strip('"').strip("'")
    except KeyError:
        sys.stderr.write("WORKLOAD_CMD not found in file %s\n" % meas_fn)
        sys.exit(1)

    try:
        meas['description'] = environ['DESCRIPTION']
    except KeyError:
        sys.stderr.write("DESCRIPTION not found in file %s\n" % meas_fn)
        sys.exit(1)

    meas['timestamp'] = dt.datetime.now().strftime('%Y%m%d-%H%M%S')

    try:
        sources = []
        hosts = environ['HOSTS'].split(' ')
        for host in hosts:
            sources.append(host.strip('"').strip("'"))
    except KeyError:
        sources.append(os.uname()[1].split('.')[0])  # short hostname
    meas['sources'] = sources

    if 'DSTAT' in environ:
        chart_type = 'timeseries'
        cpu = {'chart_type': chart_type}

        data = {}
        for source in sources:
            data[source] = {
                'rawFilename': 'data/raw/%s.%s.dstat.csv' %
                               (meas['run_id'], source),
                'finalFilename': 'data/final/%s.%s.cpu.%s.csv' %
                                 (meas['run_id'], source, chart_type)
            }
        cpu['data'] = data
        meas['cpu'] = cpu
    print json.dumps(meas)


if __name__ == '__main__':
    main(sys.argv[1:])
