# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# AUTH_db interface example for xmppd.py

# $Id: db_fake.py,v 1.4 2004/10/24 04:49:09 snakeru Exp $

from xmpp import *
import os

try:
	from xml.marshal.generic import *
	marshal = Marshaller()
	unmarshal = Unmarshaller()
except:
	pass

db={}
# OLD STRUCTURE
#db['localhost']={}
#db['thx1138.dsic.upv.es']={}
#db['__admin__']={}
#db['localhost']['test']='test'
#db['localhost']['test2']='test'
#db['localhost']['gusarba']='kakatua'
#db['localhost']['jpalanca']='kakatua'
#db['localhost']['acc']='secret'
#db['localhost']['ams']='secret'
#db['localhost']['df']='secret'
#db['localhost']['rma']='secret'
#db['localhost']['ping']='secret'
#db['thx1138.dsic.upv.es']['gusarba']='kakatua'
#db['thx1138.dsic.upv.es']['jpalanca']='kakatua'
#db['thx1138.dsic.upv.es']['test']='test'
#db['thx1138.dsic.upv.es']['acc']='secret'
#db['thx1138.dsic.upv.es']['ams']='secret'
#db['thx1138.dsic.upv.es']['df']='secret'
#db['thx1138.dsic.upv.es']['rma']='secret'
#db['thx1138.dsic.upv.es']['ping']='secret'
#db['__admin__'] = ['gusarba']

class AUTH(PlugIn):
    NS=''
    def getpassword(self, username, domain):
        try: return db[domain][username]['password']
        except KeyError:
		return None
		#print "### DB: getpassword: Key Error: ", username, domain

    def isuser(self, username, domain):
        try: return db[domain].has_key(username)
        except KeyError:
		return False
		#print "### DB: isuser: Key Error: ", username, domain

    def isadmin(self, username):
	try:
		global db
		if username in db['__admin__']:
			return True
		else:
			return False
	except:
		return False
		#print "### DB: isadmin: Key Error: ", username

class DB(PlugIn):
    NS=''
    def store(self,domain,node,stanza,id='next_unique_id'): pass
    def plugin(self, server):
	global db
	self.spoolpath = server.spoolpath
	self.userdbfile = server.spoolpath + os.sep + 'user_db.xml'
	try:
		if self.loaddb():
			self.DEBUG('DB: User database loaded', 'info')
			# Create a dict for every servername
			for name in server.servernames:
				if name not in db.keys():
					db[name] = {}
			self.savedb()
		else:
			self.DEBUG('DB: Could NOT load user database. Building own', 'error')
			try:
				for name in server.servernames:
					db[name] = {}
				db['__admin__'] = {}
				if self.savedb():
					self.DEBUG('DB: User database built and saved', 'info')
				else:
					self.DEBUG('DB: Could not save built database', 'error')
			except:
				self.DEBUG('DB: Could not build user database. We are all doomed!', 'error')

	except:
		pass

    def registeruser(self,domain,username,password):
	try:
		# We only accept server domains, not every domain
		if domain in self._owner.servernames:
			db[domain][str(username)] = dict()
			db[domain][str(username)]['password'] = str(password)
			db[domain][str(username)]['roster'] = dict()
			self.DEBUG('registeruser: User registered in domain ' + str(domain) , 'info')
			self.savedb()
			#print "#### Trying to save database"
			return True
		else:
			self.DEBUG('registeruser: User NOT registered in domain ' + str(domain) , 'error')
			return False

		self.loaddb()
	except:
		print "### DB: User NOT registered: ", username
		return False

    def getRoster(self, jid):
	# Try split the username from the domain
	if '@' in jid:
		# Regular client
		username, domain = jid.split('@')
	else:
		# Component or similar
		username, domain = jid.split('.', 1)
	return db[domain][str(username)]['roster']

    def printdb(self):
	return str(db)

    def savedb(self):
	try:
		global db
		#print "#### userdbfile = " + str(self.userdbfile)
		#print "#### spoolpath = " + str(self.spoolpath)
		if not os.path.exists(self.spoolpath):
			self.DEBUG("spoolpath does no exist.", 'warn')
			p = self.spoolpath.split(os.sep)
			tmpitem=''
			for item in p:
				tmpitem+=os.sep+str(item)
				if not os.path.exists(tmpitem):
					self.DEBUG("mkdir " + str(tmpitem), 'info')
					os.mkdir(tmpitem)
		fh = open(self.userdbfile, 'w')
		marshal.dump(db, fh)
		fh.close()
		self.DEBUG('savedb: User database saved!', 'info')
		return True
	except:
		self.DEBUG('savedb: Could not save user database', 'error')
		return False

    def loaddb(self):
	try:
		global db
		fh = open(self.userdbfile, 'r')
		db = unmarshal.load(fh)
		fh.close()
		self.DEBUG('loaddb: User database loaded', 'info')
		return True
	except:
		self.DEBUG('loaddb: Could not load user database', 'error')
		return False

    def listdb(self):
	try:
		global db
		return str(db)
	except:
		pass

