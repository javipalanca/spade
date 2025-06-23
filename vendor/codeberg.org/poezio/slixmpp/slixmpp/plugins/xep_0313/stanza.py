# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from datetime import datetime
from typing import (
    Any,
    Iterable,
    List,
    Optional,
    Set,
    Union,
)

from slixmpp.stanza import Message
from slixmpp.jid import JID
from slixmpp.xmlstream import ElementBase, ET
from slixmpp.plugins import xep_0082


class MAM(ElementBase):
    """A MAM Query element.

    .. code-block:: xml

        <iq type='set' id='juliet1'>
          <query xmlns='urn:xmpp:mam:2'>
            <x xmlns='jabber:x:data' type='submit'>
              <field var='FORM_TYPE' type='hidden'>
                <value>urn:xmpp:mam:2</value>
              </field>
              <field var='with'>
                <value>juliet@capulet.lit</value>
              </field>
            </x>
          </query>
        </iq>

    """
    name = 'query'
    namespace = 'urn:xmpp:mam:2'
    plugin_attrib = 'mam'
    #: Available interfaces:
    #:
    #: - ``queryid``: The MAM query id
    #: - ``start`` and ``end``: Temporal boundaries of the query
    #: - ``with``: JID of the other entity the conversation is with
    #: - ``after_id``: Fetch stanzas after this specific ID
    #: - ``before_id``: Fetch stanzas before this specific ID
    #: - ``ids``: Fetch the stanzas matching those IDs
    #: - ``results``: pseudo-interface used to accumulate MAM results during
    #:   fetch, not relevant for the stanza itself.
    interfaces = {
        'queryid', 'start', 'end', 'with', 'results',
        'before_id', 'after_id', 'ids', 'flip_page',
    }
    sub_interfaces = {'start', 'end', 'with', 'before_id', 'after_id', 'ids',
                      'flip_page'}

    def setup(self, xml=None):
        ElementBase.setup(self, xml)
        self._results: List[Message] = []

    def _setup_form(self):
        found = self.xml.find(
                '{jabber:x:data}x/'
                '{jabber:x:data}field[@var="FORM_TYPE"]/'
                "{jabber:x:data}value[.='urn:xmpp:mam:2']"
        )
        if found is None:
            self['form']['type'] = 'submit'
            self['form'].add_field(
                var='FORM_TYPE', ftype='hidden', value='urn:xmpp:mam:2'
            )

    def get_fields(self):
        form = self.get_plugin('form', check=True)
        if not form:
            return {}
        return form.get_fields()

    def get_start(self) -> Optional[datetime]:
        fields = self.get_fields()
        field = fields.get('start')
        if field and field["value"]:
            return xep_0082.parse(field['value'])
        return None

    def set_start(self, value: Union[str, datetime]):
        self._setup_form()
        if isinstance(value, datetime):
            value = xep_0082.format_datetime(value)
        self.set_custom_field('start', value)

    def get_end(self) -> Optional[datetime]:
        fields = self.get_fields()
        field = fields.get('end')
        if field and field["value"]:
            return xep_0082.parse(field['value'])
        return None

    def set_end(self, value: Union[str, datetime]):
        if isinstance(value, datetime):
            value = xep_0082.format_datetime(value)
        self.set_custom_field('end', value)

    def get_with(self) -> Optional[JID]:
        fields = self.get_fields()
        field = fields.get('with')
        if field:
            return JID(field['value'])
        return None

    def set_with(self, value: JID):
        self.set_custom_field('with', value)

    def set_custom_field(self, fieldname: str, value: Any):
        self._setup_form()
        fields = self.get_fields()
        field = fields.get(fieldname)
        if field:
            field['value'] = str(value)
        else:
            field = self['form'].add_field(var=fieldname)
            field['value'] = str(value)

    def get_custom_field(self, fieldname: str) -> Optional[str]:
        fields = self.get_fields()
        field = fields.get(fieldname)
        if field:
            return field['value']
        return None

    def set_before_id(self, value: str):
        self.set_custom_field('before-id', value)

    def get_before_id(self):
        self.get_custom_field('before-id')

    def set_after_id(self, value: str):
        self.set_custom_field('after-id', value)

    def get_after_id(self):
        self.get_custom_field('after-id')

    def set_ids(self, value: List[str]):
        self._setup_form()
        fields = self.get_fields()
        field = fields.get('ids')
        if field:
            field['ids'] = value
        else:
            field = self['form'].add_field(var='ids')
            field['value'] = value

    def get_ids(self):
        self.get_custom_field('id')

    # The results interface is meant only as an easy
    # way to access the set of collected message responses
    # from the query.

    def get_results(self) -> List[Message]:
        return self._results

    def set_results(self, values: List[Message]):
        self._results = values

    def del_results(self):
        self._results = []

    def get_flip_page(self):
        return self.xml.find(f'{{{self.namespace}}}flip-page') is not None

class Fin(ElementBase):
    """A MAM fin element (end of query).

    .. code-block:: xml

        <iq type='result' id='juliet1'>
          <fin xmlns='urn:xmpp:mam:2'>
            <set xmlns='http://jabber.org/protocol/rsm'>
              <first index='0'>28482-98726-73623</first>
              <last>09af3-cc343-b409f</last>
            </set>
          </fin>
        </iq>

    """
    name = 'fin'
    namespace = 'urn:xmpp:mam:2'
    plugin_attrib = 'mam_fin'
    interfaces = {'results', 'stable', 'complete'}

    def setup(self, xml=None):
        ElementBase.setup(self, xml)
        self._results: List[Message] = []

    # The results interface is meant only as an easy
    # way to access the set of collected message responses
    # from the query.

    def get_results(self) -> List[Message]:
        return self._results

    def set_results(self, values: List[Message]):
        self._results = values

    def del_results(self):
        self._results = []


class Result(ElementBase):
    """A MAM result payload.

    .. code-block:: xml

        <message id='aeb213' to='juliet@capulet.lit/chamber'>
          <result xmlns='urn:xmpp:mam:2' queryid='f27' id='28482-98726-73623'>
            <forwarded xmlns='urn:xmpp:forward:0'>
              <delay xmlns='urn:xmpp:delay' stamp='2010-07-10T23:08:25Z'/>
              <message xmlns='jabber:client' from="witch@shakespeare.lit"
                       to="macbeth@shakespeare.lit">
                <body>Hail to thee</body>
              </message>
            </forwarded>
          </result>
        </message>
    """
    name = 'result'
    namespace = 'urn:xmpp:mam:2'
    plugin_attrib = 'mam_result'
    #: Available interfaces:
    #:
    #: - ``queryid``: MAM queryid
    #: - ``id``: ID of the result
    interfaces = {'queryid', 'id'}


class Metadata(ElementBase):
    """Element containing archive metadata

    .. code-block:: xml

        <iq type='result' id='jui8921rr9'>
          <metadata xmlns='urn:xmpp:mam:2'>
            <start id='YWxwaGEg' timestamp='2008-08-22T21:09:04Z' />
            <end id='b21lZ2Eg' timestamp='2020-04-20T14:34:21Z' />
          </metadata>
        </iq>

    """
    name = 'metadata'
    namespace = 'urn:xmpp:mam:2'
    plugin_attrib = 'mam_metadata'


class Start(ElementBase):
    """Metadata about the start of an archive.

    .. code-block:: xml

        <iq type='result' id='jui8921rr9'>
          <metadata xmlns='urn:xmpp:mam:2'>
            <start id='YWxwaGEg' timestamp='2008-08-22T21:09:04Z' />
            <end id='b21lZ2Eg' timestamp='2020-04-20T14:34:21Z' />
          </metadata>
        </iq>

    """
    name = 'start'
    namespace = 'urn:xmpp:mam:2'
    plugin_attrib = name
    #: Available interfaces:
    #:
    #: - ``id``: ID of the first message of the archive
    #: - ``timestamp`` (``datetime``): timestamp of the first message of the
    #:   archive
    interfaces = {'id', 'timestamp'}

    def get_timestamp(self) -> Optional[datetime]:
        """Get the timestamp.

        :returns: The timestamp.
        """
        stamp = self.xml.attrib.get('timestamp', None)
        if stamp is not None:
            return xep_0082.parse(stamp)
        return stamp

    def set_timestamp(self, value: Union[datetime, str]):
        """Set the timestamp.

        :param value: Value of the timestamp (either a datetime or a
                      XEP-0082 timestamp string.
        """
        if isinstance(value, str):
            value = xep_0082.parse(value)
        value = xep_0082.format_datetime(value)
        self.xml.attrib['timestamp'] = value


class End(ElementBase):
    """Metadata about the end of an archive.

    .. code-block:: xml

        <iq type='result' id='jui8921rr9'>
          <metadata xmlns='urn:xmpp:mam:2'>
            <start id='YWxwaGEg' timestamp='2008-08-22T21:09:04Z' />
            <end id='b21lZ2Eg' timestamp='2020-04-20T14:34:21Z' />
          </metadata>
        </iq>

    """
    name = 'end'
    namespace = 'urn:xmpp:mam:2'
    plugin_attrib = name
    #: Available interfaces:
    #:
    #: - ``id``: ID of the first message of the archive
    #: - ``timestamp`` (``datetime``): timestamp of the first message of the
    #:   archive
    interfaces = {'id', 'timestamp'}

    def get_timestamp(self) -> Optional[datetime]:
        """Get the timestamp.

        :returns: The timestamp.
        """
        stamp = self.xml.attrib.get('timestamp', None)
        if stamp is not None:
            return xep_0082.parse(stamp)
        return stamp

    def set_timestamp(self, value: Union[datetime, str]):
        """Set the timestamp.

        :param value: Value of the timestamp (either a datetime or a
                      XEP-0082 timestamp string.
        """
        if isinstance(value, str):
            value = xep_0082.parse(value)
        value = xep_0082.format_datetime(value)
        self.xml.attrib['timestamp'] = value
