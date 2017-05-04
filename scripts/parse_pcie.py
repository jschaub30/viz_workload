#!/usr/bin/env python3

'''
I wrote this script as a wrapper around the 'parse_pcie_init.py' script,
which expects 2 files to be present in the local directory
- "loadingsample.txt"
- "routesample.txt"
My monitor collects data for these 2 files into 1 raw text file, so the code
below splits the data, runs the 'parse_pcie_init.py' script on all data collected,
then records the average utilization and average data size into 2 CSV files
'''
import sys
import re
import time
import subprocess
from datetime import datetime

# these are inherited from script 'parse_pcie_init.py'
loadingfile="loadingsample.txt"
routefile="routesample.txt"


def parse_header(line, pattern):
    '''
    Find columns for each data type
    '''
    # line.pop(0)  # good timestamp
    # line.pop(0)  # bad timestamp
    columns = [col for col, label in enumerate(line)
               if re.search(pattern, label)]
    labels = [line[idx] for idx in columns]
    return (columns, labels)

def main(raw_fn):
    with open(raw_fn, 'r') as fid:
        blobs = fid.read().split('TIMESTAMP=')
    intermediate_fn = raw_fn + '.sum'
    base_fn = raw_fn.replace('data/raw', 'data/final')
    host_util_igr_fn = base_fn + '.host_util_igr.csv'
    host_util_egr_fn = base_fn + '.host_util_egr.csv'
    
    with open(routefile, 'w') as fid:
        fid.write(blobs.pop(0))
    header = subprocess.getoutput('python parse_pcie_init.py 1')
    header = 'datetime,' + header
    lines = [header]
    for blob in blobs:
        # strip measurement from file and write to 'loadingsample.txt'
        # then run parse_pcie_init.py
        idx = blob.index('\n')
        timestamp = blob[:idx].strip()

        with open(loadingfile, 'w') as fid:
            fid.write(blob[idx:].strip())
        blob = subprocess.getoutput('python parse_pcie_init.py')
        # now write line after prepending timestamp
        line = '{},{}'.format(timestamp, blob)
        lines.append(line)
    with open(intermediate_fn, 'w') as fid:
        fid.write('\n'.join(lines))
    print('Collected data written to {}'.format(intermediate_fn))
    header = lines.pop(0).strip().split(',')
    suffixes = ['ing_util', 'egr_util', 'ing_size', 'egr_size',
                'd_ing_util', 'd_egr_util', 'd_ing_size', 'd_egr_size']
    for suffix in suffixes:
        fn = '{}.{}.csv'.format(base_fn, suffix)
        if suffix.startswith('d_'):
            pattern = 'D.*' + suffix[2:]
        else:
            pattern = 'H\d+_' + suffix
        columns, labels = parse_header(header, pattern)
        assert len(columns) > 0
        labels = ['elapsed time'] + labels
        t0 = False
        lines_str = ','.join(labels) + '\n'

        for line in lines:
            line = line.strip().split(',')
            timestamp = datetime.strptime(line[0], '%Y%m%d-%H%M%S')
            if not t0:
                t0 = timestamp
            elapsed = str((timestamp - t0).seconds)
            line = [elapsed] + [str(line[idx]) if line[idx] else '0'
                    for idx in columns]
            lines_str += ','.join(line) + '\n'
        with open(fn, 'w') as fid:
            fid.write(lines_str)
        print('Data written to {}'.format(fn))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('USAGE: {} filename\n'.format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv[1])
 
