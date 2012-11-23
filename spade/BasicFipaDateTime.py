# -*- coding: utf-8 -*-
from datetime import datetime


class BasicFipaDateTime:
    """
    Help class to operate dates and times
    """

    def __init__(self, date=None):
        """
        constructor
        date parameter can be suplied
        """
        if (date is None):
            self.fromDateTime(datetime.now())
        else:
            if isinstance(date, str) is True:
                self.fromString(date)
            elif isinstance(date, datetime) is True:
                self.fromDateTime(date)

    def fromDateTime(self, dt):
        """
        inits the object with another BasicFipaDateTime class
        """
        self.calendar = dt

    def fromString(self, string):
        """
        loads the date and time from a string
        """
        if string is not None and string != "":
            #print "string: " + str(string)

            year = int(string[0:4])
            month = int(string[4:6])
            day = int(string[6:8])
            #tz = str[8]
            hour = int(string[9:11])
            minute = int(string[11:13])
            second = int(string[13:15])
            milli = int(string[15:18])

            self.calendar = datetime(year, month, day, hour, minute, second, milli)

            return True
        else:
            return False

    def getYear(self):
        return self.calendar.year

    def setYear(self, year):
        self.calendar = datetime(year, self.getMonth(), self.getDay(), self.getHour(), self.getMinutes(), self.getSeconds(), self.getMilliseconds(), self.getTypeDesignator())

    def getMonth(self):
        return self.calendar.month

    def setMonth(self, month):
        self.calendar = datetime(self.calendar.year, month, self.calendar.day, self.calendar.hour, self.calendar.minute, self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def getDay(self):
        return self.calendar.day

    def setDay(self, day):
        self.calendar = datetime(self.calendar.year, self.calendar.month, day, self.calendar.hour, self.calendar.minute, self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def getHour(self):
        return self.calendar.hour

    def setHour(self, hour):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, hour, self.calendar.minute, self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def getMinutes(self):
        return self.calendar.minute

    def setMinutes(self, minute):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, self.calendar.hour, minute, self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def getSeconds(self):
        return self.calendar.second

    def setSeconds(self, second):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, self.calendar.hour, self.calendar.minute, second, self.calendar.microsecond, self.calendar.tzinfo)

    def getMilliseconds(self):
        return self.calendar.microsecond

    def setMilliseconds(self, milli):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, self.calendar.hour, self.calendar.minute, self.calendat.second, microsecond, self.calendar.tzinfo)

    def getTypeDesignator(self):
        return self.calendar.tzinfo

    def setTypeDesignator(self, tzinfo):
        #self.calendar = datetime(self.calendar.year,self.calendar.month, self.calendar.day,self.calendar.hour,self.calendar.minute,self.calendat.second,self.calendar.microsecond,tzinfo)
        pass

    def paddedInt(self, size, val):
        res = str(val)
        while len(res) < size:
            res = '0' + res
        return str(res)

    def __str__(self):
        """
        returns a printable version of the object
        """
        str_date = str(self.getYear()) + self.paddedInt(2, self.getMonth()) + self.paddedInt(2, self.getDay()) + "T"
        str_date = str_date + str(self.paddedInt(2, self.getHour()))
        str_date = str_date + str(self.paddedInt(2, self.getMinutes())) + str(self.paddedInt(2, self.getSeconds())) + str(self.paddedInt(3, self.getMilliseconds()))

        return str_date

    def getTime(self):
        """
        returns a printable version of the object
        """
        return self.__str__()

    def getDate(self):
        """
        returns a printable version of the object
        """
        return self.__str__()
