# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging

from asyncio import Future
from typing import Optional
from slixmpp.plugins.base import BasePlugin
from slixmpp.plugins.xep_0108 import stanza, UserActivity


log = logging.getLogger(__name__)


class XEP_0108(BasePlugin):

    """
    XEP-0108: User Activity
    """

    name = 'xep_0108'
    description = 'XEP-0108: User Activity'
    dependencies = {'xep_0163'}
    stanza = stanza

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=UserActivity.namespace)
        self.xmpp['xep_0163'].remove_interest(UserActivity.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0163'].register_pep('user_activity', UserActivity)

    def publish_activity(self, general: str, specific: Optional[str] = None,
                         text: Optional[str] = None, **pubsubkwargs) -> Future:
        """
        Publish the user's current activity.

        :param general: The required general category of the activity.
        :param specific: Optional specific activity being done as part
                         of the general category.
        :param text: Optional natural-language description or reason
                     for the activity.
        """
        activity = UserActivity()
        activity['value'] = (general, specific)
        activity['text'] = text
        return self.xmpp['xep_0163'].publish(
            activity,
            node=UserActivity.namespace,
            **pubsubkwargs
        )

    def stop(self, **pubsubkwargs) -> Future:
        """
        Clear existing user activity information to stop notifications.
        """
        activity = UserActivity()
        return self.xmpp['xep_0163'].publish(
            activity,
            node=UserActivity.namespace,
            **pubsubkwargs
        )
