from slixmpp import register_stanza_plugin
from slixmpp.plugins.xep_0402.stanza import Extensions
from slixmpp.xmlstream import ElementBase

NS = "urn:xmpp:bookmarks-pinning:0"


class Pinned(ElementBase):
    """
    Pinned bookmark element


    To enable it on a Conference element, use enable() like this:

    .. code-block::python

        # C being a Conference element
        C['extensions'].enable('pinned')

    Which will add the <pinned> element to the <extensions> element.
    """
    namespace = NS
    name = "pinned"
    plugin_attrib = "pinned"
    interfaces = {"pinned"}
    bool_interfaces = {"pinned"}
    is_extension = True


def register_plugin():
    register_stanza_plugin(Extensions, Pinned)
