#!/usr/bin/env python

from distutils.core import setup

setup(name='SPADE',
      version='1.9b',
      description='Smart Python multi-Agent Develpment Environment',
      author='Javi Palanca, Miguel Escriva, Gustavo Aranda',
      author_email='jpalanca@dsic.upv.es',
      url='http://gti-ia.dsic.upv.es/projects/magentix/',
      package_dir={'spade': 'spade'},
      packages=['spade'],
      scripts=['spade-rma.py'],
      data_files=[('/etc/spade',['etc/spade.ini','etc/jabber.xml'])]
     )
