# -*- coding: utf-8 -*-
from content import ContentObject
import copy


class aid:
    def __init__(self, name=None, addresses=None, resolvers=None, userDefinedProperties=None, co=None):
        """
        Agent Identifier Class
        Optional parameters:
                String name
                String[] addresses
                String[] resolvers
                ContentObject co
        """
        if co:
            self.__name = co.name
            if "list" in str(type(co.addresses)):
                self.__addresses = copy.copy(co.addresses)
            else:
                self.__addresses = []
                if co.addresses:
                    self.__addresses.append(co.addresses)
            if "list" in str(type(co.resolvers)):
                self.__resolvers = copy.copy(co.resolvers)
            else:
                self.__resolvers = []
                if co.resolvers:
                    self.__resolvers.append(co.resolvers)
            self.__userDefinedProperties = list()
            return

        if name is not None:
            self.__name = name
        else:
            self.__name = None  # string
        if addresses is not None:
            self.__addresses = addresses
        else:
            self.__addresses = list()  # string
        if resolvers is not None:
            self.__resolvers = resolvers
        else:
            self.__resolvers = list()  # aid
        if userDefinedProperties is not None:
            self.__userDefinedProperties = userDefinedProperties
        else:
            self.__userDefinedProperties = list()  # properties

    def getName(self):
        """
        returns name of the agent (string)
        """
        return self.__name

    def setName(self, name):
        """
        sets name of the agent (string)
        """
        self.__name = name

    def getAddresses(self):
        """
        returns a list of addreses
        """
        return self.__addresses

    def addAddress(self, addr):
        """
        adds a new address to the addresses list
        """
        self.__addresses.append(addr)

    def getResolvers(self):
        """
        returns a list of resolvers
        """
        return self.__resolvers

    def addResolvers(self, resolver):
        """
        adds a new resolver to the resolvers list
        """
        self.__resolvers.append(resolver)

    def getProperties(self):
        return self.__userDefinedProperties

    def addProperty(self, prop):
        self.__userDefinedProperties.append(prop)

    def match(self, other):
        """
        returns True if two AIDs are similar
        else returns False
        """

        if other is None:
            return True
        if (self.getName() is not None and other.getName() is not None and not (str(other.getName()) in str(self.getName()))):
            return False
        if (len(self.getAddresses()) > 0 and len(other.getAddresses()) > 0):
            for oaddr in other.getAddresses():
                found = False
                for saddr in self.getAddresses():
                    if (oaddr in saddr):
                        found = True
                if not found:
                    return False
        if (len(self.getResolvers()) > 0 and len(other.getResolvers()) > 0):
            for oaddr in other.getResolvers():
                found = False
                for saddr in self.getResolvers():
                    if (oaddr in saddr):
                        found = True
                if not found:
                    return False
        if (len(self.getProperties()) > 0 and len(other.getProperties()) > 0):
            for oaddr in other.getProperties():
                found = False
                for saddr in self.getProperties():
                    if (oaddr in saddr):
                        found = True
                if not found:
                    return False
        return True

    def __eq__(self, other):
        """
        Comparision operator (==)
        returns True if two AIDs are equal
        else returns False
        """
        if other is None:
            return False

        if (self.getName() is not None and other.getName() is not None
                and self.getName() != other.getName()):
            return False
        addr1 = self.getAddresses()
        addr2 = other.getAddresses()
        addr1.sort()
        addr2.sort()
        if addr1 != addr2:
            return False

        res1 = self.getResolvers()
        res2 = other.getResolvers()
        res1.sort()
        res2.sort()
        if res1 != res2:
            return False

        return True

    def __ne__(self, other):
        """
        != operator
        returns False if two AIDs are equal
        else returns True
        """

        return not (self == other)

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
        if self.getName() is not None:
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
        if self.getAddresses() != []:
            co["addresses"] = []
            for addr in self.getAddresses():
                co["addresses"].append(addr)
        if self.getResolvers() != []:
            co["resolvers"] = []
            for r in self.getResolvers():
                co["resolvers"].append(r)
        if self.getProperties() != []:
            co["properties"] = []
            for p in self.getProperties():
                co["properties"].append(p)
        return co

    def asJSON(self):
        """
        returns a version of an AID in JSON format
        """
	try:
	    import json
	except ImportError:
	    import simplejson as json 
        return json.dumps(self.asContentObject())

    def asXML(self):
        """
        returns a printable version of an AID in XML
        """
        sb = "<agent-identifier>\n\t" + self.encodeTag("name", self.getName()) + "\n"
        sb = sb + "\t<addresses>\n"

        addresses = self.getAddresses()
        for addr in addresses:
            sb = sb + "\t\t" + self.encodeTag("url", addr) + "\n"

        sb = sb + "\t</addresses>\n"

        sb = sb + "</agent-identifier>\n"

        return sb

    def encodeTag(self, tag, content):
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
                    self.addAddress(addr)  # [0])

            if "resolvers" in content["agent-identifier"]:
                for res in content["agent-identifier"].resolvers.sequence:
                    self.addResolvers(res)  # [0]))

        else:
            return -1

    def loadJSON(self, content):
        """
        initialices an AID class using a JSON string
        """

        if "name" in content:
            self.setName(content["name"])
        else:
            return -1

        if "addresses" in content:
            for addr in content["addresses"]:
                self.addAddress(addr)

        if "resolvers" in content:
            for res in content["resolvers"]:
                self.addResolvers(res)
