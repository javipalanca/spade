#!/usr/bin/env python
import os
import sys
from distutils.core import setup, Extension
import glob
#if os.name != "posix":
#	import py2exe
try:
	import bdist_mpkg	
except:
	# This is not a mac
	pass

if sys.platform == "win32":
    ext = Extension("tlslite.utils.win32prng",
                    sources=["tlslite/utils/win32prng.c"],
                    libraries=["advapi32"])
    exts = [ext]
else:
    exts = None



if os.name == "posix":
	#if sys.platform != "darwin":
		setup(name='SPADE',
		version='1.9.4',
		description='Smart Python multi-Agent Development Environment',
		author='Javi Palanca, Miguel Escriva, Gustavo Aranda',
		author_email='jpalanca@dsic.upv.es',
		url='http://gti-ia.dsic.upv.es/projects/magentix/',
		package_dir={'spade': 'spade'},
		packages=['spade', 'xmpp', 'xmppd', 'tlslite', 'tlslite.utils', 'tlslite.integration', 'munkware', 'munkware.network'],
		scripts=['spade-rma.py', 'runspade.py',"tlslite/scripts/tls.py", "tlslite/scripts/tlsdb.py"],
		data_files=[
			('/etc/spade',['etc/spade.xml']),
			('/etc/spade',['etc/xmppd.xml']),
			('/usr/share/spade',['usr/share/spade/rma.glade']),
			('/usr/share/doc/spade',['readme.txt']),
			('/usr/share/doc/spade/',['doc/api.tar.gz']),
			#('/usr/share/spade/jabberd',['usr/share/spade/jabberd/jabberd','usr/share/spade/jabberd/jabber.xml']),
			#('/usr/share/spade/jabberd/libs',glob.glob('usr/share/spade/jabberd/libs/*.so')),
			#('/usr/share/spade/jabberd/spool',['usr/share/spade/jabberd/spool/.spool'])
		]
		)

else:
	setup(name='SPADE',
	version='1.9.4',
	description='Smart Python multi-Agent Development Environment',
	author='Javi Palanca, Miguel Escriva, Gustavo Aranda',
	author_email='jpalanca@dsic.upv.es',
	url='http://gti-ia.dsic.upv.es/projects/magentix/',
	package_dir={'spade': 'spade'},
	packages=['spade', 'xmpp', 'xmppd', 'tlslite', 'tlslite.utils', 'tlslite.integration'],
	#scripts=['spade-rma.py', 'runspade.py'],
	console=['spade-rma.py', 'runspade.py','configure.py',"tlslite/scripts/tls.py", "tlslite/scripts/tlsdb.py"],
	data_files=[
		('etc',[]),
		('usr/share/spade',['usr/share/spade/rma.glade']),
		('.',['readme.txt']),
		#('doc/private',glob.glob('doc/api/private/*')),
		#('doc/public',glob.glob('doc/api/public/*')),
		#('doc',['doc/api/index.html','doc/api/epydoc.css']),
		#('usr/share/spade/jabberd',['usr/share/spade/jabberd/jabberd.exe']),
		#('usr/share/spade/jabberd/libs',glob.glob('usr/share/spade/jabberd/libs/*.dll')),
		#('usr/share/spade/jabberd/spool',[])
		('usr/share/spade/xmppd/spool',[])
	],
        ext_modules=exts
	)
	
	
