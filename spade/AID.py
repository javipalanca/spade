

class aid:
	def __init__(self, name = None, addresses = None, resolvers = None, userDefinedProperties= None):
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
		return self.__name

	def setName(self,name):
		self.__name = name

	def getAddresses(self):
		return self.__addresses

	def addAddress(self,addr):
		self.__addresses.append(addr)

	def getResolvers(self):
		return self.__resolvers

	def addResolvers(self,resolver):
		self.__resolvers.append(resolver)

	def getProperties(self):
		return self.__userDefinedProperties
	
	def addPropertie(self,prop):
		self.__userDefinedProperties.append(prop)

	def __eq__(self, other):
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


	def asXML(self):
		sb = "<agent-identifier>\n\t" + self.encodeTag( "name", self.getName() ) + "\n"
		sb = sb + "\t<addresses>\n"
    
		addresses = self.getAddresses()
		for addr in addresses:
			sb = sb + "\t\t" + self.encodeTag( "url", addr ) + "\n"

		sb = sb + "\t</addresses>\n"
	 	sb = sb + "</agent-identifier>\n"

		return sb

	def encodeTag( self, tag, content ):
		sb = "<" + tag + ">" + content + "</" + tag + ">"

		return sb


	def loadSL0(self, content):

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



				
