#!/usr/bin/env python

'''
Input:  run id, comma separated hosts array, comma separated measurement array
Output: json string

Example:
$ ./create_measurement.py run1 host1,host2 time,stdout,stderr,dstat
'''

import sys
import json

def add_simple(meas_type, run_id):
    '''
    Simple measurements have properties "type", and "rawFilename"
    '''
    obj = {}
    obj['type'] = meas_type
    obj['rawFilename'] = "data/raw/%s.%s.txt" % (run_id, meas_type)
    return obj

def add_timeseries(meas_type, run_id, hosts):
    '''
    Timeseries measurements add 'sources' and contain data for each source
    '''
    obj = {}
    for host in hosts:
        obj['type'] = 'timeseries'
        obj['sources'] = hosts
        obj[host] = {}
        obj[host]['rawFilename'] = "data/raw/%s.%s.%s.txt" % (run_id,
        host, meas_type)
        obj[host]['finalFilename'] = "data/final/%s.%s.%s.txt" % (run_id,
        host, meas_type)
    return obj

def add_dstat(measurement, run_id, hosts):
    '''
    Add timeseries for 'cpu', 'mem', 'io', and 'net' to existing measurement
    '''


def main(args):
    '''
    Writes a json measurement object based on measurement file
    '''
    run_id = args[0]
    hosts = args[1].split(',')
    if len(args) > 2:
        measurements = args[2].split(',')
    else:
        measurements = ['dstat']
    m = {}
    for meas_type in ['time', 'stdout', 'stdin']:
        m[meas_type] = add_simple(meas_type, run_id)

    # Now add dstat measurements
    if 'dstat' in measurements:
        for meas_type in ['cpu', 'mem', 'io', 'net']:
            m[meas_type] = add_timeseries(meas_type, run_id, hosts)
    print(m)
    json.dumps(m)

if __name__ == '__main__':
    main(sys.argv[1:])
