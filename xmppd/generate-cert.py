#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

if len(sys.argv) > 1:
    servername = sys.argv[1]
else:
    servername = "server"

cmd = "openssl genrsa -out %s.key 1024" % (servername)
os.system(cmd)
cmd = "openssl req -new -key %s.key -out %s.csr" % (servername, servername)
os.system(cmd)
cmd = "openssl x509 -req -days 999 -in %s.csr -signkey %s.key -out %s.crt" % (servername, servername, servername)
os.system(cmd)
cmd = "cat %s.key %s.crt > %s.pem" % (servername, servername, servername)
os.system(cmd)
cmd = "rm %s.key %s.csr %s.crt" % (servername, servername, servername)
os.system(cmd)
