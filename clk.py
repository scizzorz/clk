#!/usr/bin/env python
import sys, os, getopt, md5, re, time, tempfile, datetime
from os.path import expanduser

LOCALE=dict()
LOCALE['ioerror']="Unable to open file '%s' for %s"
LOCALE['date'] = '%D'
LOCALE['time'] = '%H:%M'

CONFIG=dict()
CONFIG['file'] = '.clk'

CONFIG['hi_in'] = 11
CONFIG['hi_out'] = 8
CONFIG['hi_date'] = 2
CONFIG['hi_time'] = 4

RE = dict()
RE['line'] = re.compile('(\d+) (\w+)')

workingPath = os.getcwd()
filePath = '%s/%s' % (workingPath,CONFIG['file'])

def hi(string, color):
	color = int(color)
	# xterm highlighting
	if color<8:
		return "\033[%dm%s\033[0m" % (color+30,string)
	else:
		return "\033[%dm%s\033[0m" % (color+82,string)

def timeToString(val):
	return '%d seconds' % int(val)

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

def printLines():
	try:
		temp = open(filePath,'r+')
	except IOError:
		print LOCALE['ioerror'] % (filePath,'reading')
		sys.exit(1)
	else:
		lines = [line.strip() for line in temp]
		for line in lines:
			match = RE['line'].search(line)
			if match!=None:
				unixTime = int(match.group(1))
				dateObj = datetime.datetime.fromtimestamp(unixTime)
				dateString = hi(dateObj.strftime(LOCALE['date']), CONFIG['hi_date'])
				timeString = hi(dateObj.strftime(LOCALE['time']), CONFIG['hi_time'])

				status = match.group(2)
				if status == 'in':
					status = hi(status, CONFIG['hi_in'])
				elif status == 'out':
					status = hi(status, CONFIG['hi_out'])

				print '%s %s %s' % (dateString, timeString, status)


def main(argv):
	if len(argv)==0:
		print 'no command'
	elif argv[0] == 'in' or argv[0] == 'out':
		addLine(argv[0])
	elif argv[0] == 'print':
		printLines()

if __name__=='__main__':
	main(sys.argv[1:])
