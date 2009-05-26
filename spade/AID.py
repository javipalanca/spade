from content import ContentObject
import copy

class aid:
	def __init__(self, name = None, addresses = None, resolvers = None, userDefinedProperties= None, co = None):
		"""
		Agent Identifier Class
		Optional parameters:
			String name
			String[] addresses
			String[] resolvers
			ContentObject co
		"""
		if co:
		    #print "AID FROM:\n",co.pprint()
		    self.__name = co.name
		    if "list" in str(type(co.addresses)):
		        self.__addresses = copy.copy(co.addresses)
		    else:
		        self.__addresses = []
		        if co.addresses:
		            self.__addresses.append(co.addresses)
		    self.__resolvers = list()
		    self.__userDefinedProperties = list()
		    #print "AID:",str(self.asXML())
		    return
		    
		if name != None:
			self.__name = name
		else:
			self.__name = None #string
		if addresses != None:
			self.__addresses = addresses
		else:
			self.__addresses = list() #string
		if resolvers != None:
			self.__resolvers = resolvers
		else:
			self.__resolvers = list() #aid
		if userDefinedProperties != None:
			self.__userDefinedProperties = userDefinedProperties
		else:
			self.__userDefinedProperties = list() #properties

	def getName(self):
		"""
		returns name of the agent (string)
		"""
		return self.__name

	def setName(self,name):
		"""
		sets name of the agent (string)
		"""
		self.__name = name

	def getAddresses(self):
		"""
		returns a list of addreses
		"""
		return self.__addresses

	def addAddress(self,addr):
		"""
		adds a new address to the addresses list
		"""
		self.__addresses.append(addr)

	def getResolvers(self):
		"""
		returns a list of resolvers
		"""
		return self.__resolvers

	def addResolvers(self,resolver):
		"""
		adds a new resolver to the resolvers list
		"""
		self.__resolvers.append(resolver)

	def getProperties(self):
		return self.__userDefinedProperties

	def addPropertie(self,prop):
		self.__userDefinedProperties.append(prop)

	def __eq__(self, other):
		"""
		Comparision operator (==)
		returns True if two AIDs are equal
		else returns False
		"""
		if other != None:
			if (self.getName() != None and other.getName() != None \
			and self.getName() != other.getName()):
				return False
			if (len(self.getAddresses())>0 and len(other.getAddresses())>0 \
			and self.getAddresses().sort() != other.getAddresses().sort()):
				return False

			return True
		else: return False

	def __ne__(self,other):
		"""
		!= operator
		returns False if two AIDs are equal
		else returns True
		"""

		return not self == other


        def __hash__(self):
            h = hash(self.__name)
            for i in self.__addresses:
                h = h + hash(i)
            for i in self.__resolvers:
                h = h + hash(i)
            for i in self.__userDefinedProperties:
                h = h + hash(i)
            return h

	def __str__(self):
		"""
		returns a printable version of an AID
		"""
		sb = ""
		if self.getName() != None:
			sb = sb + ":name " + str(self.getName()) + "\n"
		if self.getAddresses() != []:
			sb = sb + ":addresses \n(sequence\n"
			for i in self.getAddresses():
				sb = sb + str(i) + '\n'
			sb = sb + ")\n"
		if self.getResolvers() != []:
			sb = sb + ":resolvers \n(sequence\n"
			for i in self.getResolvers():
				sb = sb + str(i) + '\n'
			sb = sb + ")\n"
		if sb != "":
			sb = "(agent-identifier\n" + sb + ")\n"
		else:
			sb = "None"

		return sb
		
	def asContentObject(self):
	    """
	    returns a version of an AID in ContentObject format
	    """
	    co = ContentObject()	    
	    co["name"] = self.getName()
	    co["addresses"] = []
	    for addr in self.getAddresses():
	        co["addresses"].append(addr)
	    return co

	def asXML(self):
		"""
		returns a printable version of an AID in XML
		"""
		sb = "<agent-identifier>\n\t" + self.encodeTag( "name", self.getName() ) + "\n"
		sb = sb + "\t<addresses>\n"

		addresses = self.getAddresses()
		for addr in addresses:
			sb = sb + "\t\t" + self.encodeTag( "url", addr ) + "\n"

		sb = sb + "\t</addresses>\n"
	 	sb = sb + "</agent-identifier>\n"

		return sb

	def encodeTag( self, tag, content ):
		"""
		encodes a content between 2 XML tags using the tag parameter

			<tag>content</tag>

		return string
		"""
		sb = "<" + tag + ">" + content + "</" + tag + ">"

		return sb


	def loadSL0(self, content):
		"""
		initialices an AID class using a string content encoded in SLO
		"""

		if "agent-identifier" in content:
			if "name" in content["agent-identifier"]:
				self.setName(content["agent-identifier"].name[0])
			else:
				return -1

			if "addresses" in content["agent-identifier"]:
				for addr in content["agent-identifier"].addresses.sequence:
					self.addAddress(addr)#[0])

			if "resolvers" in content["agent-identifier"]:
				for res in content["agent-identifier"].resolvers.sequence:
					self.addResolvers(self.loadSL0(res))#[0]))

		else: return -1




