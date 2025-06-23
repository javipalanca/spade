import logging

from slixmpp import CoroutineCallback, StanzaPath, Iq, register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import StanzaBase

from . import stanza


class XEP_0055(BasePlugin):
    """
    XEP-0055: Jabber Search

    The config options are only useful for a "server-side" search feature,
    and if the ``provide_search`` option is set to True.

    API
    ===

    ``search_get_form``: customize the search form content (ie fields)

    ``search_query``: return search results
    """
    name = "xep_0055"
    description = "XEP-0055: Jabber search"
    dependencies = {"xep_0004", "xep_0030"}
    stanza = stanza
    default_config = {
        "form_fields": {"first", "last"},
        "form_instructions": "",
        "form_title": "",
        "provide_search": True
    }

    def plugin_init(self):
        register_stanza_plugin(Iq, stanza.Search)
        register_stanza_plugin(stanza.Search, self.xmpp["xep_0004"].stanza.Form)

        if self.provide_search:
            self.xmpp["xep_0030"].add_feature(stanza.Search.namespace)
            self.xmpp.register_handler(
                CoroutineCallback(
                    "search",
                    StanzaPath("/iq/search"),
                    self._handle_search,
                )
            )
            self.api.register(self._get_form, "search_get_form")
            self.api.register(self._get_results, "search_query")

    async def _handle_search(self, iq: StanzaBase):
        if iq["search"]["form"].get_values():
            reply = await self.api["search_query"](None, None, iq.get_from(), iq)
            reply["search"]["form"]["type"] = "result"
        else:
            reply = await self.api["search_get_form"](None, None, iq.get_from(), iq)
        reply["search"]["form"].add_field(
            "FORM_TYPE", value=stanza.Search.namespace, ftype="hidden"
        )
        reply.send()

    async def _get_form(self, jid, node, ifrom, iq):
        reply = iq.reply()
        form = reply["search"]["form"]
        form["title"] = self.form_title
        form["instructions"] = self.form_instructions
        for field in self.form_fields:
            form.add_field(field)
        return reply

    async def _get_results(self, jid, node, ifrom, iq):
        reply = iq.reply()
        form = reply["search"]["form"]
        form["type"] = "result"

        for field in self.form_fields:
            form.add_reported(field)
        return reply

    def make_search_iq(self, **kwargs):
        iq = self.xmpp.make_iq(itype="set", **kwargs)
        iq["search"]["form"].set_type("submit")
        iq["search"]["form"].add_field(
            "FORM_TYPE", value=stanza.Search.namespace, ftype="hidden"
        )
        return iq


log = logging.getLogger(__name__)
