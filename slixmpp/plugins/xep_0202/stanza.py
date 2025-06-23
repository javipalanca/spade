
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import datetime as dt
from typing import Union

from slixmpp.xmlstream import ElementBase
from slixmpp.plugins import xep_0082


class EntityTime(ElementBase):

    """
    The <time> element represents the local time for an XMPP agent.
    The time is expressed in UTC to make synchronization easier
    between entities, but the offset for the local timezone is also
    included.

    Example <time> stanzas:
    ::

        <iq type="result">
          <time xmlns="urn:xmpp:time">
            <utc>2011-07-03T11:37:12.234569</utc>
            <tzo>-07:00</tzo>
          </time>
        </iq>

    Stanza Interface:
    ::

        time -- The local time for the entity (updates utc and tzo).
        utc  -- The UTC equivalent to local time.
        tzo  -- The local timezone offset from UTC.
    """

    name = 'time'
    namespace = 'urn:xmpp:time'
    plugin_attrib = 'entity_time'
    interfaces = {'tzo', 'utc', 'time'}
    sub_interfaces = interfaces

    def set_time(self, value: Union[str, dt.datetime]) -> None:
        """
        Set both the UTC and TZO fields given a time object.

        :param value: A datetime object or properly formatted
                      string equivalent.
        """
        date = value
        if not isinstance(value, dt.datetime):
            date = xep_0082.parse(value)
        self.set_utc(date)
        self.set_tzo(date.tzinfo)

    def get_time(self) -> dt.datetime:
        """
        Return the entity's local time based on the UTC and TZO data.
        """
        date = self.get_utc()
        tz = self.get_tzo()
        return date.astimezone(tz)

    def del_time(self) -> None:
        """Remove both the UTC and TZO fields."""
        del self['utc']
        del self['tzo']

    def get_tzo(self) -> dt.tzinfo:
        """
        Return the timezone offset from UTC as a tzinfo object.
        """
        tzo = self._get_sub_text('tzo')
        if tzo == '':
            tzo = 'Z'
        time = xep_0082.parse('00:00:00%s' % tzo)
        return time.tzinfo

    def set_tzo(self, value: Union[int, dt.tzinfo]) -> None:
        """
        Set the timezone offset from UTC.

        :param value: Either a tzinfo object or the number of
                      seconds (positive or negative) to offset.
        """
        time = xep_0082.time(offset=value)
        if xep_0082.parse(time).tzinfo == dt.timezone.utc:
            self._set_sub_text('tzo', 'Z')
        else:
            self._set_sub_text('tzo', time[-6:])

    def get_utc(self) -> dt.datetime:
        """
        Return the time in UTC as a datetime object.
        """
        value = self._get_sub_text('utc')
        if value == '':
            return xep_0082.parse(xep_0082.datetime())
        return xep_0082.parse('%sZ' % value)

    def set_utc(self, value: Union[str, dt.datetime]) -> None:
        """
        Set the time in UTC.

        :param value: A datetime object or properly formatted
                      string equivalent.
        """
        date = value
        if not isinstance(value, dt.datetime):
            date = xep_0082.parse(value)
        date = date.astimezone(dt.timezone.utc)
        value = xep_0082.format_datetime(date)
        self._set_sub_text('utc', value)
