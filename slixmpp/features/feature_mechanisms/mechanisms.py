# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import ssl
import logging

from slixmpp.util import sasl
from slixmpp.util.stringprep_profiles import StringPrepError
from slixmpp.stanza import StreamFeatures
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream.matcher import MatchXPath
from slixmpp.xmlstream.handler import Callback
from slixmpp.features.feature_mechanisms import stanza

from typing import ClassVar, Set


log = logging.getLogger(__name__)


class FeatureMechanisms(BasePlugin):

    name = 'feature_mechanisms'
    description = 'RFC 6120: Stream Feature: SASL'
    dependencies: ClassVar[Set[str]] = set()
    stanza = stanza
    default_config = {
        'use_mech': None,
        'use_mechs': None,
        'min_mech': None,
        'sasl_callback': None,
        'security_callback': None,
        'encrypted_plain': True,
        'unencrypted_plain': False,
        'unencrypted_digest': False,
        'unencrypted_cram': False,
        'unencrypted_scram': False,
        'order': 100,
        'tls_version': None,
    }

    def plugin_init(self):
        if self.sasl_callback is None:
            self.sasl_callback = self._default_credentials

        if self.security_callback is None:
            self.security_callback = self._default_security

        creds = self.sasl_callback({'username'}, set())
        if not self.use_mech and not creds['username']:
            self.use_mech = 'ANONYMOUS'

        self.mech = None
        self.mech_list = set()
        self.attempted_mechs = set()

        register_stanza_plugin(StreamFeatures, stanza.Mechanisms)

        self.xmpp.register_stanza(stanza.Success)
        self.xmpp.register_stanza(stanza.Failure)
        self.xmpp.register_stanza(stanza.Auth)
        self.xmpp.register_stanza(stanza.Challenge)
        self.xmpp.register_stanza(stanza.Response)
        self.xmpp.register_stanza(stanza.Abort)

        self.xmpp.register_handler(
                Callback('SASL Success',
                         MatchXPath(stanza.Success.tag_name()),
                         self._handle_success,
                         instream=True))
        self.xmpp.register_handler(
                Callback('SASL Failure',
                         MatchXPath(stanza.Failure.tag_name()),
                         self._handle_fail,
                         instream=True))
        self.xmpp.register_handler(
                Callback('SASL Challenge',
                         MatchXPath(stanza.Challenge.tag_name()),
                         self._handle_challenge))

        self.xmpp.register_feature('mechanisms',
                self._handle_sasl_auth,
                restart=True,
                order=self.order)

    def _default_credentials(self, required_values, optional_values):
        creds = self.xmpp.credentials
        result = {}
        values = required_values.union(optional_values)
        for value in values:
            if value == 'username':
                result[value] = creds.get('username', self.xmpp.requested_jid.user)
            elif value == 'email':
                jid = self.xmpp.requested_jid.bare
                result[value] = creds.get('email', jid)
            elif value == 'channel_binding':
                if isinstance(self.xmpp.socket, (ssl.SSLSocket, ssl.SSLObject)):
                    version = self.xmpp.socket.version()
                    # As of now, python does not implement anything else
                    # than tls-unique, which is forbidden on TLSv1.3
                    # see https://github.com/python/cpython/issues/95341
                    if version != 'TLSv1.3':
                        result[value] = self.xmpp.socket.get_channel_binding(
                            cb_type="tls-unique"
                        )
                    elif 'tls-exporter' in ssl.CHANNEL_BINDING_TYPES:
                        result[value] = self.xmpp.socket.get_channel_binding(
                            cb_type="tls-exporter"
                        )
                    else:
                        result[value] = None
                else:
                    result[value] = None
            elif value == 'host':
                result[value] = creds.get('host', self.xmpp.requested_jid.domain)
            elif value == 'realm':
                result[value] = creds.get('realm', self.xmpp.requested_jid.domain)
            elif value == 'service-name':
                result[value] = creds.get('service-name', self.xmpp._service_name)
            elif value == 'service':
                result[value] = creds.get('service', 'xmpp')
            elif value in creds:
                result[value] = creds[value]
        return result

    def _default_security(self, values):
        result = {}
        for value in values:
            if value == 'encrypted':
                if 'starttls' in self.xmpp.features:
                    result[value] = True
                elif isinstance(self.xmpp.socket, (ssl.SSLSocket, ssl.SSLObject)):
                    result[value] = True
                else:
                    result[value] = False
            elif value == 'tls_version':
                if isinstance(self.xmpp.socket, (ssl.SSLSocket, ssl.SSLObject)):
                    result[value] = self.xmpp.socket.version()
            elif value == 'binding_proposed':
                result[value] = any(x for x in self.mech_list if x.endswith('-PLUS'))
            else:
                result[value] = self.config.get(value, False)
        return result

    def _handle_sasl_auth(self, features):
        """
        Handle authenticating using SASL.

        Arguments:
            features -- The stream features stanza.
        """
        if 'mechanisms' in self.xmpp.features:
            # SASL authentication has already succeeded, but the
            # server has incorrectly offered it again.
            return False

        enforce_limit = False
        limited_mechs = self.use_mechs

        if limited_mechs is None:
            limited_mechs = set()
        elif limited_mechs and not isinstance(limited_mechs, set):
            limited_mechs = set(limited_mechs)
            enforce_limit = True

        if self.use_mech:
            limited_mechs.add(self.use_mech)
            enforce_limit = True

        if enforce_limit:
            self.use_mechs = limited_mechs

        self.mech_list = set(features['mechanisms'])

        return self._send_auth()

    def _send_auth(self):
        mech_list = self.mech_list - self.attempted_mechs
        try:
            self.mech = sasl.choose(mech_list,
                                    self.sasl_callback,
                                    self.security_callback,
                                    limit=self.use_mechs,
                                    min_mech=self.min_mech)
        except sasl.SASLNoAppropriateMechanism:
            log.error("No appropriate login method.")
            self.xmpp.event("failed_all_auth")
            if not self.attempted_mechs:
                # Only trigger this event if we didn't try at least one
                # method
                self.xmpp.event("no_auth")
            self.attempted_mechs = set()
            return self.xmpp.disconnect()
        except StringPrepError:
            log.exception("A credential value did not pass SASLprep.")
            self.xmpp.disconnect()

        resp = stanza.Auth(self.xmpp)
        resp['mechanism'] = self.mech.name
        try:
            resp['value'] = self.mech.process()
        except sasl.SASLCancelled:
            self.attempted_mechs.add(self.mech.name)
            self._send_auth()
        except sasl.SASLMutualAuthFailed:
            log.error("Mutual authentication failed! " + \
                      "A security breach is possible.")
            self.attempted_mechs.add(self.mech.name)
            self.xmpp.disconnect()
        except sasl.SASLFailed:
            self.attempted_mechs.add(self.mech.name)
            self._send_auth()
        else:
            resp.send()

        return True

    def _handle_challenge(self, stanza):
        """SASL challenge received. Process and send response."""
        resp = self.stanza.Response(self.xmpp)
        try:
            resp['value'] = self.mech.process(stanza['value'])
        except sasl.SASLCancelled:
            self.stanza.Abort(self.xmpp).send()
        except sasl.SASLMutualAuthFailed:
            log.error("Mutual authentication failed! " + \
                      "A security breach is possible.")
            self.attempted_mechs.add(self.mech.name)
            self.xmpp.disconnect()
        except sasl.SASLFailed:
            self.stanza.Abort(self.xmpp).send()
        else:
            if resp.get_value() == '':
                resp.del_value()
            resp.send()

    def _handle_success(self, stanza):
        """SASL authentication succeeded. Restart the stream."""
        try:
            final = self.mech.process(stanza['value'])
        except sasl.SASLMutualAuthFailed:
            log.error("Mutual authentication failed! " + \
                      "A security breach is possible.")
            self.attempted_mechs.add(self.mech.name)
            self.xmpp.disconnect()
        else:
            self.attempted_mechs = set()
            self.xmpp.authenticated = True
            self.xmpp.features.add('mechanisms')
            self.xmpp.event('auth_success', stanza)
            # Restart the stream
            self.xmpp.init_parser()
            self.xmpp.send_raw(self.xmpp.stream_header)

    def _handle_fail(self, stanza):
        """SASL authentication failed. Disconnect and shutdown."""
        self.attempted_mechs.add(self.mech.name)
        log.info("Authentication failed: %s", stanza['condition'])
        self.xmpp.event("failed_auth", stanza)
        self._send_auth()
        return True
