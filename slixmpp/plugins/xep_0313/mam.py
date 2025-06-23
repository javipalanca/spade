
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission
import logging

from asyncio import Future
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Tuple,
)

from slixmpp import JID
from slixmpp.stanza import Message, Iq
from slixmpp.xmlstream.handler import Collector
from slixmpp.xmlstream.matcher import MatchXMLMask
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0313 import stanza
from slixmpp.plugins.xep_0004.stanza import Form


log = logging.getLogger(__name__)


class XEP_0313(BasePlugin):

    """
    XEP-0313 Message Archive Management
    """

    name = 'xep_0313'
    description = 'XEP-0313: Message Archive Management'
    dependencies = {
        'xep_0004', 'xep_0030', 'xep_0050', 'xep_0059', 'xep_0297'
    }
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(stanza.MAM, Form)
        register_stanza_plugin(Iq, stanza.MAM)
        register_stanza_plugin(Message, stanza.Result)
        register_stanza_plugin(Iq, stanza.Fin)
        register_stanza_plugin(
            stanza.Result,
            self.xmpp['xep_0297'].stanza.Forwarded
        )
        register_stanza_plugin(stanza.MAM, self.xmpp['xep_0059'].stanza.Set)
        register_stanza_plugin(stanza.Fin, self.xmpp['xep_0059'].stanza.Set)
        register_stanza_plugin(Iq, stanza.Metadata)
        register_stanza_plugin(stanza.Metadata, stanza.Start)
        register_stanza_plugin(stanza.Metadata, stanza.End)

    def retrieve(
            self,
            jid: Optional[JID] = None,
            start: Optional[datetime] = None,
            end: Optional[datetime] = None,
            with_jid: Optional[JID] = None,
            ifrom: Optional[JID] = None,
            reverse: bool = False,
            timeout: int = None,
            callback: Callable[[Iq], None] = None,
            iterator: bool = False,
            rsm: Optional[Dict[str, Any]] = None
    ) -> Awaitable:
        """
        Send a MAM query and retrieve the results.

        :param JID jid: Entity holding the MAM records
        :param datetime start,end: MAM query temporal boundaries
        :param JID with_jid: Filter results on this JID
        :param JID ifrom: To change the from address of the query
        :param bool reverse: Get the results in reverse order
        :param int timeout: IQ timeout
        :param func callback: Custom callback for handling results
        :param bool iterator: Use RSM and iterate over a paginated query
        :param dict rsm: RSM custom options
        """
        iq, stanza_mask = self._pre_mam_retrieve(
            jid, start, end, with_jid, ifrom
        )
        query_id = iq['id']
        amount = 10
        if rsm:
            for key, value in rsm.items():
                iq['mam']['rsm'][key] = str(value)
                if key == 'max':
                    amount = value
        cb_data = {}

        xml_mask = str(stanza_mask)

        def pre_cb(query: Iq) -> None:
            stanza_mask['mam_result']['queryid'] = query['id']
            xml_mask = str(stanza_mask)
            query['mam']['queryid'] = query['id']
            collector = Collector(
                'MAM_Results_%s' % query_id,
                MatchXMLMask(xml_mask))
            self.xmpp.register_handler(collector)
            cb_data['collector'] = collector

        def post_cb(result: Iq) -> None:
            results = cb_data['collector'].stop()
            if result['type'] == 'result':
                result['mam']['results'] = results
                result['mam_fin']['results'] = results

        if iterator:
            return self.xmpp['xep_0059'].iterate(
                iq, 'mam', 'results', amount=amount,
                reverse=reverse, recv_interface='mam_fin',
                pre_cb=pre_cb, post_cb=post_cb
            )

        collector = Collector(
            'MAM_Results_%s' % query_id,
            MatchXMLMask(xml_mask))
        self.xmpp.register_handler(collector)

        def wrapped_cb(iq: Iq) -> None:
            results = collector.stop()
            if iq['type'] == 'result':
                iq['mam']['results'] = results
            if callback:
                callback(iq)

        return iq.send(timeout=timeout, callback=wrapped_cb)

    async def iterate(
            self,
            jid: Optional[JID] = None,
            start: Optional[datetime] = None,
            end: Optional[datetime] = None,
            with_jid: Optional[JID] = None,
            ifrom: Optional[JID] = None,
            reverse: bool = False,
            rsm: Optional[Dict[str, Any]] = None,
            total: Optional[int] = None,
    ) -> AsyncGenerator:
        """
        Iterate over each message of MAM query.

        .. versionadded:: 1.8.0

        :param jid: Entity holding the MAM records
        :param start: MAM query start time
        :param end: MAM query end time
        :param with_jid: Filter results on this JID
        :param ifrom: To change the from address of the query
        :param reverse: Get the results in reverse order
        :param rsm: RSM custom options
        :param total: A number of messages received after which the query
                      should stop.
        """
        iq, stanza_mask = self._pre_mam_retrieve(
            jid, start, end, with_jid, ifrom
        )
        query_id = iq['id']
        amount = 10

        if rsm:
            for key, value in rsm.items():
                iq['mam']['rsm'][key] = str(value)
                if key == 'max':
                    amount = value
        cb_data = {}

        def pre_cb(query: Iq) -> None:
            stanza_mask['mam_result']['queryid'] = query['id']
            xml_mask = str(stanza_mask)
            query['mam']['queryid'] = query['id']
            collector = Collector(
                'MAM_Results_%s' % query_id,
                MatchXMLMask(xml_mask))
            self.xmpp.register_handler(collector)
            cb_data['collector'] = collector

        def post_cb(result: Iq) -> None:
            results = cb_data['collector'].stop()
            if result['type'] == 'result':
                result['mam']['results'] = results
                result['mam_fin']['results'] = results

        iterator = self.xmpp['xep_0059'].iterate(
            iq, 'mam', 'results', amount=amount,
            reverse=reverse, recv_interface='mam_fin',
            pre_cb=pre_cb, post_cb=post_cb
        )
        recv_count = 0

        async for page in iterator:
            messages = [message for message in page['mam']['results']]
            if reverse:
                messages.reverse()
            for message in messages:
                yield message
                recv_count += 1
                if total is not None and recv_count >= total:
                    break
            if total is not None and recv_count >= total:
                break

    def _pre_mam_retrieve(
            self,
            jid: Optional[JID] = None,
            start: Optional[datetime] = None,
            end: Optional[datetime] = None,
            with_jid: Optional[JID] = None,
            ifrom: Optional[JID] = None,
    ) -> Tuple[Iq, Message]:
        """Build the IQ and stanza mask for MAM results
        """
        iq = self.xmpp.make_iq_set(ito=jid, ifrom=ifrom)
        query_id = iq['id']
        iq['mam']['queryid'] = query_id
        iq['mam']['start'] = start
        iq['mam']['end'] = end
        iq['mam']['with'] = with_jid

        stanza_mask = self.xmpp.Message()

        auto_origin = stanza_mask.xml.find('{urn:xmpp:sid:0}origin-id')
        if auto_origin is not None:
            stanza_mask.xml.remove(auto_origin)
        del stanza_mask['id']
        del stanza_mask['lang']
        stanza_mask['from'] = jid
        stanza_mask['mam_result']['queryid'] = query_id

        return (iq, stanza_mask)

    async def get_fields(self, jid: Optional[JID] = None, **iqkwargs) -> Form:
        """Get MAM query fields.

        .. versionadded:: 1.8.0

        :param jid: JID to retrieve the policy from.
        :return: The Form of allowed options
        """
        ifrom = iqkwargs.pop('ifrom', None)
        iq = self.xmpp.make_iq_get(ito=jid, ifrom=ifrom)
        iq.enable('mam')
        result = await iq.send(**iqkwargs)
        return result['mam']['form']

    async def get_configuration_commands(self, jid: Optional[JID],
                                         **discokwargs) -> Future:
        """Get the list of MAM advanced configuration commands.

        .. versionchanged:: 1.8.0

        :param jid: JID to get the commands from.
        """
        if jid is None:
            jid = self.xmpp.boundjid.bare
        return await self.xmpp['xep_0030'].get_items(
            jid=jid,
            node='urn:xmpp:mam#configure',
            **discokwargs
        )

    def get_archive_metadata(self, jid: Optional[JID] = None,
                             **iqkwargs) -> Future:
        """Get the archive metadata from a JID.

        :param jid: JID to get the metadata from.
        """
        ifrom = iqkwargs.pop('ifrom', None)
        iq = self.xmpp.make_iq_get(ito=jid, ifrom=ifrom)
        iq.enable('mam_metadata')
        return iq.send(**iqkwargs)
