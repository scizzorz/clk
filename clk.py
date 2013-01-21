#!/usr/bin/env python
import sys, os, getopt, md5, re, time, tempfile, datetime
from os.path import expanduser

LOCALE=dict()
LOCALE['ioerror']="Unable to open file '%s' for %s"
LOCALE['date'] = '%D'
LOCALE['time'] = '%H:%M'
LOCALE['days'] = '%s days'
LOCALE['hours'] = '%s hours'
LOCALE['minutes'] = '%s minutes'
LOCALE['seconds'] = '%s seconds'
LOCALE['clock'] = 'Clocking %s at %s %s'
LOCALE['currently_working'] = 'Currently clocked in'

CONFIG=dict()
CONFIG['file'] = '.clk'

CONFIG['hi_in'] = 11
CONFIG['hi_out'] = 8
CONFIG['hi_date'] = 12
CONFIG['hi_time'] = 13
CONFIG['hi_now'] = 9
CONFIG['hi_days'] = 8
CONFIG['hi_hours'] = 9
CONFIG['hi_minutes'] = 10
CONFIG['hi_seconds'] = 11

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
	val = int(val)
	days = val / 86400
	hours = (val % 86400) / 3600
	minutes = (val % 3600) / 60
	seconds = val % 60

	builder = []

	if days>0:
		builder.append(LOCALE['days'] % hi(days, CONFIG['hi_days']))

	if hours>0:
		builder.append(LOCALE['hours'] % hi(hours, CONFIG['hi_hours']))

	if minutes>0:
		builder.append(LOCALE['minutes'] % hi(minutes, CONFIG['hi_minutes']))

	if seconds>0:
		builder.append(LOCALE['seconds'] % hi(seconds, CONFIG['hi_seconds']))

	return ', '.join(builder)

def addLine(line):
	try:
		temp = open(filePath,'a+')
	except IOError:
		print LOCALE['ioerror'] % (filePath,'appending')
		sys.exit(1)
	else:
		unixTime = time.time()
		dateObj = datetime.datetime.fromtimestamp(unixTime)
		dateString = hi(dateObj.strftime(LOCALE['date']), CONFIG['hi_date'])
		timeString = hi(dateObj.strftime(LOCALE['time']), CONFIG['hi_time'])
		status = line
		if status == 'in':
			status = hi(status, CONFIG['hi_in'])
		elif status == 'out':
			status = hi(status, CONFIG['hi_out'])

		print LOCALE['clock'] % (status, dateString, timeString)

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

def summarizeLines():
	state = 'out'
	startUnix = 0
	startTime = 'none'
	startDate = 'none'
	startStatus = 'none'

	totalTime = 0

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

				thisState = match.group(2)
				if state != thisState:
					if thisState == 'out':
						totalTime += unixTime - startUnix
						print '%s %s until %s %s: %s' % (startDate, startTime, dateString, timeString, timeToString(unixTime - startUnix))
					elif thisState == 'in':
						startUnix = unixTime
						startDate = dateString
						startTime = timeString
						startStatus = status
					state = thisState

	if state == 'in':
		unixTime = time.time()
		dateObj = datetime.datetime.fromtimestamp(unixTime)
		dateString = hi(dateObj.strftime(LOCALE['date']), CONFIG['hi_date'])
		timeString = hi(dateObj.strftime(LOCALE['time']), CONFIG['hi_time'])
		print '%s %s %s %s %s: %s' % (startDate, startTime, hi('until',CONFIG['hi_now']), dateString, timeString, timeToString(unixTime - startUnix))
		print hi(LOCALE['currently_working'], CONFIG['hi_now'])

def summarizeDays():
	state = 'out'
	startUnix = 0
	startKey = None
	startTime = 'none'
	startDate = 'none'
	startStatus = 'none'

	totalTime = 0

	days = dict()

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
				dayKey = dateObj.strftime(LOCALE['date'])
				dateString = hi(dateObj.strftime(LOCALE['date']), CONFIG['hi_date'])
				timeString = hi(dateObj.strftime(LOCALE['time']), CONFIG['hi_time'])

				status = match.group(2)
				if status == 'in':
					status = hi(status, CONFIG['hi_in'])
				elif status == 'out':
					status = hi(status, CONFIG['hi_out'])

				thisState = match.group(2)
				if state != thisState:
					if thisState == 'out':
						if startKey not in days:
							days[startKey] = 0
						days[startKey] += unixTime - startUnix
						totalTime += unixTime - startUnix
					elif thisState == 'in':
						startUnix = unixTime
						startKey = dayKey
						startDate = dateString
						startTime = timeString
						startStatus = status
					state = thisState

	if state == 'in':
		unixTime = time.time()
		if startKey not in days:
			days[startKey] = 0
		days[startKey] += unixTime - startUnix
		totalTime += unixTime - startUnix

	for key, val in sorted(days.iteritems()):
		print '%s %s' % (hi(key, CONFIG['hi_date']), timeToString(val))

	print '%s %s' % (hi('total', CONFIG['hi_now']), timeToString(totalTime))

	if state == 'in':
		print hi(LOCALE['currently_working'], CONFIG['hi_now'])

def main(argv):
	if len(argv)==0:
		printLines()
	elif argv[0] == 'in' or argv[0] == 'out':
		addLine(argv[0])
	elif argv[0] == 'print':
		printLines()
	elif argv[0] in ('sum','summary'):
		summarizeLines()
	elif argv[0] in ('day', 'days', 'daily'):
		summarizeDays()

if __name__=='__main__':
	main(sys.argv[1:])
