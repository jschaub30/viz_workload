#!/usr/bin/python

'''
Input:  dstat file (data/raw directory)
Output: cpu, mem, io, net csv files (data/final directory)
'''

import sys
from datetime import datetime

def scale(val, factor):
    return str(round(float(val) / factor))

def main(dstat_fn):
    '''
    Read dstat file and write individual csv files for cpu, io, memory and
    network.  Use timestamp normalized to the first measured timestamp.
    '''
    with open(dstat_fn, 'r') as fid:
        blob = fid.read()
    lines = blob.split('\n')
    scaleGB = 1.0/1024/1024/1024

    monitors = [
        {'name': 'mem', 'columnNames': ["used", "buff", "cach", "free"], 'scale': scaleGB},
        {'name': 'cpu', 'columnNames': ["usr", "sys", "idl", "wai", "hiq", "siq"], 'scale': 1},
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
            timestamp = datetime.strptime(line[0], "%d-%m %H:%M:%S")

            # First normalize timestamp
            if timestamp_0 == -1:
                timestamp_0 = timestamp
            for monitor in monitors:
                cols = columns[monitor['name']]
                data = [str((timestamp - timestamp_0).total_seconds())]
                for i in range(1, len(cols)):
                    data.append(str(round(float(line[cols[i]])*monitor['scale'], 1)))
                out_string[monitor['name']] += ','.join(data) + '\n'
        if '"new","used"' in line:
            start = True
            fields = line.replace('"', '').split(',')
            for monitor in monitors:
                idx = [0]
                for field in monitor['columnNames']:
                    idx.append(fields.index(field))
                columns[monitor['name']] = idx

    # Now write output csv files
    for monitor in monitors:
        out_fn = dstat_fn.replace('.dstat.csv', '.dstat.%s.csv' % monitor['name'])
        # write data to data/final directory
        out_fn = out_fn.replace('data/raw', 'data/final')
        print 'writing ' + out_fn
        with open(out_fn, 'w') as fid:
            fid.write(out_string[monitor['name']])

if __name__ == '__main__':
    main(sys.argv[1])
