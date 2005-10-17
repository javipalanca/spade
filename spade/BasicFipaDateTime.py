"""
 * Java Agent Message Router - JAMR ( http://liawww.epfl.ch/~cion/jamr ) 
 * FIPA compliant Message Transport Implementation
 *
 * Copyright (C) 2000, 2001, Laboratoire d'Intelligence Artificielle,
 * Echole Polytechnique Federale de Lausanne ( http://liawww.epfl.ch )
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software foundation
 *
 *
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
 * General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library (file lesser.txt); if not, try downloading it
 * from http://www.gnu.org/copyleft/lesser.txt or write to the Free
 * Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *
 * BasicFipaDateTime.java
 *
 *
 * Created: Mon Aug 28 22:41:41 2000
 *
 * @author Ion Constantinescu ( ion.constantinescu@epfl.ch )
 * @version 0.72
 * @author Nicolas Lhuillier (Motorola Labs)
 * Corrected bug with Java Calendar class
 * @version 1.0
"""

from datetime import datetime


class BasicFipaDateTime:

	def __init__(self,date = None):
		if (date == None):
			self.fromDateTime(datetime.now())
		else:
			if (isinstance(date,str) == True):
				self.fromString(date)
			elif (isinstance(date, datetime) == True):
				self.fromDateTime(date)
	
		
	def fromDateTime(self, dt):
		self.calendar = dt

	def fromString(self, string):
		if string != None and string != "":
			#print "string: " + str(string)
			
			year = int(string[0:4])
			month = int(string[4:6])
			day = int(string[6:8])
			#tz = str[8]
			hour = int(string[9:11])
			minute = int(string[11:13])
			second = int(string[13:15])
			milli = int(string[15:18])

			self.calendar = datetime(year,month,day,hour,minute,second,milli)
			
			return True
		else:
			return False




	def getYear(self):
		return self.calendar.year

	def setYear(self,year):
		self.calendar = datetime(year,self.getMonth(), self.getDay(),self.getHour(),self.getMinutes(),self.getSeconds(),self.getMilliseconds(),self.getTypeDesignator())

	def getMonth(self):
		return self.calendar.month

	def setMonth(self,month):
		self.calendar = datetime(self.calendar.year,month, self.calendar.day,self.calendar.hour,self.calendar.minute,self.calendar.second,self.calendar.microsecond,self.calendar.tzinfo)
	
	def getDay(self):
		return self.calendar.day

	def setDay(self,day):
		self.calendar = datetime(self.calendar.year,self.calendar.month,day,self.calendar.hour,self.calendar.minute,self.calendar.second,self.calendar.microsecond,self.calendar.tzinfo)

	def getHour(self):
		return self.calendar.hour
	
	def setHour(self,hour):
		self.calendar = datetime(self.calendar.year,self.calendar.month, self.calendar.day,hour,self.calendar.minute,self.calendar.second,self.calendar.microsecond,self.calendar.tzinfo)

	def getMinutes(self):
		return self.calendar.minute
	
	def setMinutes(self,minute):
		self.calendar = datetime(self.calendar.year,self.calendar.month, self.calendar.day,self.calendar.hour,minute,self.calendar.second,self.calendar.microsecond,self.calendar.tzinfo)

	def getSeconds(self):
		return self.calendar.second

	def setSeconds(self,second):
		self.calendar = datetime(self.calendar.year,self.calendar.month, self.calendar.day,self.calendar.hour,self.calendar.minute,second,self.calendar.microsecond,self.calendar.tzinfo)

	def getMilliseconds(self):
		return self.calendar.microsecond

	def setMilliseconds(self,milli):
		self.calendar = datetime(self.calendar.year,self.calendar.month, self.calendar.day,self.calendar.hour,self.calendar.minute,self.calendat.second,microsecond,self.calendar.tzinfo)

	def getTypeDesignator(self):
		return self.calendar.tzinfo

	def setTypeDesignator(self,tzinfo):
		#self.calendar = datetime(self.calendar.year,self.calendar.month, self.calendar.day,self.calendar.hour,self.calendar.minute,self.calendat.second,self.calendar.microsecond,tzinfo)
		pass

	def paddedInt( self, size, val ):
		res = str(val)
		while len(res) < size:
			res = '0' + res
		return str(res)

	def __str__(self):
		str_date = str(self.getYear()) + self.paddedInt(2,self.getMonth()) + self.paddedInt(2,self.getDay())+"T"
		str_date = str_date + str(self.paddedInt(2,self.getHour()))
		str_date = str_date + str(self.paddedInt(2,self.getMinutes())) + str(self.paddedInt(2,self.getSeconds())) + str(self.paddedInt(3,self.getMilliseconds()))
		
		return str_date;

	def getTime(self):
		return self.__str__()
	
	def getDate(self):
		return self.__str__()
	
	
