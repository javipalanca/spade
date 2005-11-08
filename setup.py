#!/usr/bin/env python
import os
from distutils.core import setup
import glob


if os.name == "posix":
	setup(name='SPADE',
	version='1.9.2',
	description='Smart Python multi-Agent Develpment Environment',
	author='Javi Palanca, Miguel Escriva, Gustavo Aranda',
	author_email='jpalanca@dsic.upv.es',
	url='http://gti-ia.dsic.upv.es/projects/magentix/',
	package_dir={'spade': 'spade'},
	packages=['spade', 'spade.xmpp'],
	scripts=['bin/spade-rma.py', 'bin/runspade.py'],
	data_files=[
		('/etc/spade',['etc/spade.xml']),
		('/usr/share/spade',['usr/share/spade/rma.glade']),
		('/usr/share/spade/jabberd',['usr/share/spade/jabberd/jabberd','usr/share/spade/jabberd/jabber.xml']),
		('/usr/share/spade/jabberd/libs',glob.glob('usr/share/spade/jabberd/libs/*.so')),
		('/usr/share/spade/jabberd/spool',['usr/share/spade/jabberd/spool/.spool'])
	]
	)

else:
	import py2exe
	setup(name='SPADE',
	version='1.9.2',
	description='Smart Python multi-Agent Develpment Environment',
	author='Javi Palanca, Miguel Escriva, Gustavo Aranda',
	author_email='jpalanca@dsic.upv.es',
	url='http://gti-ia.dsic.upv.es/projects/magentix/',
	package_dir={'spade': 'spade'},
	packages=['spade', 'spade.xmpp'],
	scripts=['spade-rma.py', 'runspade.py'],
	console=['spade-rma.py', 'runspade.py'],
	data_files=[('etc',['etc/spade.ini','etc/jabber.xml']),('etc',['usr/share/spade/rma.glade'])]
	)
	
