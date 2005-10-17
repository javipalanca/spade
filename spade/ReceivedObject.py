"""
  File: ./FIPA/RECEIVEDOBJECT.JAVA
  From: FIPA.IDL
  Date: Mon Sep 04 15:08:50 2000
  By: idltojava Java IDL 1.2 Nov 10 1997 13:52:11
"""

class ReceivedObject:

	def __init__(self, by=None, _from=None, date=None, id=None, via=None):
		self.by = by
		self._from = _from
		self.date = date
		self.id = id
		self.via = via

	def getBy(self):
		return self.by
	
	def setBy(self,by):
		self.by = by

	def getFrom(self):
		return self._from
	
	def setFrom(self,_from):
		self._from = _from

	def getDate(self):
		return self.date
	
	def setDate(self,date):
		self.date = date

	def getId(self):
		return self.id
	
	def setId(self,id):
		self.id = id

	def getVia(self):
		return self.via
	
	def setVia(self,via):
		self.via = via

