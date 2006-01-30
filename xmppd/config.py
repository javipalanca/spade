# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# Configuration reader for xmppd.py

# $Id: config.py,v 1.3 2004/10/03 17:47:50 snakeru Exp $

from xmpp import *
import ConfigParser

from string import *
from xml.sax import ContentHandler
from xml.sax import parseString
from xml.sax import make_parser
from xml.sax.handler import *
import os

servernames = []
certificatefile = ''
spoolpath = ''
sslkeyfile = ''

class xmppdXML:
	'''XML streams parser for xmppd'''
        def __init__(self):
                self.ch = xmppdXMLHandler()

        def parseString(self, xmlstream, tag_attr, chars):
                self.ch.tag_attr = tag_attr
                parseString(xmlstream, self.ch)
                return self.ch.tag_name, self.ch.message

class xmppdXMLHandler(ContentHandler):
        def __init__(self):
                self.chars = ""
                self.message = ""
		self.section = ""
                self.current_tag = ""

        def startElement(self, name, attrs):
		global certificatefile
		global spoolpath
                self.chars = ""
                self.tag_name = name
                if name == "server":
                        self.section = "server"
                        #print "Current Tag: " + name
                elif name == "servernames":
                        self.section = "servernames"
                        #print "Current Tag: " + name
                elif name == "name":
                        self.current_tag = "name"
                        #print "Current Tag: " + name
                elif name == "certificate":
                        self.section = "certificate"
			try:
				certificatefile = attrs['file']
			except:
				certificatefile = ''
                        #print "Current Tag: " + name
                elif name == "spool":
                        self.section = "spool"
			try:
				spoolpath = attrs['path']
			except:
				spoolpath = '.'
                        #print "Current Tag: " + name
                else:
                        self.chars = ""
                        self.tag_name = name

        def characters(self, ch):
                self.chars = str(self.chars + ch)

        def endElement(self, name):
                #print 'Final de: ' + name + ' con current_tag: ' + self.current_tag
                #print 'Caracteres : ' + self.chars
                if name == "name":
			servernames.append(self.chars)	
                self.message = self.chars


class Config(PlugIn):
    NS=''
    def __init__(self):
        PlugIn.__init__(self)
        self.DBG_LINE='config'

    def plugin(self,server):
        server.servernames=[]

	# Invoke the parsing
	parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        dh = xmppdXMLHandler()
        parser.setContentHandler(dh)
        parser.parse(server.cfgfile)

        for name in servernames:
            server.servernames.append(name.strip())
	if certificatefile == '':
		server.sslcertfile = None
	else:
		server.sslcertfile = certificatefile
	if sslkeyfile == '':
		server.sslkeyfile = server.sslcertfile
	else:
		server.sslkeyfile = sslkeyfile
	
	# This was good ... for a time
	#server.spoolpath = spoolpath
	server.spoolpath = os.environ['HOME'] + '.xmppd'

