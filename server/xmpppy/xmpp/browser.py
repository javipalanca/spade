##   browser.py
##
##   Copyright (C) 2004 Alexey "Snake" Nezhdanov
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.

# $Id: browser.py,v 1.6 2004/07/11 19:00:00 snakeru Exp $

from dispatcher import *
from client import PlugIn

class Browser(PlugIn):
    def __init__(self):
        PlugIn.__init__(self)
        DBG_LINE='browser'
        self._exported_methods=[]
        self._handlers={'':{}}

    def plugin(self, owner):
        owner.RegisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_INFO)
        owner.RegisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_ITEMS)

    def plugout(self):
        self._owner.UnregisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_INFO)
        self._owner.UnregisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_ITEMS)

    def _traversePath(self,node,jid,set=0):
        """Returns dictionary and key or None,None
        None - root node (w/o "node" attribute)
        /a/b/c - node
        /a/b/  - branch
        Set returns '' or None as the key
        get returns '' or None as the key or None as the dict"""

        if self._handlers.has_key(jid): cur=self._handlers[jid]
        elif set:
            self._handlers[jid]={}
            cur=self._handlers[jid]
        else: cur=self._handlers['']
        if node is None: node=[None]
        else: node=node.replace('/',' /').split('/')
        for i in node:
            if i<>'' and cur.has_key(i): cur=cur[i]
            elif set and i<>'': cur[i]={dict:cur,str:i}; cur=cur[i]
            elif set or cur.has_key(''): return cur,''
            else: return None,None
        if cur.has_key(1) or set: return cur,1
        raise "Corrupted data"

    def setDiscoHandler(self,handler,node='',jid=''):
        node,key=self._traversePath(node,jid,1)
        node[key]=handler

    def getDiscoHandler(self,node='',jid=''):
        node,key=self._traversePath(node,jid)
        if node: return node[key]

    def delDiscoHandler(self,node='',jid=''):
        node,key=self._traversePath(node,jid)
        if node:
            handler=node[key]
            del node[dict][node[str]]
            return handler

    def _DiscoveryHandler(self,conn,request):
        handler=self.getDiscoHandler(request.getQuerynode(),request.getTo())
        if not handler: return conn.send(Error(request,ERR_ITEM_NOT_FOUND))
        rep=request.buildReply('result')
        q=rep.getTag('query')
        if request.getQueryNS()==NS_DISCO_ITEMS:
            # handler must return list: [{jid,action,node,name}]
            if type(handler)==dict: lst=handler['items']
            else: lst=handler(conn,request,'items')
            for item in lst: q.addChild('item',item)
        elif request.getQueryNS()==NS_DISCO_INFO:
            if type(handler)==dict: dt=handler['info']
            else: lst=handler(conn,request,'info')
            # handler must return dictionary:
            # {'ids':[{},{},{},{}], 'features':[fe,at,ur,es], 'xdata':DataForm}
            for id in dt['ids']: q.addChild('identity',id)
            for feature in dt['features']: q.addChild('feature',{'var':feature})
            if dt.has_key('xdata'): q.addChild(node=dt['xdata'])
        conn.send(rep)
        raise NodeProcessed
