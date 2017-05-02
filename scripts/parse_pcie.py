#!/usr/bin/env python3

'''
I wrote this script as a wrapper around the 'fw_simple_v1.5.py' script,
which expects 2 files to be present in the local directory
- "loadingsample.txt"
- "routesample.txt"
My monitor collects data for these 2 files into 1 raw text file, so the code
below splits the data, runs the 'fw_simple_v1.5.py' script on all data collected,
then records the average utilization and average data size into 2 CSV files
'''
import sys
import os.path
import time
import subprocess
from datetime import datetime

# these are inherited from script 'fw_simple_v1.5.py'
loadingfile="loadingsample.txt"
routefile="routesample.txt"


def parse_header(line):
    '''
    Find columns for each data type
    '''
    line.pop(0)  # good timestamp
    line.pop(0)  # bad timestamp
    util_htod = [i for i, x in enumerate(line) if x.startswith('H')
                 and 'util' in x]
    util_dtoh = [i for i, x in enumerate(line) if x.startswith('D')
                 and 'util' in x]
    size_htod = [i for i, x in enumerate(line) if x.startswith('H')
                 and 'size' in x]
    size_dtoh = [i for i, x in enumerate(line) if x.startswith('D')
                 and 'size' in x]
    return (util_htod, util_dtoh, size_htod, size_dtoh)

def main(raw_fn):
    with open(raw_fn, 'r') as fid:
        blobs = fid.read().split('TIMESTAMP=')
    intermediate_fn = raw_fn + '.sum'
    util_fn = raw_fn.replace('data/raw', 'data/final') + '.util.csv'
    size_fn = raw_fn.replace('data/raw', 'data/final') + '.size.csv'
    
    with open(routefile, 'w') as fid:
        fid.write(blobs.pop(0))
    blob = subprocess.getoutput('python fw_simple_v1.5.py 1') #header
    header = 'datetime,' + blob
    lines = [header]
    for blob in blobs:
        idx = blob.index('\n')
        timestamp = blob[:idx].strip()

        with open(loadingfile, 'w') as fid:
            fid.write(blob[idx:].strip())
        blob = subprocess.getoutput('python fw_simple_v1.5.py')
        line = '{},{}'.format(timestamp, blob)
        lines.append(line)
    with open(intermediate_fn, 'w') as fid:
        fid.write('\n'.join(lines))
    print('Collected data written to {}'.format(intermediate_fn))
    header = lines.pop(0).strip().split(',')
    util_htod, util_dtoh, size_htod, size_dtoh = parse_header(header)
    assert len(util_htod) == len(util_dtoh) == len(size_htod) == len(size_htod)
    data_width = len(util_htod)
    util_str = 'elapsed time,util_htod,util_dtoh\n'
    size_str = 'elapsed time,size_htod,size_dtoh\n'
    t0 = False
    utilization = []
    for line in lines:
        line = line.strip().split(',')
        timestamp = datetime.strptime(line.pop(0), '%Y%m%d-%H%M%S')
        line.pop(0) # bad timestamp
        if not t0:
            t0 = timestamp
        elapsed = (timestamp - t0).seconds
        # Average utilization.  Zero lane if no data, but include in 
        # calculation of mean
        print(line)
        u_htod = sum([float(line[i].strip('%')) if line[i] else 0
                      for i in util_htod]) / data_width
        u_dtoh = sum([float(line[i].strip('%')) if line[i] else 0
                      for i in util_dtoh]) / data_width
        util_str += '{},{:.1f},{:.1f}\n'.format(elapsed, u_htod, u_dtoh)
        # Sum of all data
        print(size_htod)
        for i in size_htod:
            print(line[i])
        s_htod = sum([int(line[i]) for i in size_htod if line[i]])
        s_dtoh = sum([int(line[i]) for i in size_dtoh if line[i]])
        size_str += '{},{:.1f},{:.1f}\n'.format(elapsed, s_htod, s_dtoh)
    # header = [header[i] for i in idx_util]
    with open(util_fn, 'w') as fid:
        fid.write(util_str)
    print('Final pci utilization data written to {}'.format(util_fn))
    with open(size_fn, 'w') as fid:
        fid.write(size_str)
    print('Final pci size data written to {}'.format(size_fn))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('USAGE: {} filename\n'.format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv[1])
 
