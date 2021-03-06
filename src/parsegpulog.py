#!/usr/bin/python
""" Script to generate plots of relevant parameters from a log file as 
    generated by the stderr and stdout of the GPU correlator:
	Usage: $ <corr_cmd> 2>&1 | tee output.log
	       $ parsegpulog output.log
	pep/28Oct14
"""

import sys;
import re;
import numpy;
import datetime;
from pylab import *;
import matplotlib.ticker as ticker

keywords = ['exec', 'stats'];
if __name__ == "__main__":
	# print '--> Operating on log file ', sys.argv[1];
	lineno = 0;
	fl_lineno = 0;
	fl_prog = re.compile ('\[(\d+)s, (\d+)\], stats (\d+)-(\d+); flagged: ([-+]?(\d+(\.\d*)?))% \((\d+)\)');
	tim_prog = re.compile ('time: \[(\d+)s, (\d+)\], late: ([-+]?(\d+(\.\d*)?))s, exec: ([-+]?(\d+(\.\d*)?))');
	max_size = 600000;

	tim = numpy.zeros (max_size, dtype=numpy.int);
	t_late = numpy.zeros (max_size, dtype=numpy.float16);
	t_exec = numpy.zeros (max_size, dtype=numpy.float16);
	st_tim = numpy.zeros ((6, max_size), dtype=numpy.float16);
	st_flag = numpy.zeros ((6, max_size), dtype=numpy.float16);

	# with open (sys.argv[1], 'r') as f:
	if sys.argv[1] == '-':
		f = sys.stdin;
	else:
		f = open (sys.argv[1], 'r');

 	for line in f:
		if keywords[0] in line:
			mat = tim_prog.match (line);
			# print 'Extracted: ', int(mat.group(1));
			tim[lineno] = int(mat.group(1));
			t_late[lineno] = float(mat.group(3));
			t_exec[lineno] = float(mat.group(6));
			lineno = lineno+1;

#			strsplit = line.split (',');
#			tim[lineno] = int((strsplit[0].split(':')[1])[2:-1]); # Unix sec
#			t_late = float(strsplit[2].split(':')[1][:-1]);
#			t_exec = float (strsplit[3].split(':')[1][:-1]);

		elif keywords[1] in line:
			# simulate sscanf (line, "[%ds, %d], stats %d-%d; flagged: %d%% (%d)", 
			#                  &unixtim, &bsn, &dip0, &dip1, &flagpercent, &dummy)
			mat = fl_prog.match (line);
			st = int(mat.group(3))/48;
			if st < 0 | st > 6:
				print '### Station: ', st;
			st_tim[st][lineno] = mat.group(1); # Time of this record
			st_flag[st][lineno] = mat.group(5); # % data flagged.
			# print 'St: %d, Tim: %.0f, linno: %d, flag:%.2f'%(st,float(mat.group(1)),lineno,float(mat.group(5)));
			# if st == 5:
		# 		lineno = lineno+1;
			
		else:
			continue;

	print '--> Parsed ', lineno, ' lines.';
	print '--> Start time:', datetime.datetime.fromtimestamp(tim[0]).strftime('%Y-%m-%d %H:%M:%S')
	print '--> End   time:', datetime.datetime.fromtimestamp(tim[lineno-1]).strftime('%Y-%m-%d %H:%M:%S')

	# Start plotting
	fig1 = figure(figsize=(12,6));

	ax = fig1.add_subplot (2,2,1);
	# plot ((tim[1:lineno]-tim[1])/3600.0, t_late[1:lineno]); # Ignore first record
	plot (tim[1:lineno]-tim[1], 'o'); # Ignore first record
	xlabel ('Time (hours from %s)'%(datetime.datetime.fromtimestamp (tim[1])));
	ylabel ('Late');

	ax = fig1.add_subplot (2,2,2);
	n, bins, patches = ax.hist(t_late[1:lineno]);
	ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%.0f')%(y*1e-3)))
	ax.set_xlabel('Late time (sec)');
	ax.set_ylabel('Frequency (000s)');

	subplot (2,2,3);
	plot (tim[1:lineno]/3600, t_exec[1:lineno]);
	xlabel ('Time (hrs from %s)'%(datetime.datetime.fromtimestamp (tim[1])));
	ylabel ('Exec');

	ax = fig1.add_subplot (2,2,4);
	n, bins, patches = ax.hist(t_exec[1:lineno]);
	ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%.0f')%(y*1e-3)))
	ax.set_xlabel('Exec. time (sec)');
	ax.set_ylabel('Frequency (000s)');

	fig1.text (0.5, 0.975, 'Execution and latency per timeslice', horizontalalignment='center', verticalalignment='top');
	plt.tight_layout();

	fig2 = figure(figsize=(12,6));
	st_name = ['CS002', 'CS003', 'CS004', 'CS005', 'CS006', 'CS007'];
	for st in range (0,6):
		subplot (2,6,st+1);
		plot ((tim[1:lineno]-tim[1])/3600.0, st_flag[st][1:lineno]);
		xlabel (st_name[st]);
		# xlabel ('Time (secs from %s)'%(datetime.datetime.fromtimestamp (tim[1])));
		ylabel ('Flag %');

		ax = fig2.add_subplot (2,6,st+7);
		n, bins, patches = ax.hist (st_flag[st][0:lineno]);
		ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%.0f')%(y*1e-3)))
		ax.set_xlabel ('Flag %');
		ax.set_ylabel ('Timeslices (000s)');
	fig2.text (0.5, 0.975, 'Data flagged per station (percent), hrs since %s'%datetime.datetime.fromtimestamp(tim[1]), horizontalalignment='center', verticalalignment='top');
	plt.tight_layout();
	show();
