#!/usr/bin/env python3

'''
Input:  Mellanox Infiniband csv data file (data/raw directory)
Output: Normalized csv file with elapsed time and data in GB (data/final directory)
'''

import sys
from datetime import datetime

def scale(val, factor):
    return str(round(float(val) / factor))

def main(raw_fn):
    '''
    Read raw csv file and write individual csv files for cpu, io, memory and
    network.  Use timestamp normalized to the first measured timestamp.
    '''
    with open(raw_fn, 'r') as fid:
        blob = fid.read()
    lines = blob.split('\n')
    scaleGB = 1.0/1024/1024/1024

    out_string = ''
    column_names = ['time'] + lines.pop(0).split(',')[1:]
    out_string = ','.join(column_names) + '\n'
    t0 = False

    for line in lines:
        if line:
            line = line.split(',')
            time_sec = int(line.pop(0))
            data = [str(round(float(x) * scaleGB,4)) for x in line]
            if not t0:
                t0 = time_sec
            time_sec -= t0
            out_string += ','.join([str(time_sec)] + data) + '\n'
    # write data to data/final directory
    out_fn = raw_fn.replace('data/raw', 'data/final') + '.csv'
    with open(out_fn, 'w') as fid:
        fid.write(out_string)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("USAGE: ./parse_ib.py [raw_filename]\n")
        sys.exit(1)
    main(sys.argv[1])
