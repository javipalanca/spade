##   features.py 
##
##   Copyright (C) 2003-2004 Alexey "Snake" Nezhdanov
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

# $Id: features.py,v 1.18 2004/10/08 19:01:39 snakeru Exp $

from protocol import *

### DISCO ### http://jabber.org/protocol/disco ### JEP-0030 ####################
### Browse ### jabber:iq:browse ### JEP-0030 ###################################
### Agents ### jabber:iq:agents ### JEP-0030 ###################################
def _discover(disp,ns,jid,node=None,fb2b=0,fb2a=1):
    iq=Iq(to=jid,typ='get',queryNS=ns)
    if node: iq.setAttr('node',node)
    rep=disp.SendAndWaitForResponse(iq)
    if fb2b and not isResultNode(rep): rep=disp.SendAndWaitForResponse(Iq(to=jid,typ='get',queryNS=NS_BROWSE))   # Fallback to browse
    if fb2a and not isResultNode(rep): rep=disp.SendAndWaitForResponse(Iq(to=jid,typ='get',queryNS=NS_AGENTS))   # Fallback to agents
    if isResultNode(rep): return rep.getQueryPayload()
    return []

def discoverItems(disp,jid,node=None):
    """ According to JEP-0030:
        query MAY have node attribute
        item: MUST HAVE jid attribute and MAY HAVE name, node, action attributes.
        action attribute of item can be either of remove or update value."""
    ret=[]
    for i in _discover(disp,NS_DISCO_ITEMS,jid,node):
        if i.getName()=='agent' and i.getTag('name'): i.setAttr('name',i.getTagData('name'))
        ret.append(i.attrs)
    return ret

def discoverInfo(disp,jid,node=None):
    """ According to JEP-0030:
        query MAY have node attribute
        identity: MUST HAVE category and name attributes and MAY HAVE type attribute.
        feature: MUST HAVE var attribute"""
    identities , features = [] , []
    for i in _discover(disp,NS_DISCO_INFO,jid,node):
        if i.getName()=='identity': identities.append(i.attrs)
        elif i.getName()=='feature': features.append(i.getAttr('var'))
        elif i.getName()=='agent':
            if i.getTag('name'): i.setAttr('name',i.getTagData('name'))
            if i.getTag('description'): i.setAttr('name',i.getTagData('description'))
            identities.append(i.attrs)
            if i.getTag('groupchat'): features.append(NS_GROUPCHAT)
            if i.getTag('register'): features.append(NS_REGISTER)
            if i.getTag('search'): features.append(NS_SEARCH)
    return identities , features

### Registration ### jabber:iq:register ### JEP-0077 ###########################
def getRegInfo(disp,host,info={}):
    """Gets registration blank from host.
       disp must be connected dispatcher instance."""
    iq=Iq('get',NS_REGISTER,to=host)
    for i in info.keys(): iq.setTagData(i,info[i])
    resp=disp.SendAndWaitForResponse(iq)
    if not isResultNode(resp): return
    df=resp.getTag('query',namespace=NS_REGISTER).getTag('x',namespace=NS_DATA)
    if df: return DataForm(node=df)
    df=DataForm(typ='form')
    for i in resp.getQueryPayload():
        if i.getName()=='instructions': df.addInstructions(i.getData())
        else: df.setField(i.getName()).setValue(i.getData())
    return df

def register(disp,host,info):
    """Registrates on host with provided info.
       disp must be connected dispatcher instance."""
    iq=Iq('set',NS_REGISTER,to=host)
    if type(info)<>type({}): info=info.asDict()
    for i in info.keys(): iq.setTag('query').setTagData(i,info[i])
    resp=disp.SendAndWaitForResponse(iq)
    if isResultNode(resp): return 1

def unregister(disp,host):
    """Unregisters with host.
       disp must be connected and authorized dispatcher instance."""
    resp=disp.SendAndWaitForResponse(Iq('set',NS_REGISTER,to=host,payload=[Node('remove')]))
    if isResultNode(resp): return 1

def changePasswordTo(disp,newpassword,host=None):
    """Changes password on specified or current (if not specified) server.
       disp must be connected and authorized dispatcher instance."""
    if not host: host=disp._owner.Server
    resp=disp.SendAndWaitForResponse(Iq('set',NS_REGISTER,to=host,payload=[Node('username',payload=[disp._owner.Server]),Node('password',payload=[newpassword])]))
    if isResultNode(resp): return 1

### Privacy ### jabber:iq:privacy ### draft-ietf-xmpp-im-19 ####################
#type=[jid|group|subscription]
#action=[allow|deny]

def getPrivacyLists(disp):
    try:
        dict={'lists':[]}
        resp=disp.SendAndWaitForResponse(Iq('get',NS_PRIVACY))
        if not isResultNode(resp): return
        for list in resp.getQueryPayload():
            if list.getName()=='list': dict['lists'].append(list.getAttr('name'))
            else: dict[list.getName()]=list.getAttr('name')
        return dict
    except: pass

def getPrivacyList(disp,listname):
    try:
        resp=disp.SendAndWaitForResponse(Iq('get',NS_PRIVACY,payload=[Node('list',{'name':listname})]))
        if isResultNode(resp): return resp.getQueryPayload()[0]
    except: pass

def setActivePrivacyList(disp,listname=None,typ='active'):
    if listname: attrs={'name':listname}
    else: attrs={}
    resp=disp.SendAndWaitForResponse(Iq('set',NS_PRIVACY,payload=[Node(typ,attrs)]))
    if isResultNode(resp): return 1

def setDefaultPrivacyList(disp,listname=None): return setActivePrivacyList(disp,listname,'default')

def setPrivacyList(disp,payload):
    resp=disp.SendAndWaitForResponse(Iq('set',NS_PRIVACY,payload=[payload]))
    if isResultNode(resp): return 1

def delPrivacyList(disp,listname):
    resp=disp.SendAndWaitForResponse(Iq('set',NS_PRIVACY,payload=[Node('list',{'name':listname})]))
    if isResultNode(resp): return 1
