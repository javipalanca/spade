#!/usr/bin/env python
import os
import sys
from distutils.core import setup, Extension
import glob

from runspade import __version__

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
		version=__version__,
		description='Smart Python multi-Agent Development Environment',
		author='Javier Palanca, Gustavo Aranda, Miguel Escriva, Natalia Criado',
		author_email='jpalanca@gmail.com',
		url='http://spade2.googlecode.com',
		package_dir={'spade': 'spade'},
		#packages=['spade', 'xmpp', 'xmppd', 'xmppd.modules', 'xmppd.locale', 'xmppd.socker', 'tlslite', 'tlslite.utils', 'tlslite.integration'],
		packages=['spade', 'xmpp', 'xmppd', 'xmppd.modules', 'xmppd.socker', 'tlslite', 'tlslite.utils', 'tlslite.integration'],
		#scripts=['spade.sh','gspade.sh','gspade.py', 'runspade.py',"tlslite/scripts/tls.py", "tlslite/scripts/tlsdb.py"],
		scripts=['runspade.py'],#,"tlslite/scripts/tls.py", "tlslite/scripts/tlsdb.py"],
		data_files=[
			('/etc/spade',['etc/spade.xml']),
			('/etc/spade',['etc/xmppd.xml']),
			#('/usr/share/spade',['usr/share/spade/rma.glade']),
			#('/usr/share/spade/mtp',glob.glob('usr/share/spade/mtp/*.py')),
			#('/usr/share/doc/spade',['readme.txt']),
			#('/usr/share/doc/spade/',['doc/api.tar.gz']),
			#('/usr/share/spade/jabberd',['usr/share/spade/jabberd/jabberd','usr/share/spade/jabberd/jabber.xml']),
			#('/usr/share/spade/jabberd/libs',glob.glob('usr/share/spade/jabberd/libs/*.so')),
			#('/usr/share/spade/jabberd/spool',['usr/share/spade/jabberd/spool/.spool'])
		]
		)

else:
	# GUS: What is this case? Meesa not understand :-?

	setup(name='SPADE',
	version=__version__,
	description='Smart Python multi-Agent Development Environment',
	author='Javier Palanca, Gustavo Aranda, Miguel Escriva, Natalia Criado',
	author_email='jpalanca@gmail.com',
	url='http://spade2.googlecode.com',
	package_dir={'spade': 'spade'},
	#packages=['spade', 'xmpp', 'xmppd', 'xmppd.filters', 'tlslite', 'tlslite.utils', 'tlslite.integration'],
	packages=['spade', 'xmpp', 'xmppd', 'xmppd.modules', 'xmppd.socker', 'tlslite', 'tlslite.utils', 'tlslite.integration'],
	#scripts=['spade-rma.py', 'runspade.py'],
	scripts=['runspade.py'],#,"tlslite/scripts/tls.py", "tlslite/scripts/tlsdb.py"],
	#console=['gspade.py', 'runspade.py','configure.py',"tlslite/scripts/tls.py", "tlslite/scripts/tlsdb.py"],
	data_files=[
		('etc',[]),
		#('usr/share/spade',['usr/share/spade/rma.glade']),
		#('.',['readme.txt']),
		#('doc/private',glob.glob('doc/api/private/*')),
		#('doc/public',glob.glob('doc/api/public/*')),
		#('doc',['doc/api/index.html','doc/api/epydoc.css']),
		#('usr/share/spade/jabberd',['usr/share/spade/jabberd/jabberd.exe']),
		#('usr/share/spade/jabberd/libs',glob.glob('usr/share/spade/jabberd/libs/*.dll')),
		#('usr/share/spade/jabberd/spool',[])
		#('usr/share/spade/xmppd/spool',[])
	],
        ext_modules=exts
	)
	
	
