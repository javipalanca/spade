# -*- coding: utf-8 -*-
from spade.utils import deprecated


class FipaMessage:
    """
    This object contains the envelope and payload (body) of a fipa message
    """

    def __init__(self, messageEnvelopes, messageBody):
        self.__messageEnvelopes = messageEnvelopes
        self.__messageBody = messageBody
        self.__messageEnvelopes.setPayloadLength(str(len(str(self.__messageBody))))

    def get_envelope(self):
        return self.__messageEnvelopes

    getEnvelope = deprecated(get_envelope, "getEnvelope")

    def get_body(self):
        return self.__messageBody

    getBody = deprecated(get_body, "getBody")
