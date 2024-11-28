import ssl

from slixmpp import ClientXMPP
import logging

from slixmpp.exceptions import IqError, IqTimeout


class RegistrationException(Exception):
    pass


class XMPPClient(ClientXMPP):
    def __init__(self, jid, password, verify_security, auto_register):
        ClientXMPP.__init__(self, jid, password)

        self.logger = logging.getLogger("spade.Agent")

        if not verify_security:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

        self.add_event_handler("session_start", self.session_start)
        self.register_plugin("xep_0199")  # XMPP Ping

        if auto_register:
            self.add_event_handler("register", self.register)
            self.register_plugin("xep_0077")  # In-band-registration

        self.register_plugin("xep_0199")  # Ping / Keepalive connection
        self["xep_0199"].enable_keepalive(interval=55)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    async def register(self, event):
        resp = self.Iq()
        resp["type"] = "set"
        resp["register"]["username"] = self.boundjid.user
        resp["register"]["password"] = self.password

        try:
            await resp.send()
        except IqError:
            """
                If the user is already registered, it will return an IQ error
                We can safely ignore it. The client will try the auth process
                right after the ibr process
            """
            pass
        except IqTimeout:
            raise RegistrationException("Timeout error during the register process.")
