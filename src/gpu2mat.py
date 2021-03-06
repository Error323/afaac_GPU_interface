#!/usr/bin/python
# Program to extract visibility data from the AARTFAAC GPU correlator output
# stream, and write out a .mat file.
# pep/03Jun14

import sys;
import traceback
import numpy;
import os;
import struct;
import scipy.io as sio;

def main ():
	if (len(sys.argv) < 2):
		print 'Usage: ', sys.argv[0], ' rawfile.dat';
		print '       Converts correlated output as generated by AARTFAAC GPU correlator';
		print '       into a .mat file.\n';
		sys.exit (-1);

	nelem  = 288;       
	nrec = 30;
	nbline= nelem*(nelem+1)/2; 
	nchan = 63;
	npol = 4;

	hdrsize = 512;
	recsize = hdrsize + nbline*nchan*npol*2*4; # 4 is for sizeof (float), 2 is for complex float.

	
	# Create an array for every timeslice from all subbands
	tobs = numpy.zeros (nrec, 'd'); # Time of obs, as double
	acm = numpy.zeros ([nrec, nbline, nchan, npol, 2], 'f');
	
	# Output .mat file
#	foutname = sys.argv[1].split('.')[0] + '.mat';
#	print 'Writing to file: ', foutname;
#	if not os.path.isfile (foutname):
#		ffloat = open (foutname, 'wb');
#	else:
#		print '	   ### File exists! Quitting!';
#		sys.exit (-1);
	
	print 'Operating  with : %d pols, %d chans, %d blines' %(npol, nchan, nbline);
	print 'Header/rec size : %d/%d bytes' % (hdrsize, recsize);
	print 'Records per file: %d' % nrec;
	# open file
	try:
		fin = open (sys.argv[1], "rb");
	except IOError:
		print 'File ',sys.argv[1],' does not exist!. Quitting...';
		return -1; 
	
	ind = 0;
	doneRead = 0;
	while doneRead == 0:
		for ind in range (0, nrec):
			# Read in record from file
			rec = fin.read(recsize);
			if not rec: 
				print 'EOF reached. Last few records may be discarded.\n';
		 		doneRead = 1; break;
	
			(magic, pad0, startTime, endTime) = struct.unpack ("<IIdd", rec[0:24]);
			print 'Rec: %04d, Start: %.2f, End: %.2f' % (ind, startTime, endTime);
			tmp = numpy.reshape (numpy.asarray (struct.unpack ("ff"*nbline*nchan*npol, rec[512:])),[nbline, nchan, npol, 2]);

			# Debug section to match rdgpuvis.c output
			# print '%f', startTime;
			# for tind in range (0, nbline):
			#	print '%f %f ' % (tmp[tind][0][0][0], tmp[tind][0][0][1]);
				

			acm [ind] = tmp;
			tobs[ind] = startTime;
			# print 'Type of acm' , type(acm);
			# print 'Shape of array: ', acm.shape;
	
		if ind == 0: # First record of new file is incomplete
			print 'First record corrupt! Not writing this set...';
			break;
		elif ind < nrec-1: # Managed to get some records, but not all
			acm.resize ((ind, nbline,nchan,npol,2));
			print 'Found lesser number of records!';
			fname = '%s_%d-%d.mat'%(sys.argv[1], tobs[0], tobs[ind-1]);
			print 'Writing to file %s.\n' % fname;
		else:
			fname = '%s_%d-%d.mat'%(sys.argv[1], tobs[0], tobs[ind]);
			print 'Writing to file %s.\n' % fname;

		sio.savemat (fname, {'acm':acm, 'tobs':tobs});

	# ffloat.close ();
	fin.close ();
	return;

if __name__ == "__main__":
	main ();
