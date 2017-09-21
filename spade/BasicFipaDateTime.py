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
        if date is None:
            self.from_datetime(datetime.now())
        else:
            if isinstance(date, str) is True:
                self.from_string(date)
            elif isinstance(date, datetime) is True:
                self.from_datetime(date)

        self.calendar = None

    def from_datetime(self, dt):
        """
        inits the object with another BasicFipaDateTime class
        """
        self.calendar = dt

    def from_string(self, string):
        """
        loads the date and time from a string
        """
        if string is not None and string != "":
            year = int(string[0:4])
            month = int(string[4:6])
            day = int(string[6:8])
            hour = int(string[9:11])
            minute = int(string[11:13])
            second = int(string[13:15])
            milli = int(string[15:18])

            self.calendar = datetime(year, month, day, hour, minute, second, milli)

            return True
        else:
            return False

    def get_year(self):
        return self.calendar.year

    def set_year(self, year):
        self.calendar = datetime(year, self.get_month(), self.get_day(), self.get_hour(), self.get_minutes(),
                                 self.get_seconds(), self.get_milliseconds(), self.get_type_designator())

    def get_month(self):
        return self.calendar.month

    def set_month(self, month):
        self.calendar = datetime(self.calendar.year, month, self.calendar.day, self.calendar.hour, self.calendar.minute,
                                 self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def get_day(self):
        return self.calendar.day

    def set_day(self, day):
        self.calendar = datetime(self.calendar.year, self.calendar.month, day, self.calendar.hour, self.calendar.minute,
                                 self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def get_hour(self):
        return self.calendar.hour

    def set_hour(self, hour):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, hour, self.calendar.minute,
                                 self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def get_minutes(self):
        return self.calendar.minute

    def set_minutes(self, minute):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, self.calendar.hour, minute,
                                 self.calendar.second, self.calendar.microsecond, self.calendar.tzinfo)

    def get_seconds(self):
        return self.calendar.second

    def set_seconds(self, second):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, self.calendar.hour,
                                 self.calendar.minute, second, self.calendar.microsecond, self.calendar.tzinfo)

    def get_milliseconds(self):
        return self.calendar.microsecond

    def set_milliseconds(self, milli):
        self.calendar = datetime(self.calendar.year, self.calendar.month, self.calendar.day, self.calendar.hour,
                                 self.calendar.minute, self.calendar.second, milli, self.calendar.tzinfo)

    def get_type_designator(self):
        return self.calendar.tzinfo

    def set_type_designator(self, tzinfo):
        pass

    @staticmethod
    def padded_int(size, val):
        res = str(val)
        while len(res) < size:
            res = '0' + res
        return str(res)

    def __str__(self):
        """
        returns a printable version of the object
        """
        str_date = str(self.get_year()) + self.padded_int(2, self.get_month()) + self.padded_int(2, self.get_day()) + "T"
        str_date = str_date + str(self.padded_int(2, self.get_hour()))
        str_date = str_date + str(self.padded_int(2, self.get_minutes())) + str(self.padded_int(2, self.get_seconds())) + str(self.padded_int(3, self.get_milliseconds()))

        return str_date

    def get_time(self):
        """
        returns a printable version of the object
        """
        return self.__str__()

    def get_date(self):
        """
        returns a printable version of the object
        """
        return self.__str__()
