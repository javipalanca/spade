#!/usr/bin/python

from agent import *
from select import select

s = []
#~ s = ['servicio1']
a1 = Agent("fa1", "jabber.org")
#a1.addService('ping','services/ping.py')
while(1):
   	print '>>>'
	inputs, outputs, errors = select([sys.stdin], [], [],1)
	line = sys.stdin.readline()
	if line[0] == 'q':
		a1.remove()
		print 'aaaadios'
		sys.exit(0)
	elif line[0] == 's':
		a1.addService('ping','ping.py')
	
