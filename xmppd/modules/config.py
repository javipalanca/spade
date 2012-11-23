# -*- coding: utf-8 -*-
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# Configuration reader for xmppd.py

# $Id: config.py,v 1.3 2004/10/03 17:47:50 snakeru Exp $

from xmpp import *
#import ConfigParser

#cfgfile='xmppd.cfg'

from string import *
from xml.sax import ContentHandler
from xml.sax import parseString
from xml.sax import make_parser
from xml.sax.handler import *
import os
import copy

servernames = []
administrators = {}
certificatefile = ''
spoolpath = ''
sslkeyfile = ''
#mucjid = ''
#mucname = ''
plugins = {}
components = {}  # Core agents like AMS, DF, ...


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
        self.current_server = ""
        self.current_admins = []

    def startElement(self, name, attrs):
        global certificatefile
        global spoolpath
        global administrators
        global plugins
        global components
        self.chars = ""
        self.tag_name = name
        if self.section == "components":
            try:
                d = dict()
                for k, v in attrs.items():
                    d[str(k)] = str(v)  # De-unicodize
                components[name.lower()] = d
            except:
                pass
        elif self.section == "plugins":  # Server plugins
            try:
                d = dict()
                for k, v in attrs.items():
                    d[str(k)] = str(v)  # De-unicodize
                plugins[name] = d
            except:
                pass
        elif name == "plugins":
            self.section = "plugins"
        elif name == "components":
            self.section = "components"
        elif name == "server":
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
        elif name == "administrators":
            self.section = "administrators"
            #print "Current Tag: " + name
            try:
                self.current_server = attrs['server']
            except:
                self.current_server = ''
        elif name == "admin":
            self.current_tag = "admin"
            try:
                self.current_admins.append(attrs['name'])
            except:
                pass
        else:
            self.chars = ""
            self.tag_name = name

    def characters(self, ch):
        self.chars = str(self.chars + ch)

    def endElement(self, name):
        global mucjid
        global administrators
        #print 'Final de: ' + name + ' con current_tag: ' + self.current_tag
        #print 'Caracteres : ' + self.chars
        if name == "components":
            self.section = ""
        if name == "plugins":
            self.section = ""
        elif name == "name":
            servernames.append(self.chars)
        #elif name == "server":
            # Try to guess muc jid
            #try:
            #	mucjid = "muc." + servernames[0]
            #except:
            #	print "ERROR: Could not find suitable JID for MUC component."
        elif name == "administrators":
            try:
                administrators[self.current_server] = self.current_admins
            except:
                pass
            self.current_admins = []
            self.current_server = ""
            self.section = ""
        self.message = self.chars


class Config(PlugIn):
    NS = ''

    def __init__(self):
        PlugIn.__init__(self)
        self.DBG_LINE = 'config'

    def plugin(self, server):
        global plugins
        global components
        #configfile = ConfigParser.ConfigParser()
        #configfile.add_section('server')
        #configfile.readfp(open('xmppd.cfg','r'))

        #server names
        server.servernames = []
        #server admins
        server.administrators = {}
        try:
            server.sqlite_db = configfile.get('server', 'sqlite_file')
        except:
            server.sqlite_db = None

        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        dh = xmppdXMLHandler()
        parser.setContentHandler(dh)
        parser.parse(server.cfgfile)
        #parser.parse('../etc/xmppd.xml')

        for name in servernames:
            server.DEBUG('server', 'Added new server (%s) from config!' % name.split(), 'info')
            server.servernames.append(name.strip())
            server.administrators.update({name: []})
            #for admin in configfile.get(name,'admins').split(','):

        for name, v in administrators.items():
            for admin in v:
                server.administrators[name].append(admin.strip())
                server.DEBUG('server', 'Added new admin (%s) for server (%s) from config!' % (admin.strip(), name), 'info')

        server.plugins = copy.copy(plugins)
        server.DEBUG('server', 'Added plugins list: %s' % (str(server.plugins)), 'ok')
        server.components = components
        server.DEBUG('server', 'Added components list: ' + str(server.components), 'ok')

        if certificatefile == '':
            server.sslcertfile = None
        else:
            server.sslcertfile = certificatefile
        if sslkeyfile == '':
            server.sslkeyfile = server.sslcertfile
        else:
            server.sslkeyfile = sslkeyfile
