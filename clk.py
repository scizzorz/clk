#!/usr/bin/env python
import sys, os, re, time, datetime
from os.path import expanduser

class ClockLine:
	def __init__(self, match = None, status = None):
		if match is None:
			self.unix_time = 0
			self.date_str = 'none'
			self.time_str = 'none'
			self.status = 'none'
		elif status is not None and match is not None and (type(match) is int or type(match) is float):
			self.unix_time = match
			self.date = datetime.datetime.fromtimestamp(self.unix_time)
			self.date_str = highlight(self.date.strftime(LOCALE['date']), CONFIG['hi_date'])
			self.time_str = highlight(self.date.strftime(LOCALE['time']), CONFIG['hi_time'])
			self.status = status
		else:
			self.unix_time = int(match.group(1))
			self.date = datetime.datetime.fromtimestamp(self.unix_time)
			self.date_str = highlight(self.date.strftime(LOCALE['date']), CONFIG['hi_date'])
			self.time_str = highlight(self.date.strftime(LOCALE['time']), CONFIG['hi_time'])
			self.status = match.group(2)

		if self.status == 'in':
			self.cstatus = highlight(self.status, CONFIG['hi_in'])
		elif self.status == 'out':
			self.cstatus = highlight(self.status, CONFIG['hi_out'])

	def copy(self, copyee):
		self.unix_time = copyee.unix_time
		self.date = copyee.date
		self.date_str = copyee.date_str
		self.time_str = copyee.time_str
		self.status = copyee.status


LOCALE = dict()
LOCALE['ioerror'] = "Unable to open file '%s' for %s"
LOCALE['date'] = '%D'
LOCALE['time'] = '%H:%M'
LOCALE['days'] = '%s days'
LOCALE['hours'] = '%s hours'
LOCALE['minutes'] = '%s minutes'
LOCALE['seconds'] = '%s seconds'
LOCALE['clock'] = 'Clocking %s at %s %s'
LOCALE['currently_working'] = 'Currently clocked in'

CONFIG = dict()
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
RE['line'] = re.compile('^(\d+) (\w+) (.+)$')

working_dir = os.getcwd()
file_path = '%s/%s' % (expanduser('~'), CONFIG['file'])

def highlight(string, color):
	color = int(color)
	# xterm highlighting
	if color < 8:
		color += 30
	else:
		color += 82

	return "\033[%dm%s\033[0m" % (color, string)

def time_to_string(val):
	val = int(val)
	days = val / 86400
	hours = (val % 86400) / 3600
	minutes = (val % 3600) / 60
	seconds = val % 60

	builder = []

	if days > 0:
		builder.append(LOCALE['days'] % highlight(days, CONFIG['hi_days']))

	if hours > 0:
		builder.append(LOCALE['hours'] % highlight(hours, CONFIG['hi_hours']))

	if minutes > 0:
		builder.append(LOCALE['minutes'] % highlight(minutes, CONFIG['hi_minutes']))

	if seconds > 0:
		builder.append(LOCALE['seconds'] % highlight(seconds, CONFIG['hi_seconds']))

	return ', '.join(builder)

def append_line(line):
	try:
		temp = open(file_path,'a+')
	except IOError:
		print LOCALE['ioerror'] % (file_path,'appending')
		sys.exit(1)
	else:
		line = ClockLine(time.time(), line)

		print LOCALE['clock'] % (line.cstatus, line.date_str, line.time_str)

		temp.write('%d %s %s\n' % (time.time(), line, working_dir))
		temp.close()

def read_lines():
	try:
		# see if the file exists before we even try to open it...
		if os.path.exists(file_path):
			temp = open(file_path,'r+')
		else:
			return None
	except IOError:
		print LOCALE['ioerror'] % (file_path, 'reading')
		sys.exit(1)
	else:
		# only get lines that match the regex
		lines = [RE['line'].search(line) for line in temp if RE['line'].search(line)]

		# only get lines that match the working directory
		# and then convert them into a ClockLine object
		lines = [ClockLine(match) for match in lines if match.group(3) == working_dir]

		return lines


def print_lines():
	lines = read_lines()
	for match in lines:
		print '%s %s %s' % (match.date_str, match.time_str, match.cstatus)

def summarize_lines():
	state = 'out'
	current = ClockLine()

	lines = read_lines()
	for match in lines:
		if state != match.status:
			# clocked out at this time, add it up and summarize
			if match.status == 'out':
				print '%s %s until %s %s: %s' % (current.date_str, current.time_str, match.date_str, match.time_str, time_to_string(match.unix_time - current.unix_time))

			# clocked in at this time, reset the last clock position
			elif match.status == 'in':
				current.copy(match)

			# set the current state
			state = match.status

	if state == 'in':
		match = ClockLine(time.time(), 'out')

		print '%s %s %s %s %s: %s' % (current.date_str, current.time_str, highlight('until', CONFIG['hi_now']), match.date_str, match.time_str, time_to_string(match.unix_time - current.unix_time))
		print highlight(LOCALE['currently_working'], CONFIG['hi_now'])

def summarize_days():
	state = 'out'
	current = ClockLine()
	start_key = None

	total_time = 0

	days = dict()

	lines = read_lines()
	for match in lines:
		current_key = match.date.strftime(LOCALE['date'])

		if state != match.status:
			# clocked out at this time, add it up and summarize
			if match.status == 'out':
				if start_key not in days:
					days[start_key] = 0

				days[start_key] += match.unix_time - current.unix_time
				total_time += match.unix_time - current.unix_time

			# clocked in at this time, reset the last clock position
			elif match.status == 'in':
				start_key = current_key
				current.copy(match)

			state = match.status

	if state == 'in':
		match = ClockLine(time.time(), 'out')

		if start_key not in days:
			days[start_key] = 0

		days[start_key] += match.unix_time - current.unix_time
		total_time += match.unix_time - current.unix_time

	for key, val in sorted(days.iteritems()):
		print '%s %s' % (highlight(key, CONFIG['hi_date']), time_to_string(val))

	print '%s %s' % (highlight('total', CONFIG['hi_now']), time_to_string(total_time))

	if state == 'in':
		print highlight(LOCALE['currently_working'], CONFIG['hi_now'])

def print_status():
	state = 'none'

	lines = read_lines()
	for match in lines:
		state = match.status

	print state

def main(argv):
	if len(argv) == 0:
		print_lines()
	elif argv[0] == 'in' or argv[0] == 'out':
		append_line(argv[0])
	elif argv[0] == 'print':
		print_lines()
	elif argv[0] in ('sum', 'summary'):
		summarize_lines()
	elif argv[0] in ('day', 'days', 'daily'):
		summarize_days()
	elif argv[0] in ('st', 'status', 'state'):
		print_status()

if __name__ == '__main__':
	main(sys.argv[1:])
