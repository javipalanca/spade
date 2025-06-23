#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Implementation of xeps for Internet of Things
# http://wiki.xmpp.org/web/Tech_pages/IoT_systems
# Copyright (C) 2013 Sustainable Innovation, Joachim.lindborg@sust.se
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging

from os.path import basename, join as pjoin
from argparse import ArgumentParser
from urllib import urlopen
from getpass import getpass

import asyncio
import slixmpp
from slixmpp.plugins.xep_0323.device import Device

#from slixmpp.exceptions import IqError, IqTimeout

class IoT_TestDevice(slixmpp.ClientXMPP):

    """
    A simple IoT device that can act as server or client
    """
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.device=None
        self.releaseMe=False
        self.beServer=True
        self.clientJID=None

    def datacallback(self,from_jid,result,nodeId=None,timestamp=None,fields=None,error_msg=None):
        """
        This method will be called when you ask another IoT device for data with the xep_0323
        se script below for the registration of the callback
        """
        logging.debug("we got data %s from %s",str(result),from_jid)

    def beClientOrServer(self,server=True,clientJID=None ):
        if server:
            self.beServer=True
            self.clientJID=None
        else:
            self.beServer=False
            self.clientJID=clientJID

    def testForRelease(self):
        # todo thread safe
        return self.releaseMe

    def doReleaseMe(self):
        # todo thread safe
        self.releaseMe=True

    def addDevice(self, device):
        self.device=device

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        # tell your preffered friend that you are alive
        self.send_message(mto='jocke@jabber.sust.se', mbody=self.boundjid.bare +' is now online use xep_323 stanza to talk to me')

        if not(self.beServer):
            session=self['xep_0323'].request_data(self.boundjid.full,self.clientJID,self.datacallback)

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            logging.debug("got normal chat message" + str(msg))
            ip=urlopen('http://icanhazip.com').read()
            msg.reply("Hi I am " + self.boundjid.full + " and I am on IP " + ip).send()
        else:
            logging.debug("got unknown message type %s", str(msg['type']))

class TheDevice(Device):
    """
    This is the actual device object that you will use to get information from your real hardware
    You will be called in the refresh method when someone is requesting information from you
    """
    def __init__(self,nodeId):
        Device.__init__(self,nodeId)
        self.counter=0

    def refresh(self,fields):
        """
        the implementation of the refresh method
        """
        self._set_momentary_timestamp(self._get_timestamp())
        self.counter+=self.counter
        self._add_field_momentary_data(self, "Temperature", self.counter)

if __name__ == '__main__':

    # Setup the command line arguments.
    #
    # This script can act both as
    #   "server" an IoT device that can provide sensorinformation
    #   python IoT_TestDevice.py -j "serverjid@yourdomain.com" -p "password" -n "TestIoT" --debug
    #
    #   "client" an IoT device or other party that would like to get data from another device

    parser = ArgumentParser()

    # Output verbosity options.
    parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                        action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument("-t", "--pingto", help="set jid to ping",
                        action="store", type="string", dest="pingjid",
                        default=None)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")

    # IoT test
    parser.add_argument("-c", "--sensorjid", dest="sensorjid",
                        help="Another device to call for data on", default=None)
    parser.add_argument("-n", "--nodeid", dest="nodeid",
                        help="I am a device get ready to be called", default=None)

    args = parser.parse_args()

     # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")


    xmpp = IoT_TestDevice(args.jid,args.password)
    xmpp.register_plugin('xep_0030')
    #xmpp['xep_0030'].add_feature(feature='urn:xmpp:iot:sensordata',
    #                             node=None,
    #    jid=None)
    xmpp.register_plugin('xep_0323')
    xmpp.register_plugin('xep_0325')

    if args.nodeid:

        # xmpp['xep_0030'].add_feature(feature='urn:xmpp:sn',
        # node=args.nodeid,
        # jid=xmpp.boundjid.full)

        myDevice = TheDevice(args.nodeid);
        # myDevice._add_field(name="Relay", typename="numeric", unit="Bool");
        myDevice._add_field(name="Temperature", typename="numeric", unit="C")
        myDevice._set_momentary_timestamp("2013-03-07T16:24:30")
        myDevice._add_field_momentary_data("Temperature", "23.4", flags={"automaticReadout": "true"})

        xmpp['xep_0323'].register_node(nodeId=args.nodeid, device=myDevice, commTimeout=10);
        xmpp.beClientOrServer(server=True)
        while not(xmpp.testForRelease()):
            xmpp.connect()
            asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            logging.debug("lost connection")
    if args.sensorjid:
        logging.debug("will try to call another device for data")
        xmpp.beClientOrServer(server=False,clientJID=args.sensorjid)
        xmpp.connect()
        asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
        logging.debug("ready ending")

    else:
       print("noopp didn't happen")
