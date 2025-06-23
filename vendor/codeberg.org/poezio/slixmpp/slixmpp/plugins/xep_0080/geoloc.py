
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Erik Reuterborg Larsson
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
from asyncio import Future
from typing import Optional, Callable

from slixmpp import JID
from slixmpp.plugins.base import BasePlugin
from slixmpp.plugins.xep_0080 import stanza, Geoloc


log = logging.getLogger(__name__)


class XEP_0080(BasePlugin):

    """
    XEP-0080: User Location
    """

    name = 'xep_0080'
    description = 'XEP-0080: User Location'
    dependencies = {'xep_0163'}
    stanza = stanza

    def plugin_end(self):
        self.xmpp['xep_0163'].remove_interest(Geoloc.namespace)
        self.xmpp['xep_0030'].del_feature(feature=Geoloc.namespace)

    def session_bind(self, jid: JID):
        self.xmpp['xep_0163'].register_pep('user_location', Geoloc)

    def publish_location(self, **kwargs) -> Future:
        """
        Publish the user's current location.

        :param accuracy: Horizontal GPS error in meters.
        :param alt: Altitude in meters above or below sea level.
        :param area: A named area such as a campus or neighborhood.
        :param bearing: GPS bearing (direction in which the entity is
                        heading to reach its next waypoint), measured in
                        decimal degrees relative to true north.
        :param building: A specific building on a street or in an area.
        :param country: The nation where the user is located.
        :param countrycode: The ISO 3166 two-letter country code.
        :param datum: GPS datum.
        :param description: A natural-language name for or description of
                            the location.
        :param error: Horizontal GPS error in arc minutes. Obsoleted by
                      the accuracy parameter.
        :param floor: A particular floor in a building.
        :param lat: Latitude in decimal degrees North.
        :param locality: A locality within the administrative region, such
                         as a town or city.
        :param lon: Longitude in decimal degrees East.
        :param postalcode: A code used for postal delivery.
        :param region: An administrative region of the nation, such
                       as a state or province.
        :param room: A particular room in a building.
        :param speed: The speed at which the entity is moving,
                      in meters per second.
        :param street: A thoroughfare within the locality, or a crossing
                       of two thoroughfares.
        :param text: A catch-all element that captures any other
                     information about the location.
        :param timestamp: UTC timestamp specifying the moment when the
                          reading was taken.
        :param uri: A URI or URL pointing to information about
                    the location.
        :param options: Optional form of publish options.
        """
        options = kwargs.get('options', None)
        ifrom = kwargs.get('ifrom', None)
        callback = kwargs.get('callback', None)
        timeout = kwargs.get('timeout', None)
        for param in ('ifrom', 'block', 'callback', 'timeout', 'options'):
            if param in kwargs:
                del kwargs[param]

        geoloc = Geoloc()
        geoloc.values = kwargs

        return self.xmpp['xep_0163'].publish(
            geoloc,
            options=options,
            ifrom=ifrom,
            callback=callback,
            timeout=timeout,
        )

    def stop(self, ifrom: Optional[JID] = None,
             callback: Optional[Callable] = None,
             timeout: Optional[int] = None) -> Future:
        """
        Clear existing user location information to stop notifications.
        """
        geoloc = Geoloc()
        return self.xmpp['xep_0163'].publish(
            geoloc,
            ifrom=ifrom,
            callback=callback,
            timeout=timeout,
        )
