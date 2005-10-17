"""
   File: ./FIPA/FIPAMESSAGE.JAVA
   From: FIPA.IDL
   Date: Mon Sep 04 15:08:50 2000
     By: idltojava Java IDL 1.2 Nov 10 1997 13:52:11
"""

class FipaMessage:

    def __init__(self, messageEnvelopes, messageBody):
        self.__messageEnvelopes = messageEnvelopes
        self.__messageBody = messageBody

    def getEnvelope(self):
        return self.__messageEnvelopes

    def getBody(self):
        return self.__messageBody

