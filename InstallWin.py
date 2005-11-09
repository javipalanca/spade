
#!/usr/bin/env python
import os
from distutils.core import setup
import py2exe
import glob


setup(name='SPADE',
	version='1.9.2',
	description='Smart Python multi-Agent Develpment Environment',
	author='Javi Palanca, Miguel Escriva, Gustavo Aranda',
	author_email='jpalanca@dsic.upv.es',
	url='http://gti-ia.dsic.upv.es/projects/magentix/',
	package_dir={'spade': 'spade'},
	packages=['spade', 'spade.xmpp'],
	#scripts=['spade-rma.py', 'runspade.py'],
	console=['spade-rma.py', 'runspade.py'],
	data_files=[
		('etc',['etc/spade.xml']),
		('usr/share/spade',['usr/share/spade/rma.glade']),
		('.',['readme.txt']),
		('doc/private',glob.glob('doc/api/private/*')),
		('doc/public',glob.glob('doc/api/public/*')),
		('doc',['doc/api/index.html','doc/api/epydoc.css']),
		('usr/share/spade/jabberd',['usr/share/spade/jabberd/jabberd.exe','usr/share/spade/jabberd/jabber.xml']),
		('usr/share/spade/jabberd/libs',glob.glob('usr/share/spade/jabberd/libs/*.dll')),
		('usr/share/spade/jabberd/spool',['usr/share/spade/jabberd/spool/.spool'])
	]
)
	
