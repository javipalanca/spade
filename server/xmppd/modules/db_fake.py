# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# AUTH_db interface example for xmppd.py

# $Id: db_fake.py,v 1.4 2004/10/24 04:49:09 snakeru Exp $

from xmpp import *

db={}
db['localhost']={}
db['thx1138.dsic.upv.es']={}
db['localhost']['test']='test'
db['localhost']['test2']='test'
db['localhost']['gusarba']='kakatua'
db['localhost']['acc']='secret'
db['localhost']['ams']='secret'
db['localhost']['df']='secret'
db['localhost']['rma']='secret'
db['thx1138.dsic.upv.es']['gusarba']='kakatua'
db['thx1138.dsic.upv.es']['jpalanca']='kakatua'
db['thx1138.dsic.upv.es']['test']='test'
db['thx1138.dsic.upv.es']['acc']='secret'
db['thx1138.dsic.upv.es']['ams']='secret'
db['thx1138.dsic.upv.es']['df']='secret'
db['thx1138.dsic.upv.es']['rma']='secret'

class AUTH(PlugIn):
    NS=''
    def getpassword(self, username, domain):
        try: return db[domain][username]
        except KeyError: pass

    def isuser(self, username, domain):
        try: return db[domain].has_key(username)
        except KeyError: pass

class DB(PlugIn):
    NS=''
    def store(self,domain,node,stanza,id='next_unique_id'): pass
