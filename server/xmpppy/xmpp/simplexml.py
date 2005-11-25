##   simplexml.py based on Mattew Allum's xmlstream.py
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

# $Id: simplexml.py,v 1.23 2004/09/25 19:05:38 snakeru Exp $

import xml.parsers.expat

def XMLescape(txt):
    "Escape XML entities"
    return txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

ENCODING='utf-8'
def ustr(what):
    if type(what) == type(u''): return what
    try: r=what.__str__()
    except AttributeError: r=str(what)
    if type(r)<>type(u''): return unicode(r,ENCODING)
    return r

class Node:
    FORCE_NODE_RECREATION=0
    def __init__(self, tag=None, attrs={}, payload=[], parent=None, node=None):
        if node:
            if self.FORCE_NODE_RECREATION and type(node)==type(self): node=str(node)
            if type(node)<>type(self): node=NodeBuilder(node,self)
            else:
                self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = node.name,node.namespace,{},[],[],node.parent
                for key  in node.attrs.keys(): self.attrs[key]=node.attrs[key]
                for data in node.data: self.data.append(data)
                for kid  in node.kids: self.kids.append(kid)
        else: self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = 'tag','',{},[],[],None

        if tag: self.namespace, self.name = ([self.namespace]+tag.split())[-2:]
        if parent: self.parent = parent
        if self.parent and not self.namespace: self.namespace=self.parent.namespace
        for attr in attrs.keys():
            self.attrs[attr]=attrs[attr]
        if type(payload) in (type(''),type(u'')): payload=[payload]
        for i in payload:
            if type(i)==type(self): self.addChild(node=i)
            else: self.data.append(ustr(i))
        self.T=T(self)
        self.NT=NT(self)

    def __str__(self,parent=None,fancy=0):
        s = (fancy-1) * 2 * ' ' + "<" + self.name
        if self.namespace:
            if parent and parent.namespace!=self.namespace:
                s = s + ' xmlns="%s"'%self.namespace
        for key in self.attrs.keys():
            val = ustr(self.attrs[key])
            s = s + ' %s="%s"' % ( key, XMLescape(val) )
        s = s + ">"
        cnt = 0 
        if self.kids:
            if fancy: s = s + "\n"
            for a in self.kids:
                if not fancy and (len(self.data)-1)>=cnt: s=s+XMLescape(self.data[cnt])
                elif (len(self.data)-1)>=cnt: s=s+XMLescape(self.data[cnt].strip())
                if fancy: s = s + a.__str__(self,fancy=fancy+1)
                else: s = s + a.__str__(self)
                cnt=cnt+1
        if not fancy and (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt])
        elif (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt].strip())
        if not self.kids and s[-1:]=='>':
            s=s[:-1]+' />'
            if fancy: s = s + "\n"
        else:
            if fancy and not self.data: s = s + (fancy-1) * 2 * ' '
            s = s + "</" + self.name + ">"
            if fancy: s = s + "\n"
        return s
    def addChild(self, name=None, attrs={}, payload=[], namespace=None, node=None):
        if namespace: name=namespace+' '+name
        if node:
            newnode=node
            node.parent = self
        else: newnode=Node(tag=name, parent=self, attrs=attrs, payload=payload)
        self.kids.append(newnode)
        return newnode
    def addData(self, data): self.data.append(ustr(data))
    def clearData(self): self.data=[]
    def delAttr(self, key): del self.attrs[key]
    def delChild(self, node, attrs={}):
        if type(node)<>type(self): node=self.getTag(node,attrs)
        self.kids.remove(node)
        return node
    def getAttrs(self): return self.attrs
    def getAttr(self, key):
        try: return self.attrs[key]
        except: return None
    def getChildren(self): return self.kids
    def getData(self): return ''.join(self.data)
    def getName(self): return self.name
    def getNamespace(self): return self.namespace
    def getParent(self): return self.parent
    def getPayload(self):
        ret=[]
        for i in range(len(self.kids)+len(self.data)+1):
            try:
                if self.data[i]: ret.append(self.data[i])
            except IndexError: pass
            try: ret.append(self.kids[i])
            except IndexError: pass
        return ret
    def getTag(self, name, attrs={}, namespace=None): return self.getTags(name, attrs, namespace, one=1)
    def getTagAttr(self,tag,attr):
        try: return self.getTag(tag).attrs[attr]
        except: return None
    def getTagData(self,tag):
        try: return self.getTag(tag).getData()
        except: return None
    def getTags(self, name, attrs={}, namespace=None, one=0):
        nodes=[]
        for node in self.kids:
            if namespace and namespace<>node.getNamespace(): continue
            if node.getName() == name:
                for key in attrs.keys():
                   if not node.attrs.has_key(key) or node.attrs[key]<>attrs[key]: break
                else: nodes.append(node)
            if one and nodes: return nodes[0]
        if not one: return nodes
    def setAttr(self, key, val): self.attrs[key]=val
    def setData(self, data): self.data=[ustr(data)]
    def setName(self,val): self.name = val
    def setNamespace(self, namespace): self.namespace=namespace
    def setParent(self, node): self.parent = node
    def setPayload(self,payload,add=0):
        if type(payload) in (type(''),type(u'')): payload=[payload]
        if add: self.kids+=payload
        else: self.kids=payload
    def setTag(self, name, attrs={}, namespace=None):
        node=self.getTags(name, attrs, namespace=namespace, one=1)
        if node: return node
        else: return self.addChild(name, attrs, namespace=namespace)
    def setTagAttr(self,tag,attr,val):
        try: self.getTag(tag).attrs[attr]=val
        except: self.addChild(tag,attrs={attr:val})
    def setTagData(self,tag,val,attrs={}):
        try: self.getTag(tag,attrs).setData(ustr(val))
        except: self.addChild(tag,attrs,payload=[ustr(val)])
    def has_attr(self,key): return self.attrs.has_key(key)
    def __getitem__(self,item): return self.getAttr(item)
    def __setitem__(self,item,val): return self.setAttr(item,val)
    def __delitem__(self,item): return self.delAttr(item,val)

class T:
    def __init__(self,node): self.__dict__['node']=node
    def __getattr__(self,attr): return self.node.setTag(attr)
    def __setattr__(self,attr,val):
        if isinstance(val,Node): Node.__init__(self.node.setTag(attr),node=val)
        else: return self.node.setTagData(attr,val)
    def __delattr__(self,attr): return self.node.delChild(attr)

class NT(T):
    def __getattr__(self,attr): return self.node.addChild(attr)
    def __setattr__(self,attr,val):
        if isinstance(val,Node): self.node.addChild(attr,node=val)
        else: return self.node.addChild(attr,payload=[val])

DBG_NODEBUILDER = 'nodebuilder'
class NodeBuilder:
    """builds a 'minidom' from data parsed to it. Primarily for insertXML
       method of Node"""
    def __init__(self,data=None,initial_node=None):
        self.DEBUG(DBG_NODEBUILDER, "Preparing to handle incoming XML stream.", 'start')
        self._parser = xml.parsers.expat.ParserCreate(namespace_separator=' ')
        self._parser.StartElementHandler       = self.starttag
        self._parser.EndElementHandler         = self.endtag
        self._parser.CharacterDataHandler      = self.handle_data
        self._parser.StartNamespaceDeclHandler = self.handle_namespace_start
        self.Parse = self._parser.Parse

        self.__depth = 0
        self._dispatch_depth = 1
        self._document_attrs = None
        self._mini_dom=initial_node
        self.last_is_data = 1
        self._ptr=None
        self.namespaces={"http://www.w3.org/XML/1998/namespace":'xml:'}
        self.xmlns="http://www.w3.org/XML/1998/namespace"

        if data: self._parser.Parse(data,1)

    def destroy(self):
        self._parser.StartElementHandler       = None
        self._parser.EndElementHandler         = None
        self._parser.CharacterDataHandler      = None
        self._parser.StartNamespaceDeclHandler = None

    def starttag(self, tag, attrs):
        """XML Parser callback"""
        attlist=attrs.keys()       #
        for attr in attlist:       # FIXME: Crude hack. And it also slows down the whole library considerably.
            sp=attr.rfind(" ")     #
            if sp==-1: continue    #
            ns=attr[:sp]           #
            attrs[self.namespaces[ns]+attr[sp+1:]]=attrs[attr]
            del attrs[attr]        #
        self.__depth += 1
        self.DEBUG(DBG_NODEBUILDER, "DEPTH -> %i , tag -> %s, attrs -> %s" % (self.__depth, tag, `attrs`), 'down')
        if self.__depth == self._dispatch_depth:
            if not self._mini_dom : self._mini_dom = Node(tag=tag, attrs=attrs)
            else: Node.__init__(self._mini_dom,tag=tag, attrs=attrs)
            self._ptr = self._mini_dom
        elif self.__depth > self._dispatch_depth:
            self._ptr.kids.append(Node(tag=tag,parent=self._ptr,attrs=attrs))
            self._ptr = self._ptr.kids[-1]
        if self.__depth == 1:
            self._document_attrs = attrs
            ns, name = (['']+tag.split())[-2:]
            self.stream_header_received(ns, name, attrs)
        if not self.last_is_data and self._ptr.parent: self._ptr.parent.data.append('')
        self.last_is_data = 0

    def endtag(self, tag ):
        """XML Parser callback"""
        self.DEBUG(DBG_NODEBUILDER, "DEPTH -> %i , tag -> %s" % (self.__depth, tag), 'up')
        if self.__depth == self._dispatch_depth:
            self.dispatch(self._mini_dom)
        elif self.__depth > self._dispatch_depth:
            self._ptr = self._ptr.parent
        else:
            self.DEBUG(DBG_NODEBUILDER, "Got higher than dispatch level. Stream terminated?", 'stop')
        self.__depth -= 1
        self.last_is_data = 0
        if self.__depth == 0: self.stream_footer_received()

    def handle_data(self, data):
        """XML Parser callback"""
        self.DEBUG(DBG_NODEBUILDER, data, 'data')
        if not self._ptr: return
        if self.last_is_data:
            self._ptr.data[-1] += data
        else:
            self._ptr.data.append(data)
            self.last_is_data = 1

    def handle_namespace_start(self, prefix, uri):
        if prefix: self.namespaces[uri]=prefix+':'
        else: self.xmlns=uri
    def DEBUG(self, level, text, comment=None): pass
    def getDom(self): return self._mini_dom
    def dispatch(self,stanza): pass
    def stream_header_received(self,ns,tag,attrs): pass
    def stream_footer_received(self): pass

def XML2Node(xml): return NodeBuilder(xml).getDom()
