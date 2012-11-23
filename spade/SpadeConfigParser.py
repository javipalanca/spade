# -*- coding: utf-8 -*-

#import sys
from string import *

from xml.sax import ContentHandler
from xml.sax import parseString
from xml.sax import make_parser
from xml.sax.handler import *


class ParseObject(dict):
        def __getattr__(self, name):
                return self[name]


class spadeXML:
    '''SPADE XML analyzer'''
    def __init__(self):
        self.ch = spadeXMLHandler()

    def parseString(self, xmlstream, tag_attr, chars):
        self.ch.tag_attr = tag_attr
        parseString(xmlstream, self.ch)
        return self.ch.tag_name, self.ch.message


class spadeXMLHandler(ContentHandler):
    def __init__(self):
        self.chars = ""
        self.message = ""
        self.current_tag = ""
        self.current_mtp = ""

    def startDocument(self):

        self.content = ParseObject()

    def startElement(self, name, attrs):
        '''Called when a node starts'''
        self.chars = ""
        self.tag_name = name
        if name == "platform":
            self.current_tag = "platform"
            self.content['platform'] = ParseObject()
            #print "Current Tag: " + name
        elif name == "acc":
            self.current_tag = "acc"
            self.content['acc'] = ParseObject()
            self.content.acc['mtp'] = ParseObject()
            #print "Current Tag: " + name
        elif name == "ams":
            self.current_tag = "ams"
            self.content['ams'] = ParseObject()
            #print "Current Tag: " + name
        elif name == "df":
            self.current_tag = "df"
            self.content['df'] = ParseObject()
            #print "Current Tag: " + name
        elif name == "mtp":
            self.current_tag = attrs.getValue("name")
            self.current_mtp = self.current_tag
            self.content.acc.mtp[self.current_tag] = ParseObject()

        else:
            self.chars = ""
            self.tag_name = name

    def characters(self, ch):
        '''Characters included in a node'''
        self.chars = str(self.chars + ch)

    def endElement(self, name):
        '''Called when a node ends'''
        if name == "hostname":
            if self.current_tag == "platform":
                self.content.platform['hostname'] = self.chars
            elif self.current_tag == "ams":
                self.content.ams['hostname'] = self.chars
            elif self.current_tag == "df":
                self.content.df['hostname'] = self.chars
            elif self.current_tag == "acc":
                self.content.acc['hostname'] = self.chars

        elif name == "password":
            if self.current_tag == "ams":
                self.content.ams['password'] = self.chars
            elif self.current_tag == "df":
                self.content.df['password'] = self.chars
            elif self.current_tag == "acc":
                self.content.acc['password'] = self.chars

        elif name == "port":
            if self.current_tag == "platform":
                self.content.platform['port'] = self.chars
            elif self.current_tag == "ams":
                self.content.ams['port'] = self.chars
            elif self.current_tag == "df":
                self.content.df['port'] = self.chars
            elif self.current_tag == "acc":
                self.content.acc['port'] = self.chars
            else:
                self.content.acc[self.current_tag]['port'] = self.chars

        elif name == "mtp":
                self.current_mtp = ""

        elif name == "protocol":
                self.content.acc["mtp"][self.current_mtp]['protocol'] = self.chars

        #elif name == "address":
        #       self.content.acc[self.current_tag][self.current_mtp]['address'] = self.chars

        elif name == "instance":
                self.content.acc["mtp"][self.current_mtp]['instance'] = self.chars

        elif name == "path":
                self.content.platform["path"] = self.chars

        elif name == "adminpasswd":
                self.content["adminpasswd"] = self.chars


class ConfigParser:

    """def get(self, section, keyword):
        answer = ""
        try:
            d = spade[section]
            answer = d[keyword]
        except:
            print "Section %s does not have keyword %s" % (str(section), keyword)
        return answer"""

    def __init__(self):
            # Create a parser
            self.parser = make_parser()

            # Tell the parser we are not interested in XML namespaces
            self.parser.setFeature(feature_namespaces, 0)

            # Create the handler
            self.dh = spadeXMLHandler()

            # Tell the parser to use our handler
            self.parser.setContentHandler(self.dh)

    def parse(self, fn):

        # Parse the input
        self.parser.parse(fn)

        return self.dh.content
