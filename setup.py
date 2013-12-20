#!/usr/bin/env python
import os
import sys
import subprocess
#from distutils.core import setup, Extension
from setuptools import setup, Extension
import glob

from runspade import __version__

#if os.name != "posix":
#   import py2exe
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
    exts = []

with open('README') as file:
    long_description = file.read()

deps = [
    "SPARQLWrapper",
    "unittest-xml-reporting"]
if subprocess.mswindows:
	deps.append( 'pywin32' )

setup(name='SPADE',
    version=__version__,
    license="LGPL",
    description='Smart Python multi-Agent Development Environment',
    long_description=long_description,
    author='Javier Palanca, Gustavo Aranda, Miguel Escriva',
    author_email='jpalanca@gmail.com',
    url='http://spade2.googlecode.com',
    package_dir={'spade': 'spade'},
    packages=['spade','spade.mtps', 'xmpp', 'xmppd', 'xmppd.modules', 'xmppd.socker', 'tlslite', 'tlslite.utils', 'tlslite.integration'],
    scripts=['runspade.py','configure.py'],#,"tlslite/scripts/tls.py", "tlslite/scripts/tlsdb.py"],
    package_data={'spade':['templates/*.*', 'templates/images/*.*'],},
    include_package_data=True,
    ext_modules=exts,
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Topic :: Adaptive Technologies',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    install_requires = deps
    )
    
    
