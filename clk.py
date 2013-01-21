#!/usr/bin/env python
import sys, os, getopt, md5, re, time, tempfile
from os.path import expanduser

LOCALE=dict()
LOCALE['ioerror']="Unable to open file '%s' for %s"

CONFIG=dict()
CONFIG['file'] = '.clk'

workingPath = os.getcwd()
filePath = '%s/%s' % (workingPath,CONFIG['file'])

def addLine(line):
	try:
		temp = open(filePath,'a+')
	except IOError:
		print LOCALE['ioerror'] % (filePath,'appending')
		sys.exit(1)
	else:
		print 'Clocking %s at %d' % (line,time.time())
		temp.write('%d %s\n' % (time.time(),line))
		temp.close()

def main(argv):
	if len(argv)==0:
		print 'no command'
	elif argv[0] == 'in' or argv[0] == 'out':
		addLine(argv[0])

if __name__=='__main__':
	main(sys.argv[1:])
