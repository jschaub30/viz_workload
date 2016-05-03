#!/usr/bin/python

'''
Input:  dstat file (data/raw directory)
Output: cpu, mem, io, net csv files (data/final directory)
'''

import sys
from datetime import datetime
import numpy as np

def main(dstat_fn):
    '''
    Read dstat file and write individual csv files for cpu, io, memory and
    network.  Use timestamp normalized to the first measured timestamp.
    '''
    with open(dstat_fn, 'r') as fid:
        blob = fid.read()
    lines = blob.split('\n')

    header = {
        'mem': ["used", "buff", "cach", "free"],
        'cpu': ["usr", "sys", "idl", "wai", "hiq", "siq"],
        'io': ["read", "writ"],
        'net': ["recv", "send"]
    }
    columns = {}
    out_string = {}
    for key in header.keys():
        out_string[key] = "time," + ','.join(header[key]) + '\n'
    timestamp_0 = -1

    start = False
    for line in lines:
        if start and len(line) > 10:
            line = line.split(',')
            timestamp = datetime.strptime(line[0], "%d-%m %H:%M:%S")

            # First normalize timestamp
            if timestamp_0 == -1:
                timestamp_0 = timestamp
            line[0] = str((timestamp - timestamp_0).total_seconds())
            line = np.array(line)
            for key in header.keys():
                out_string[key] += ','.join(line[columns[key]]) + '\n'
        if '"new","used"' in line:
            start = True
            fields = line.replace('"', '').split(',')
            for key in header.keys():
                idx = [0]
                for field in header[key]:
                    idx.append(fields.index(field))
                columns[key] = idx

    # Now write output csv files
    for key in header.keys():
        out_fn = dstat_fn.replace('.dstat.csv', '.%s.csv' % key)
        # write data to data/final directory
        out_fn = out_fn.replace('data/raw', 'data/final')
        with open(out_fn, 'w') as fid:
            fid.write(out_string[key])

if __name__ == '__main__':
    main(sys.argv[1])
