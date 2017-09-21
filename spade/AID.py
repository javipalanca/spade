# -*- coding: utf-8 -*-
from .utils import deprecated
from .content import ContentObject
import copy


class aid:
    def __init__(self, name=None, addresses=None, resolvers=None, user_defined_properties=None, co=None):
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
            self.__user_defined_properties = list()
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
        if user_defined_properties is not None:
            self.__user_defined_properties = user_defined_properties
        else:
            self.__user_defined_properties = list()  # properties

    def get_name(self):
        """
        returns name of the agent (string)
        """
        return self.__name

    getName = deprecated(get_name, "getName")

    def set_name(self, name):
        """
        sets name of the agent (string)
        """
        self.__name = name

    setName = deprecated(set_name, "setName")

    def get_addresses(self):
        """
        returns a list of addreses
        """
        return self.__addresses

    getAddresses = deprecated(get_addresses, "getAddresses")

    def add_address(self, addr):
        """
        adds a new address to the addresses list
        """
        self.__addresses.append(addr)

    addAddress = deprecated(add_address, "addAddress")

    def get_resolvers(self):
        """
        returns a list of resolvers
        """
        return self.__resolvers

    getResolvers = deprecated(get_resolvers, "getResolvers")

    def add_resolvers(self, resolver):
        """
        adds a new resolver to the resolvers list
        """
        self.__resolvers.append(resolver)

    addResolvers = deprecated(add_resolvers, "addResolvers")

    def get_properties(self):
        return self.__user_defined_properties

    getProperties = deprecated(get_properties, "getProperties")

    def add_property(self, prop):
        self.__user_defined_properties.append(prop)

    addProperty = deprecated(add_property, "addProperty")

    def match(self, other):
        """
        returns True if two AIDs are similar
        else returns False
        """

        if other is None:
            return True
        if self.get_name() is not None and other.get_name() is not None and not (str(other.get_name()) in str(self.get_name())):
            return False
        if len(self.get_addresses()) > 0 and len(other.get_addresses()) > 0:
            for oaddr in other.get_addresses():
                found = False
                for saddr in self.get_addresses():
                    if oaddr in saddr:
                        found = True
                if not found:
                    return False
        if len(self.get_resolvers()) > 0 and len(other.get_resolvers()) > 0:
            for oaddr in other.get_resolvers():
                found = False
                for saddr in self.get_resolvers():
                    if oaddr in saddr:
                        found = True
                if not found:
                    return False
        if len(self.get_properties()) > 0 and len(other.get_properties()) > 0:
            for oaddr in other.get_properties():
                found = False
                for saddr in self.get_properties():
                    if oaddr in saddr:
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

        if (self.get_name() is not None and other.get_name() is not None
                and self.get_name() != other.get_name()):
            return False
        addr1 = self.get_addresses()
        addr2 = other.get_addresses()
        addr1.sort()
        addr2.sort()
        if addr1 != addr2:
            return False

        res1 = self.get_resolvers()
        res2 = other.get_resolvers()
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
        for i in self.__user_defined_properties:
            h = h + hash(i)
        return h

    def __str__(self):
        """
        returns a printable version of an AID
        """
        sb = ""
        if self.get_name() is not None:
            sb = sb + ":name " + str(self.getName()) + "\n"
        if self.get_addresses():
            sb = sb + ":addresses \n(sequence\n"
            for i in self.get_addresses():
                sb = sb + str(i) + '\n'
            sb = sb + ")\n"
        if self.get_resolvers():
            sb = sb + ":resolvers \n(sequence\n"
            for i in self.get_resolvers():
                sb = sb + str(i) + '\n'
            sb = sb + ")\n"
        if sb != "":
            sb = "(agent-identifier\n" + sb + ")\n"
        else:
            sb = "None"

        return sb

    def to_content_object(self):
        """
        returns a version of an AID in ContentObject format
        """
        co = ContentObject()
        co["name"] = self.get_name()
        if self.get_addresses():
            co["addresses"] = []
            for addr in self.get_addresses():
                co["addresses"].append(addr)
        if self.get_resolvers():
            co["resolvers"] = []
            for r in self.get_resolvers():
                co["resolvers"].append(r)
        if self.get_properties() != []:
            co["properties"] = []
            for p in self.get_properties():
                co["properties"].append(p)
        return co

    asContentObject = deprecated(to_content_object, "asContentObject")

    def to_json(self):
        """
        returns a version of an AID in JSON format
        """
        try:
            import json
        except ImportError:
            import simplejson as json
            return json.dumps(self.asContentObject())

    asJSON = deprecated(to_json, "asJSON")

    def to_xml(self):
        """
        returns a printable version of an AID in XML
        """
        sb = "<agent-identifier>\n\t" + self.encode_tag("name", self.get_name()) + "\n"
        sb = sb + "\t<addresses>\n"

        addresses = self.get_addresses()
        for addr in addresses:
            sb = sb + "\t\t" + self.encode_tag("url", addr) + "\n"

        sb = sb + "\t</addresses>\n"

        sb = sb + "</agent-identifier>\n"

        return sb

    asXML = deprecated(to_xml, "asXML")

    def encode_tag(self, tag, content):
        """
        encodes a content between 2 XML tags using the tag parameter

                <tag>content</tag>

        return string
        """
        sb = "<" + tag + ">" + content + "</" + tag + ">"

        return sb

    def read_sl0(self, content):
        """
        initialices an AID class using a string content encoded in SLO
        """

        if "agent-identifier" in content:
            if "name" in content["agent-identifier"]:
                self.set_name(content["agent-identifier"].name[0])
            else:
                return -1

            if "addresses" in content["agent-identifier"]:
                for addr in content["agent-identifier"].addresses.sequence:
                    self.add_address(addr)  # [0])

            if "resolvers" in content["agent-identifier"]:
                for res in content["agent-identifier"].resolvers.sequence:
                    self.add_resolvers(res)  # [0]))

        else:
            return -1

    loadSL0 = deprecated(read_sl0, "loadSL0")

    def read_json(self, content):
        """
        initialices an AID class using a JSON string
        """

        if "name" in content:
            self.set_name(content["name"])
        else:
            return -1

        if "addresses" in content:
            for addr in content["addresses"]:
                self.add_address(addr)

        if "resolvers" in content:
            for res in content["resolvers"]:
                self.add_resolvers(res)

    loadJSON = deprecated(read_json, "loadJSON")