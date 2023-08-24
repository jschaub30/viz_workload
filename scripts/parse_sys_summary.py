#!/usr/bin/env python

'''
Input:  dool file (data/raw directory)
Output: cpu, mem, io, net csv files (data/final directory)
'''

import sys
from datetime import datetime

def main(dool_fn):
    '''
    Read dool file and write individual csv files for cpu, io, memory and
    network.  Use timestamp normalized to the first measured timestamp.
    '''
    with open(dool_fn, 'r') as fid:
        blob = fid.read()
    lines = blob.split('\n')
    scaleGB = 1.0/1024/1024/1024

    monitors = [
        {'name': 'mem', 'columnNames': ["used", "avai", "cach", "free"], 'scale': scaleGB},
        {'name': 'cpu', 'columnNames': ["usr", "sys", "idl", "wai"], 'scale': 1},
        {'name': 'system', 'columnNames': ["int", "csw"], 'scale': 1},
        {'name': 'io', 'columnNames': ["read", "writ"], 'scale': scaleGB},
        {'name': 'net', 'columnNames': ["recv", "send"], 'scale': scaleGB}
    ]
    out_string = {}
    columns = {}
    for monitor in monitors:
        out_string[monitor['name']] = "time," + ','.join(monitor['columnNames']) + '\n'
    timestamp_0 = -1

    start = False
    for line in lines:
        if start and len(line) > 10:
            line = line.split(',')
            timestamp = datetime.strptime(line[0], "%b-%d %H:%M:%S")

            # First normalize timestamp
            if timestamp_0 == -1:
                timestamp_0 = timestamp
            for monitor in monitors:
                cols = columns[monitor['name']]
                data = [str((timestamp - timestamp_0).total_seconds())]
                for i in range(1, len(cols)):
                    data.append(str(round(float(line[cols[i]])*monitor['scale'], 3)))
                out_string[monitor['name']] += ','.join(data) + '\n'
        if "new" in line and "cach" in line:
            start = True
            fields = line.replace('"', '').split(',')
            for monitor in monitors:
                idx = [0]
                for field in monitor['columnNames']:
                    idx.append(fields.index(field))
                columns[monitor['name']] = idx

    # Now write output csv files
    for monitor in monitors:
        out_fn = dool_fn.replace('sys-summary', monitor['name'])
        # write data to data/final directory
        out_fn = out_fn.replace('data/raw', 'data/final') + '.csv'
        #print 'writing ' + out_fn
        with open(out_fn, 'w') as fid:
            fid.write(out_string[monitor['name']])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("USAGE: ./parse_sys_summary.py [dool_filename]\n")
        sys.exit(1)
    main(sys.argv[1])
