from slixmpp import Presence
from slixmpp.xmlstream import ElementBase, register_stanza_plugin
from typing import List, Tuple

NS = 'urn:xmpp:hats:0'


class Hats(ElementBase):
    """
    Hats element, container for multiple hats:

    .. code-block::xml


      <hats xmlns='urn:xmpp:hats:0'>
        <hat title='Host' uri='http://schemas.example.com/hats#host' xml:lang='en-us'>
            <badge xmlns="urn:example:badges" fgcolor="#000000" bgcolor="#58C5BA"/>
        </hat>
        <hat title='Presenter' uri='http://schemas.example.com/hats#presenter' xml:lang='en-us'>
            <badge xmlns="urn:example:badges" fgcolor="#000000" bgcolor="#EC0524"/>
        </hat>
      </hats>

    """

    name = 'hats'
    namespace = NS
    plugin_attrib = 'hats'

    def add_hats(self, data: List[Tuple[str, str]]) -> None:
        for uri, title in data:
            hat = Hat()
            hat["uri"] = uri
            hat["title"] = title
            self.append(hat)


class Hat(ElementBase):
    """
    Hat element, has a title and url, may contain arbitrary sub-elements.

    .. code-block::xml

        <hat title='Host' uri='http://schemas.example.com/hats#host' xml:lang='en-us'>
            <badge xmlns="urn:example:badges" fgcolor="#000000" bgcolor="#58C5BA"/>
        </hat>

    """
    name = 'hat'
    plugin_attrib = 'hat'
    namespace = NS
    interfaces = {'title', 'uri'}
    plugin_multi_attrib = "hats"


def register_plugin() -> None:
    register_stanza_plugin(Hats, Hat, iterable=True)
    register_stanza_plugin(Presence, Hats)
