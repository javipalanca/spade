#!/usr/bin/python
# -*- coding: koi8-r -*-
from distutils.core import setup,sys
import os

if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name='xmpppy',
      version='0.2-rc3',
      author='Alexey Nezhdanov',
      author_email='snakeru@users.sourceforge.net',
      url='http://xmpppy.sourceforge.net/',
      description='XMPP-IM-compliant library for jabber instant messenging.',
      long_description="""This library provides functionality for writing xmpp-compliant
jabber clients and/or components.

It was initially designed as rework of jabberpy library but
lately become separate product.

Unlike jabberpy it is distributed under the terms of GPL.""",
      download_url='http://sourceforge.net/project/showfiles.php?group_id=97081',
      packages=['xmpp'],
      license="GPL",
      platforms="All",
      classifiers = [
          'Topic :: Communications :: Chat',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
        ],
     )
