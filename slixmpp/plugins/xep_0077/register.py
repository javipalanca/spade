
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
import ssl

from slixmpp.stanza import StreamFeatures, Iq
from slixmpp.xmlstream import register_stanza_plugin, JID
from slixmpp.xmlstream.handler import CoroutineCallback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0077 import stanza, Register, RegisterFeature


log = logging.getLogger(__name__)


class XEP_0077(BasePlugin):

    """
    XEP-0077: In-Band Registration

    Events:

    ::

        user_register           -- After succesful validation and add to the user store
                                   in api["user_validate"]
        user_unregister         -- After succesful user removal in api["user_remove"]

    Config:

    ::

        form_fields are only form_instructions are only used for component registration
        in case api["make_registration_form"] is not overriden.

    API:

    ::

        user_get(jid, node, ifrom, iq)
            Returns a dict-like object containing `form_fields` for this user or None
        user_remove(jid, node, ifrom, iq)
            Removes a user or raise KeyError in case the user is not found in the user store
        make_registration_form(self, jid, node, ifrom, iq)
            Returns an iq reply to a registration form request, pre-filled and with
            <registered/> in case the requesting entity is already registered to us
        user_validate((self, jid, node, ifrom, registration)
            Add the user to the user store or raise ValueError(msg) if any problem is encountered
            msg is sent back to the XMPP client as an error message.
    """

    name = 'xep_0077'
    description = 'XEP-0077: In-Band Registration'
    dependencies = {'xep_0004', 'xep_0066'}
    stanza = stanza
    default_config = {
        'create_account': True,
        'force_registration': False,
        'order': 50,
        "form_fields": {"username", "password"},
        "form_instructions": "Enter your credentials",
    }

    def plugin_init(self):
        register_stanza_plugin(StreamFeatures, RegisterFeature)
        register_stanza_plugin(Iq, Register)

        if self.xmpp.is_component:
            self.xmpp["xep_0030"].add_feature("jabber:iq:register")
            self.xmpp.register_handler(
                CoroutineCallback(
                    "registration",
                    StanzaPath("/iq/register"),
                    self._handle_registration,
                )
            )
            self._user_store = {}
            self.api.register(self._user_get, "user_get")
            self.api.register(self._user_remove, "user_remove")
            self.api.register(self._make_registration_form, "make_registration_form")
            self.api.register(self._user_validate, "user_validate")
        else:
            self.xmpp.register_feature(
                "register",
                self._handle_register_feature,
                restart=False,
                order=self.order,
            )

        register_stanza_plugin(Register, self.xmpp['xep_0004'].stanza.Form)
        register_stanza_plugin(Register, self.xmpp['xep_0066'].stanza.OOB)

        self.xmpp.add_event_handler('connected', self._force_registration)

    def plugin_end(self):
        if not self.xmpp.is_component:
            self.xmpp.unregister_feature('register', self.order)

    def _user_get(self, jid, node, ifrom, iq):
        return self._user_store.get(iq["from"].bare)

    def _user_remove(self, jid, node, ifrom, iq):
        return self._user_store.pop(iq["from"].bare)

    async def _make_registration_form(self, jid, node, ifrom, iq: Iq):
        reg = iq["register"]
        user = await self.api["user_get"](None, None, iq['from'], iq)

        if user is None:
            user = {}
        else:
            reg["registered"] = True

        reg["instructions"] = self.form_instructions

        for field in self.form_fields:
            data = user.get(field, "")
            if data:
                reg[field] = data
            else:
                # Add a blank field
                reg.add_field(field)

        reply = iq.reply()
        reply.set_payload(reg.xml)
        return reply

    def _user_validate(self, jid, node, ifrom, registration):
        self._user_store[ifrom.bare] = {key: registration[key] for key in self.form_fields}

    async def _handle_registration(self, iq: Iq):
        if iq["type"] == "get":
            await self._send_form(iq)
        elif iq["type"] == "set":
            if iq["register"]["remove"]:
                try:
                    await self.api["user_remove"](None, None, iq["from"], iq)
                except KeyError:
                    _send_error(
                        iq,
                        "404",
                        "cancel",
                        "item-not-found",
                        "User not found",
                    )
                else:
                    reply = iq.reply()
                    reply.send()
                    self.xmpp.event("user_unregister", iq)
                return


            for field in self.form_fields:
                if not iq["register"][field]:
                    # Incomplete Registration
                    _send_error(
                        iq,
                        "406",
                        "modify",
                        "not-acceptable",
                        "Please fill in all fields.",
                    )
                    return

            try:
                await self.api["user_validate"](None, None, iq["from"], iq["register"])
            except ValueError as e:
                _send_error(
                    iq,
                    "406",
                    "modify",
                    "not-acceptable",
                    e.args,
                )
            else:
                reply = iq.reply()
                reply.send()
                self.xmpp.event("user_register", iq)

    async def _send_form(self, iq):
        reply = await self.api["make_registration_form"](None, None, iq["from"], iq)
        reply.send()

    def _force_registration(self, event):
        if self.force_registration:
            self.xmpp.add_filter('in', self._force_stream_feature)

    def _force_stream_feature(self, stanza):
        if isinstance(stanza, StreamFeatures):
            if self.xmpp.enable_starttls:
                if 'starttls' not in self.xmpp.features:
                    return stanza
                elif not isinstance(self.xmpp.socket, ssl.SSLSocket):
                    return stanza
            if 'mechanisms' not in self.xmpp.features:
                log.debug('Forced adding in-band registration stream feature')
                stanza.enable('register')
                self.xmpp.del_filter('in', self._force_stream_feature)
        return stanza

    async def _handle_register_feature(self, features):
        if 'mechanisms' in self.xmpp.features:
            # We have already logged in with an account
            return False

        if self.create_account and self.xmpp.event_handled('register'):
            form = await self.get_registration()
            await self.xmpp.event_async('register', form)
            return True
        return False

    def get_registration(self, jid=None, ifrom=None,
                         timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['to'] = jid
        iq['from'] = ifrom
        iq.enable('register')
        return iq.send(timeout=timeout, callback=callback)

    def cancel_registration(self, jid=None, ifrom=None,
                            timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['to'] = jid
        iq['from'] = ifrom
        iq['register']['remove'] = True
        return iq.send(timeout=timeout, callback=callback)

    def change_password(self, password, jid=None, ifrom=None,
                        timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['to'] = jid
        iq['from'] = ifrom
        if self.xmpp.is_component:
            ifrom = JID(ifrom)
            iq['register']['username'] = ifrom.user
        else:
            iq['register']['username'] = self.xmpp.boundjid.user
        iq['register']['password'] = password
        return iq.send(timeout=timeout, callback=callback)

def _send_error(iq, code, error_type, name, text=""):
    # It would be nice to raise XMPPError but the iq payload
    # should include the register info
    reply = iq.reply()
    reply.set_payload(iq["register"].xml)
    reply.error()
    reply["error"]["code"] = code
    reply["error"]["type"] = error_type
    reply["error"]["condition"] = name
    reply["error"]["text"] = text
    reply.send()
