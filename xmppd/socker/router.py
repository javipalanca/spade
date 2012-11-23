#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Socker™ network load balancer & reverse proxy dæmon
#
# Copyright (C) 2005 BlueBridge Technologies Group, Inc.
# All rights reserved.
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# [*] Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
# [*] Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
# [*] Neither the name of BlueBridge Technologies nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"Socker™ XMPPD distributer"

__author__ = "Kristopher Tate <kris@bbridgetech.com>"
__version__ = "0.1"
__copyright__ = "Copyright (C) 2005 BlueBridge Technologies Group, Inc."
__license__ = "BSD"


from optparse import OptionParser

parser = OptionParser(version="%%prog %s" % __version__)
parser.add_option("-d", "--debug",
                  action="store_true", dest="enable_debug",
                  help="Enables debug messaging to console")

parser.add_option('-s', "--socker", metavar="host[:ip]", dest="socker_info",
                  help="")

parser.add_option('-t', "--tguid", dest="tguid",
                  help="TGUID to connect with.")

(cmd_options, cmd_args) = parser.parse_args()


from xmpp import *
import time
import sha
import sys
import xmlrpclib

globals()['socker_proxy'] = xmlrpclib.ServerProxy('http://%s' % globals()['cmd_options'].socker_info)

globals()['chain_result'] = globals()['socker_proxy'].getchain({'type_guid': '%s_p5222' % globals()['cmd_options'].tguid})

globals()['clients'] = {}
globals()['channels'] = {}


def readjuster(k, v):
    payload = {'act': 'get', 'type_guid': '%s_p5222' % globals()['cmd_options'].tguid, 'server_guid': v, 'get': ['jid']}
    jids = globals()['socker_proxy'].data(payload)
    if jids['code'] == 1:
        print "[CHANNELGUIDE] %s" % jids['rs']
        globals()['clients'][k]['jids'] = jids['rs']
        for x, y in jids['rs'].iteritems():
            if x in ['__ir__@127.0.0.1']:
                continue  # We don't want to broadcast to ourselves!
            if x not in globals()['channels']:
                globals()['channels'][x] = {}
            for z in y:
                globals()['channels'][x][z] = k


def routerHandler(session, stanza):
    name = stanza.getName()
    to = stanza['to']
    if not to:
        return

    #frm = stanza['from']
    #frm_node=frm.getNode()
    #frm_domain=frm.getDomain()

    barejid, resource = (to.getNode() + '@' + to.getDomain(), to.getResource())

    print "processing request...", name, "::", to, resource  # ,frm
    if to == '__ir__@127.0.0.1/ROUTER':
        raise NodeProcessed

    """if name in ['presence'] and barejid in globals()['channels']:
        print "[BROADCAST:PRESENCE]"
        for value in globals()['clients'].values():
            if barejid in value['jids']: value['cl'].send(stanza)
        raise NodeProcessed"""

    if barejid not in globals()['channels']:
        raise NodeProcessed  # Awww, nowhere to go!

    if resource is None:  # woah, we have to send our stanza to everyone!
        for loc in globals()['channels'][barejid].values():
            if barejid in globals()['clients'][loc]['jids']:
                globals()['clients'][loc]['cl'].send(stanza)
            print "[SENT:M] %s" % loc
    else:
        globals()['clients'][globals()['channels'][barejid][resource]]['cl'].send(stanza)
        print "[SENT:O] %s" % globals()['channels'][barejid][resource]

    raise NodeProcessed


if globals()['chain_result']['code'] == 1:
    for k, v in globals()['chain_result']['chain'].iteritems():
        cl = Client(v['host'], v['port'], None)

        if not cl.connect(server=(v['host'], v['port'])):
            raise IOError('Can not connect to server.')

        if not cl.auth('__ir__', 'test', 'ROUTER'):
            raise IOError('Can not auth with server.')

        cl.Dispatcher.RegisterNamespaceHandler(NS_CLIENT, routerHandler)

        cl.Dispatcher.RegisterNamespaceHandler(NS_SERVER, routerHandler)

        cl.sendInitPresence()

        cl.Process(0.01)

        if not cl.isConnected():
            cl.reconnectAndReauth()
        if cl.isConnected():
            globals()['clients']['%s_%s' % (v['host'], v['port'])] = {'cl': cl, 'sguid': k}
            readjuster('%s_%s' % (v['host'], v['port']), k)

sd = False
last_time = time.time()
while sd is False:
    try:
        if time.time() - last_time >= 5.0:
            globals()['channels'] = {}
            for k, v in globals()['clients'].iteritems():
                readjuster(k, v['sguid'])
            last_time = time.time()
        else:
            for k, v in globals()['clients'].iteritems():
                v['cl'].Process(0.01)
    except KeyboardInterrupt:
        sd = True
