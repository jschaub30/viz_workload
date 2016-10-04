#!/usr/bin/env python

'''
Create json object (string) for measurement
'''

import sys
import os
import getopt
import pprint

def usage():
    ''' Print usage details '''
    print "Usage: create_measurement.py [options] "
    print ""
    print "Options:"
    print "  -r  run_id # string"
    print "  -s  servers  # space or comma separated"
    print "  -d  # Add dstat measurement"
    print "  -h  print help, then exit."
    print ""
    print "Example use:"
    print "./create_measurement.py -r run1 -s host1,host2"
    print "./create_measurement.py -r run1 -s 'host1 host2' -d"
    return

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
    Timeseries measurements add properties for 'sources' and filenames for
    data from each source
    '''
    obj = {}
    for host in hosts:
        obj['type'] = 'timeseries'
        obj['sources'] = hosts
        obj[host] = {}
        obj[host]['rawFilename'] = "data/raw/%s.%s.%s.txt" % (
            run_id, host, meas_type)
        obj[host]['finalFilename'] = "data/final/%s.%s.%s.txt" % (
            run_id, host, meas_type)
    return obj

def main(args):
    '''
    Writes a json measurement object based on measurement file
    '''
    try:
        options, _ = getopt.getopt(args, 'hdr:s:',
                                   ['help', 'dstat', 'run_id', 'servers'])
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    if len(options) == 0:
        usage()
        sys.exit(1)

    dstat = False
    for opt, arg in options:
        if opt == '-r':
            run_id = arg
        elif opt == '-d':
            dstat = True
        elif opt == '-s':
            hosts = arg.replace(' ', ',').split(',')
        elif opt in ('-h', '--help'):
            usage()
            sys.exit(0)

    if not 'run_id' in locals():
        sys.stderr.write('run_id not defined')
        usage()
        sys.exit(1)

    if not 'hosts' in locals():
        hosts = [os.uname()[1].split('.')[0]]   # short hostname

    meas = {}
    for meas_type in ['time', 'stdout', 'stdin']:
        meas[meas_type] = add_simple(meas_type, run_id)

    # Now add dstat measurements
    if dstat:
        for meas_type in ['cpu', 'mem', 'io', 'net']:
            meas[meas_type] = add_timeseries(meas_type, run_id, hosts)
    pprint.pprint(meas)

if __name__ == '__main__':
    main(sys.argv[1:])
