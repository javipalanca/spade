
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0221 import stanza, Media, URI
from slixmpp.plugins.xep_0004 import FormField


log = logging.getLogger(__name__)


class XEP_0221(BasePlugin):
    """
    XEP-0221: Data Forms Media Element

    In certain implementations of Data Forms (XEP-0004), it can be
    helpful to include media data such as small images. One example is
    CAPTCHA Forms (XEP-0158). This plugin implements a method for
    including media data in a data form.

    Typical use pattern:

    .. code-block:: python

        self.register_plugin('xep_0221')
        self['xep_0050'].add_command(node="showimage",
                                        name="Show my image",
                                        handler=self.form_handler)

        def form_handler(self,iq,session):
            image_url="https://xmpp.org/images/logos/xmpp-logo.svg"
            form=self['xep_0004'].make_form('result','My Image')
            form.addField(var='myimage', ftype='text-single', label='My Image', value=image_url)
            form.field['myimage']['media'].add_uri(value=image_url, itype="image/svg")
            session['payload']=form
            return session
    """


    name = 'xep_0221'
    description = 'XEP-0221: Data Forms Media Element'
    dependencies = {'xep_0004'}

    def plugin_init(self):
        register_stanza_plugin(FormField, Media)
