#####
# parser for nvprof
#
# parsing results from something like:
#	 /usr/local/cuda-8.0/bin/nvprof --csv --print-gpu-trace --unified-memory-profiling off 
#	 --profile-child-processes --log-file $HOSTNAME.$OMPI_COMM_WORLD_RANK.%p.csv 
#	 /usr/local/cuda-8.0/samples/1_Utilities/p2pBandwidthLatencyTest/p2pBandwidthLatencyTest
# 
# assumption: start + duration < next start
#
# field: 20 = Name, 18 = P2P Dst, 16 = P2P Src, 13 = Device, 12 = Throughput, 11 = Size, 1 = During, 0 = Start
#        Note: in P2P mode, 13 Device == 18 P2P Dst (discard this now because no similar info in D2D mode)
#
# usage: 
# 	nvprof_parser -t [csv_filename] : generate title line based on csv file, also create a ".nvprof_temp" cache file
# 	nvprof_parser [csv_filename] : parse the csv file, and remove the cache file if exists, output at most 1000 lines
# 	nvprof_parser -c [csv_filename] : parse the csv file, output compressed result with max interval 100ms, error 20%
# 	nvprof_parser -p [err %] [csv_filename] : parse the csv file, output compressed result with max interval 100ms, error [err %]%
# 	nvprof_parser -i [interval] [csv_filename] : parse the csv file, output compressed result with max interval [interval]ms, error 20%
# 	nvprof_parser -i and -p can be used together and using -i and -i will automatically include -p
# 	nvprof_parser -l [linecount] [csv_filename] : parse the csv file, output compressed result with max line count for each event of each gps, the default value is 1000 lines pre event pre gpu
#
# known issue: 
#
# Changelog:
#
# 1.0 5/19/2017: initial release, create cache file when generating title line
# 1.1 5/25/2017: fix and change output format
# 1.2 5/25/2017: group output rate and size together
# 1.3 6/01/2017: result compressing
# 1.4 6/01/2017: output result with specific linecount
# 1.5 6/15/2017: fix output error when not doing result compression
#
# mhchen

from __future__ import print_function
import sys
import os.path
import time
import getopt
import argparse
from collections import defaultdict
import numpy as np
#from sklearn.linear_model import LinearRegression

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

err=0
printTitle=0
csvfile=""

outcount = 1000
ltcount = defaultdict(list) # (gpuIDtypeID, linecount)
cerror=0
cmaxinv=0.1 # default 100ms time gap
rmethod=0 # default is average
smethod=0 # default is time

parser = argparse.ArgumentParser("nvprof_parser")
parser.add_argument("csv_filename", help="Input filename.", type=str)
parser.add_argument("-t", "--title_line", help="Output head line and generate cache.", action="store_true")
parser.add_argument("-c", "--compress_error", help="Precentage of error allowed for compressing data.", action="store_true")
parser.add_argument("-p", "--compress_precentage", type=int, help="Precentage of error allowed for compressing data, automatic include -c.")
parser.add_argument("-i", "--compress_interval", type=int, help="Maximal time interval for compressing data (ms), automatic include -c.")
parser.add_argument("-l", "--output_count", type=int, help="Maximal output line count pre event pre gpu. Require -c")
#parser.add_argument("-s", "--reduce_sample_method", type=int, help="0: time, 1: interval, Require -l")
parser.add_argument("-r", "--reduce_method", type=int, help="0: average, 1: maximal, Require -l")
args = parser.parse_args()

if not args.csv_filename == "":
	csvfile = args.csv_filename
else:
	sys.exit(0)

if args.title_line:
	printTitle=1

if args.output_count > 0:
	outcount=args.output_count

if args.compress_error:
	cerror=0.1 # default 10% error

if args.compress_precentage > 0:
	cerror = args.compress_precentage * 0.01 

if args.reduce_method > 0:
	rmethod = args.reduce_method

#if args.reduce_sample_method > 0:
#	smethod = args.reduce_sample_method

if args.compress_interval > 0:
	cmaxinv = args.compress_interval / 1000
	if cerror == 0:
		cerror=0.1 # default 10% error

try:
	rf = open(csvfile, 'r')
except IOError as e:
	eprint("I/O error({0}): {1}".format(e.errno, e.strerror))
	eprint("Cannot open file: " + csvfile)
	sys.exit(1)
except:
    eprint("Unexpected error:", sys.exc_info()[0])
    raise

devlist = []
devidlist = []
devlinecount = {}
out=""
out2=""

if printTitle ==1: # printTitle, handle 13 for name, type is fixed to h2d d2h d2d p2p
	for i in range(5):
		rs = rf.readline()  # always skip the first 5 line
		if len(rs) < 1: # the csv file is corrupted
			eprint("CSV file is corrupted.\n")
			rf.close()
			sys.exit(1)

	rs = rf.readline().replace("\n", "").split(",")
	while len(rs) > 1:

		typelist=rs[20].split(" ")
		typeid=typelist[len(typelist)-1].lstrip("[").rstrip("]\"")
		if not typeid.isdigit():
			currID = rs[13].lstrip("\"").rstrip("\"") + typeid
			if not currID in devlinecount:
				devlinecount[currID] = 0
#				devlinecount[currID] = 1
#			else:
#				devlinecount[currID] += 1
		
		if not rs[13] in devlist:
			devlist.append(rs[13])
		rs = rf.readline().replace("\n", "").split(",")
	devlist.sort()
	out = "timestamp"
	for h in range(len(devlist)):
		devtmp = devlist[h].rstrip(")\"").split("(")
		devid = devtmp[len(devtmp)-1]
		#out = out + ",GPU" + devid + "_name,GPU" + devid + "_HtoD_size,GPU" + devid + "_HtoD_rate,GPU" + devid + "_DtoH_size,GPU" +  devid + "_DtoH_rate,GPU" + devid + "_DtoD_size,GPU" + devid + "_DtoD_rate,GPU" + devid + "_PtoP_size,GPU"  + devid + "_PtoP_rate"
		out = out + ",GPU" + devid + "_HtoD_size(MB),GPU" + devid + "_DtoH_size(MB),GPU" + devid + "_DtoD_size(MB),GPU" + devid + "_PtoP_size(MB)"
		out2 = out2 + ",GPU" + devid + "_HtoD_rate(GB/s),GPU" +  devid + "_DtoH_rate(GB/s),GPU" + devid + "_DtoD_rate(GB/s),GPU" + devid + "_PtoP_rate(GB/s)"
	print (out + "," + out2)
	rf.close()

	#write cache data
	try:
		cachefile = open(csvfile + ".nvprof_temp", 'w')
	except IOError as e:
		eprint("I/O error({0}): {1}".format(e.errno, e.strerror))
		eprint("Cannot open file: " + csvfile + ".nvprof_temp")
		sys.exit(1)
	except:
		eprint("Unexpected error:", sys.exc_info()[0])
		raise

#	cachefile.write(linecount + "\n")
	cachefile.write(str(len(devlinecount)) + "\n")
	for l in devlinecount.keys():
		cachefile.write(l + "\n")
#		cachefile.write(str(devlinecount[l]) + "\n")

	for h in range(len(devlist)):
		devtmp = devlist[h].rstrip(")\"").split("(")
		devid = devtmp[len(devtmp)-1]
		cachefile.write(devid + "," + devlist[h] + "\n")

	cachefile.close()

else:
	# check if cache exists
	if os.path.isfile(csvfile + ".nvprof_temp"): 
		# load cache: devid, devname
		try:
			cachefile = open(csvfile + ".nvprof_temp", 'r')
		except IOError as e:
			eprint("I/O error({0}): {1}".format(e.errno, e.strerror))
			eprint("Cannot open file: " + csvfile + ".nvprof_temp")
			sys.exit(1)
		except:
			eprint("Unexpected error:", sys.exc_info()[0])
			raise

		devcnt = int(cachefile.readline().replace("\"","").replace("\n",""))
		while devcnt > 0:
			currID = cachefile.readline().replace("\"","").replace("\n","")
			devlinecount[currID] = 0 #int(cachefile.readline().replace("\"","").replace("\n",""))
			devcnt -= 1
		rs = cachefile.readline().replace("\"","").replace("\n","").split(",")
		while len(rs) > 1:
			devidlist.append(rs[0])
			devlist.append(rs[1])
			rs = cachefile.readline().replace("\"","").replace("\n","").split(",")
		cachefile.close()

	else:
		# additional pass to build GPU lists
		for i in range(5):
			rs = rf.readline()  # always skip the first 5 line
			if len(rs) < 1: # the csv file is corrupted
				eprint("CSV file is corrupted.\n")
				rf.close()
				sys.exit(1)

		rs = rf.readline().replace("\n", "").split(",")
		while len(rs) > 1:
			typelist=rs[20].split(" ")
			typeid=typelist[len(typelist)-1].lstrip("[").rstrip("]\"")
			if not typeid.isdigit():
				currID = rs[13].lstrip("\"").rstrip("\"") + typeid
				if not currID in devlinecount:
					devlinecount[currID] = 0
#					devlinecount[currID] = 1
#				else:
#					devlinecount[currID] += 1

			if not rs[13].lstrip("\"").rstrip("\"") in devlist:
				devlist.append(rs[13].lstrip("\"").rstrip("\""))
			rs = rf.readline().replace("\n", "").split(",")
		devlist.sort()
		for h in range(len(devlist)):
			devtmp = devlist[h].rstrip(")\"").split("(")
			devidlist.append(devtmp[len(devtmp)-1])
		rf.seek(0) # reset file reading position

	# generic parsing routine 
	for i in range(5):
		rs = rf.readline()  # always skip the first 5 line
		if len(rs) < 1: # the csv file is corrupted
			eprint("CSV file is corrupted.\n")
			rf.close()
			sys.exit(1)
		
	# for data compress
	currstate = defaultdict(list)
	outcnt = {}
	outputlist = []
	outpos = {}

	rs = rf.readline().replace("\n", "").split(",")
	while len(rs) > 1:
		# check if it is data line
		typelist=rs[20].split(" ")
		typeid=typelist[len(typelist)-1].lstrip("[").rstrip("]\"")
		ts0=float(rs[0]) #* 1000000000.0 #sec
		during=float(rs[1]) #ms
		ts1=(ts0+during/1000) #* 1000000000.0
		size=rs[11] #mb
		throughput=rs[12] #gb/s
		out=""
		out2=""
		doOutput = False # determine if output current result (first line, ts0)
		doOutput2 = False # determine if output current result (second line, ts1)
		outp=""
		outp2=""
		outpts=0
		doOutputPrev = False

		#out = out + ",GPU" + devid + "_HtoD_size(MB),GPU" + devid + "_DtoH_size(MB),GPU" + devid + "_DtoD_size(MB),GPU" + devid + "_PtoP_size(MB)"
		#out2 = out2 + ",GPU" + devid + "_HtoD_rate(GB/s),GPU" +  devid + "_DtoH_rate(GB/s),GPU" + devid + "_DtoD_rate(GB/s),GPU" + devid + "_PtoP_rate(GB/s)"

		if not cerror == 0:
			if not typeid.isdigit(): # HtoD, DtoH, DtoD, PtoP
				if typeid == "HtoD":
					for h in range(len(devlist)):
						if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
							currID = devlist[h] + typeid
							if currID in currstate: # found record, check if need to output and update timestamp
								if ts0 - currstate[currID][0] > cmaxinv or float(size) > (currstate[currID][1] * (1 + cerror)) or float(size) < (currstate[currID][1] * (1 - cerror)) or float(throughput) > (currstate[currID][2] * (1 + cerror)) or float(throughput) < (currstate[currID][2] * (1 - cerror)): # out of the accaptable range of error/time interval, output and remove the entry
									doOutputPrev = True # output last timestamp
									outpts = currstate[currID][0]
									outp = outp + "," + str(currstate[currID][1]) + ",,,"
									outp2 = outp2 + "," + str(currstate[currID][2]) + ",,,"
									doOutput = True # output first new timestamp
									out = out + "," + size + ",,,"
									out2 = out2 + "," + throughput + ",,,"
									currstate[currID] = [ts1, float(size), float(throughput)] #replace the old entry
								else: # update the timestamp of the entry
									currstate[currID][0] = ts1
							else: # first line of the entry, record and output a line
								doOutput = True # output first timestamp
								currstate[currID] = [ts1, float(size), float(throughput)]
								out = out + "," + size + ",,,"
								out2 = out2 + "," + throughput + ",,,"
								outpos[currID] = h * 4
						else:
							out = out + ",,,,"
							out2 = out2 + ",,,,"
							outp = out
							outp2 = out2
				elif typeid == "DtoH":
					for h in range(len(devlist)):
						if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
							currID = devlist[h] + typeid
							if currID in currstate: # found record, check if need to output and update timestamp
								if ts0 - currstate[currID][0] > cmaxinv or float(size) > (currstate[currID][1] * (1 + cerror)) or float(size) < (currstate[currID][1] * (1 - cerror)) or float(throughput) > (currstate[currID][2] * (1 + cerror)) or float(throughput) < (currstate[currID][2] * (1 - cerror)): # out of the accaptable range of error/time interval, output and remove the entry
									doOutputPrev = True # output last timestamp
									outpts = currstate[currID][0]
									outp = outp + ",," + str(currstate[currID][1]) + ",,"
									outp2 = outp2 + ",," + str(currstate[currID][2]) + ",,"
									doOutput = True # output first new timestamp
									out = out + ",," + size + ",,"
									out2 = out2 + ",," + throughput + ",,"
									currstate[currID] = [ts1, float(size), float(throughput)] #replace the old entry
								else: # update the timestamp of the entry
									currstate[currID][0] = ts1
							else: # first line of the entry, record and output a line
								doOutput = True # output first timestamp
								currstate[currID] = [ts1, float(size), float(throughput)]
								out = out + ",," + size + ",,"
								out2 = out2 + ",," + throughput + ",,"
								outpos[currID] = h * 4 +1 
						else:
							out = out + ",,,,"
							out2 = out2 + ",,,,"
							outp = out
							outp2 = out2
				elif typeid == "DtoD":
					for h in range(len(devlist)):
						if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
							currID = devlist[h] + typeid
							if currID in currstate: # found record, check if need to output and update timestamp
								if ts0 - currstate[currID][0] > cmaxinv or float(size) > (currstate[currID][1] * (1 + cerror)) or float(size) < (currstate[currID][1] * (1 - cerror)) or float(throughput) > (currstate[currID][2] * (1 + cerror)) or float(throughput) < (currstate[currID][2] * (1 - cerror)): # out of the accaptable range of error/time interval, output and remove the entry
									doOutputPrev = True # output last timestamp
									outpts = currstate[currID][0]
									outp = outp + ",,," + str(currstate[currID][1]) + ","
									outp2 = outp2 + ",,," + str(currstate[currID][2]) + ","
									doOutput = True # output first new timestamp
									out = out + ",,," + size + ","
									out2 = out2 + ",,," + throughput + ","
									currstate[currID] = [ts1, float(size), float(throughput)] #replace the old entry
								else: # update the timestamp of the entry
									currstate[currID][0] = ts1
							else: # first line of the entry, record and output a line
								doOutput = True # output first timestamp
								currstate[currID] = [ts1, float(size), float(throughput)]
								out = out + ",,," + size + ","
								out2 = out2 + ",,," + throughput + ","
								outpos[currID] = h * 4 + 2
						else:
							out = out + ",,,,"
							out2 = out2 + ",,,,"
							outp = out
							outp2 = out2
				elif typeid == "PtoP": # Note: confirm with ihsin if src dev should be add cuz D2D cannot find src/dst pair
					for h in range(len(devlist)):
						if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
							currID = devlist[h] + typeid
							if currID in currstate: # found record, check if need to output and update timestamp
								if ts0 - currstate[currID][0] > cmaxinv or float(size) > (currstate[currID][1] * (1 + cerror)) or float(size) < (currstate[currID][1] * (1 - cerror)) or float(throughput) > (currstate[currID][2] * (1 + cerror)) or float(throughput) < (currstate[currID][2] * (1 - cerror)): # out of the accaptable range of error/time interval, output and remove the entry
									doOutputPrev = True # output last timestamp
									outpts = currstate[currID][0]
									outp = outp + ",,,," + str(currstate[currID][1])
									outp2 = outp2 + ",,,," + str(currstate[currID][2])
									doOutput = True # output first new timestamp
									out = out + ",,,," + size 
									out2 = out2 + ",,,," + throughput 
									currstate[currID] = [ts1, float(size), float(throughput)] #replace the old entry
								else: # update the timestamp of the entry
									currstate[currID][0] = ts1
							else: # first line of the entry, record and output a line
								doOutput = True # output first timestamp
								currstate[currID] = [ts1, float(size), float(throughput)]
								out = out + ",,,," + size 
								out2 = out2 + ",,,," + throughput 
								outpos[currID] = h * 4 + 3
						else:
							out = out + ",,,,"
							out2 = out2 + ",,,,"
							outp = out
							outp2 = out2
				else: # error?
					eprint("Type error: " + typeid)
					eprint(rs)
					sys.exit(1)
			
		# no compress, always output
		elif not typeid.isdigit(): # HtoD, DtoH, DtoD, PtoP
			doOutput = True
			doOutput2 = True
			if typeid == "HtoD":
				for h in range(len(devlist)):
					if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
						out = out + "," + size + ",,,"
						out2 = out2 + "," + throughput + ",,,"
					else:
						out = out + ",,,,"
						out2 = out2 + ",,,,"
			elif typeid == "DtoH":
				for h in range(len(devlist)):
					if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
						out = out + ",," + size + ",,"
						out2 = out2 + ",," + throughput + ",,"
					else:
						out = out + ",,,,"
						out2 = out2 + ",,,,"
			elif typeid == "DtoD":
				for h in range(len(devlist)):
					if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
						out = out + ",,," + size + ","
						out2 = out2 + ",,," + throughput + ","
					else:
						out = out + ",,,,"
						out2 = out2 + ",,,,"
			elif typeid == "PtoP": # Note: confirm with ihsin if src dev should be add cuz D2D cannot find src/dst pair
				for h in range(len(devlist)):
					if devlist[h] == rs[13].lstrip("\"").rstrip("\""): # the same Device name
						out = out + ",,,," + size 
						out2 = out2 + ",,,," + throughput 
					else:
						out = out + ",,,,"
						out2 = out2 + ",,,,"
			else: # error?
				eprint("Type error: " + typeid)
				eprint(rs)
				sys.exit(1)

		#output the results of two timestamp
		#use the original timestamp now
		if not cerror == 0:
			if doOutputPrev == True:
	#			print (format(outpts, '.9f') + outp + "," + outp2)
				outputlist.append([outpts, outp + outp2, currID])
				devlinecount[currID] += 1
			if doOutput == True:
	#			print (format(ts0, '.9f') + out + "," + out2)
				outputlist.append([ts0, out + out2, currID])
				devlinecount[currID] += 1
			if doOutput2 == True:
	#			print (format(ts1, '.9f') + out + "," + out2)
				outputlist.append([ts1, out + out2, currID])
				devlinecount[currID] += 1
		elif doOutput:
			print (format(ts0, '.9f') + out + out2)
			print (format(ts1, '.9f') + out + out2)

		#time.strftime("%Y%m%d") + str(time.time())

		#else: # no need to record
			#print "skit this item"
		
		rs = rf.readline().replace("\n", "").split(",")


	# check if exceed pre-defined line count pre event pre gpu, if so, force to reduce lines to limitation
	currLine = 0
	devcurrline = {}
	finalline = {}
	if not cerror == 0:
		for k in devlinecount.keys():
			if devlinecount[k] > outcount:
				devlinecount[k] = devlinecount[k] / outcount
				devcurrline[k] = 0
				finalline[k] = 0
			else:
				devlinecount[k] = 0
		outputlist = sorted(outputlist, key=lambda outlist: outlist[0])
		for l in outputlist: #sorted(outputlist, key=lambda outlist: outlist[0]):
			if devlinecount[l[2]] == 0: # directly output
				outputlist[currLine] = [l[0], l[1], l[2]]
				currLine += 1
			else: # compress again
				if rmethod == 0: # average
					rs = l[1].split(",")
					if devcurrline[l[2]] == 0: # initalize
						currstate[l[2]] = [l[0], float(rs[1+outpos[l[2]]]), float(rs[1+outpos[l[2]]+len(devlist)*4])]
						devcurrline[l[2]] = 1
					elif devcurrline[l[2]] < devlinecount[k]: # aggregate more data
						currstate[l[2]] = [l[0]+currstate[l[2]][0], float(rs[1+outpos[l[2]]])+currstate[l[2]][1], float(rs[1+outpos[l[2]]+len(devlist)*4])+currstate[l[2]][2]]
						devcurrline[l[2]] += 1
					else: # generate output
						rs[1+outpos[l[2]]] = currstate[l[2]][1]/devcurrline[l[2]]
						rs[1+outpos[l[2]]+len(devlist)*4] = currstate[l[2]][2]/devcurrline[l[2]]
						rs = ','.join(map(str, rs)) 
						outputlist[currLine] = [currstate[l[2]][0]/devcurrline[l[2]], rs, l[2]]
						currLine += 1
						finalline[l[2]] += 1
						devcurrline[l[2]] = 0
				elif rmethod == 1: # maximal
					rs = l[1].split(",")
					if devcurrline[l[2]] == 0: # initalize
						currstate[l[2]] = [l[0], float(rs[1+outpos[l[2]]]), float(rs[1+outpos[l[2]]+len(devlist)*4])]
						devcurrline[l[2]] = 1
					elif devcurrline[l[2]] < devlinecount[k]: # aggregate more data
						currstate[l[2]][0] = l[0]+currstate[l[2]][0]
						if float(rs[1+outpos[l[2]]]) > currstate[l[2]][1]:
							currstate[l[2]][1] = float(rs[1+outpos[l[2]]])
						if float(rs[1+outpos[l[2]]+len(devlist)*4]) > currstate[l[2]][2]:
							currstate[l[2]][2] = float(rs[1+outpos[l[2]]+len(devlist)*4])
						devcurrline[l[2]] += 1
					else: # generate output
						rs[1+outpos[l[2]]] = currstate[l[2]][1]
						rs[1+outpos[l[2]]+len(devlist)*4] = currstate[l[2]][2]
						rs = ','.join(map(str, rs)) 
						outputlist[currLine] = [currstate[l[2]][0]/devcurrline[l[2]], rs, l[2]]
						currLine += 1
						finalline[l[2]] += 1
						devcurrline[l[2]] = 0
		#clean up
		for i in range(len(rs)):
			rs[i]=""
		ers=rs
		for k in devcurrline.keys():
			if not devcurrline[k] == 0:
				if rmethod == 0:
					ers[1+outpos[k]] = currstate[k][1]/devcurrline[k]
					ers[1+outpos[k]+len(devlist)*4] = currstate[k][2]/devcurrline[k]
					ers = ','.join(map(str, ers)) 
					outputlist[currLine] = [currstate[k][0]/devcurrline[k], ers, k]
					currLine += 1
					finalline[k] += 1
					devcurrline[k] = 0
					ers=rs
					ers[1+outpos[k]] = ""
					ers[1+outpos[k]+len(devlist)*4] = ""
				elif rmethod == 1: #maximal
					ers[1+outpos[k]] = currstate[k][1]
					ers[1+outpos[k]+len(devlist)*4] = currstate[k][2]
					ers = ','.join(map(str, ers)) 
					outputlist[currLine] = [currstate[k][0]/devcurrline[k], ers, k]
					currLine += 1
					finalline[k] += 1
					devcurrline[k] = 0
					ers=rs
					ers[1+outpos[k]] = ""
					ers[1+outpos[k]+len(devlist)*4] = ""

		outputlist[0:currLine] = sorted(outputlist[0:currLine], key=lambda outlist: outlist[0])
		for i in range(currLine):
			print (format(outputlist[i][0], '.9f') + outputlist[i][1])
#		print (finalline)

#		for l in sorted(outputlist, key=lambda outlist: outlist[0]):
			#print (format(l[0], '.9f') + l[1])

	rf.close()

	# remove cache file
	if os.path.isfile(csvfile + ".nvprof_temp"): 
		os.remove(csvfile + ".nvprof_temp")
