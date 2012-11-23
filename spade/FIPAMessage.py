# -*- coding: utf-8 -*-

class FipaMessage:
    """
    This object contains the envelope and payload (body) of a fipa message
    """

    def __init__(self, messageEnvelopes, messageBody):
        self.__messageEnvelopes = messageEnvelopes
        self.__messageBody = messageBody
        self.__messageEnvelopes.setPayloadLength(str(len(str(self.__messageBody))))

    def getEnvelope(self):
        return self.__messageEnvelopes

    def getBody(self):
        return self.__messageBody
