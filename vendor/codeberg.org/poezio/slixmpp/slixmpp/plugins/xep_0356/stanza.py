from slixmpp.plugins.xep_0297 import Forwarded
from slixmpp.stanza import Iq, Message
from slixmpp.xmlstream import ElementBase, register_stanza_plugin

NS = "urn:xmpp:privilege:2"


class Privilege(ElementBase):
    namespace = NS
    name = "privilege"
    plugin_attrib = "privilege"

    def permission(self, access):
        for perm in self["perms"]:
            if perm["access"] == access:
                return perm["type"]

    def roster(self):
        return self.permission("roster")

    def message(self):
        return self.permission("message")

    def presence(self):
        return self.permission("presence")

    def add_perm(self, access, type_):
        # This should only be needed for servers, so maybe out of scope for slixmpp
        perm = Perm()
        perm["type"] = type_
        perm["access"] = access
        self.append(perm)


class Perm(ElementBase):
    namespace = NS
    name = "perm"
    plugin_attrib = "perm"
    plugin_multi_attrib = "perms"
    interfaces = {"type", "access"}


class NameSpace(ElementBase):
    namespace = NS
    name = "namespace"
    plugin_attrib = "namespace"
    plugin_multi_attrib = "namespaces"
    interfaces = {"ns", "type"}


class PrivilegedIq(ElementBase):
    namespace = NS
    name = "privileged_iq"
    plugin_attrib = "privileged_iq"


def register():
    register_stanza_plugin(Message, Privilege)
    register_stanza_plugin(Iq, Privilege)
    register_stanza_plugin(Privilege, Forwarded)
    register_stanza_plugin(Privilege, Perm, iterable=True)
    register_stanza_plugin(Perm, NameSpace, iterable=True)
    register_stanza_plugin(Iq, PrivilegedIq)
