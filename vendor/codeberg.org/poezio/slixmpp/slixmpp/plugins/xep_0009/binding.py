
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Dann Martens (TOMOTON).
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ET
import base64
import logging
import time

log = logging.getLogger(__name__)

_namespace = 'jabber:iq:rpc'

def fault2xml(fault):
    value = dict()
    value['faultCode'] = fault['code']
    value['faultString'] = fault['string']
    fault = ET.Element("fault", {'xmlns': _namespace})
    fault.append(_py2xml((value)))
    return fault

def xml2fault(params):
    vals = []
    for value in params.findall('{%s}value' % _namespace):
        vals.append(_xml2py(value))
    fault = dict()
    fault['code'] = vals[0]['faultCode']
    fault['string'] = vals[0]['faultString']
    return fault

def py2xml(*args):
    params = ET.Element("{%s}params" % _namespace)
    for x in args:
        param = ET.Element("{%s}param" % _namespace)
        param.append(_py2xml(x))
        params.append(param) #<params><param>...
    return params

def _py2xml(*args):
    for x in args:
        val = ET.Element("{%s}value" % _namespace)
        if x is None:
            nil = ET.Element("{%s}nil" % _namespace)
            val.append(nil)
        elif type(x) is int:
            i4 = ET.Element("{%s}i4" % _namespace)
            i4.text = str(x)
            val.append(i4)
        elif type(x) is bool:
            boolean = ET.Element("{%s}boolean" % _namespace)
            boolean.text = str(int(x))
            val.append(boolean)
        elif type(x) is str:
            string = ET.Element("{%s}string" % _namespace)
            string.text = x
            val.append(string)
        elif type(x) is float:
            double = ET.Element("{%s}double" % _namespace)
            double.text = str(x)
            val.append(double)
        elif type(x) is rpcbase64:
            b64 = ET.Element("{%s}base64" % _namespace)
            b64.text = x.encoded()
            val.append(b64)
        elif type(x) is rpctime:
            iso = ET.Element("{%s}dateTime.iso8601" % _namespace)
            iso.text = str(x)
            val.append(iso)
        elif type(x) in (list, tuple):
            array = ET.Element("{%s}array" % _namespace)
            data = ET.Element("{%s}data" % _namespace)
            for y in x:
                data.append(_py2xml(y))
            array.append(data)
            val.append(array)
        elif type(x) is dict:
            struct = ET.Element("{%s}struct" % _namespace)
            for y in x.keys():
                member = ET.Element("{%s}member" % _namespace)
                name = ET.Element("{%s}name" % _namespace)
                name.text = y
                member.append(name)
                member.append(_py2xml(x[y]))
                struct.append(member)
            val.append(struct)
        return val

def xml2py(params):
    namespace = 'jabber:iq:rpc'
    vals = []
    for param in params.findall('{%s}param' % namespace):
        vals.append(_xml2py(param.find('{%s}value' % namespace)))
    return vals

def _xml2py(value):
    namespace = 'jabber:iq:rpc'
    find_value = value.find
    if find_value('{%s}nil' % namespace) is not None:
        return None
    if find_value('{%s}i4' % namespace) is not None:
        return int(find_value('{%s}i4' % namespace).text)
    if find_value('{%s}int' % namespace) is not None:
        return int(find_value('{%s}int' % namespace).text)
    if find_value('{%s}boolean' % namespace) is not None:
        return bool(int(find_value('{%s}boolean' % namespace).text))
    if find_value('{%s}string' % namespace) is not None:
        return find_value('{%s}string' % namespace).text
    if find_value('{%s}double' % namespace) is not None:
        return float(find_value('{%s}double' % namespace).text)
    if find_value('{%s}base64' % namespace) is not None:
        return rpcbase64(find_value('{%s}base64' % namespace).text.encode())
    if find_value('{%s}Base64' % namespace) is not None:
        # Older versions of XEP-0009 used Base64
        return rpcbase64(find_value('{%s}Base64' % namespace).text.encode())
    if find_value('{%s}dateTime.iso8601' % namespace) is not None:
        return rpctime(find_value('{%s}dateTime.iso8601' % namespace).text)
    if find_value('{%s}struct' % namespace) is not None:
        struct = {}
        for member in find_value('{%s}struct' % namespace).findall('{%s}member' % namespace):
            struct[member.find('{%s}name' % namespace).text] = _xml2py(member.find('{%s}value' % namespace))
        return struct
    if find_value('{%s}array' % namespace) is not None:
        array = []
        for val in find_value('{%s}array' % namespace).find('{%s}data' % namespace).findall('{%s}value' % namespace):
            array.append(_xml2py(val))
        return array
    raise ValueError()


class rpcbase64:

    def __init__(self, data):
        #base 64 encoded string
        self.data = data

    def decode(self):
        return base64.b64decode(self.data)

    def __str__(self):
        return self.decode().decode()

    def encoded(self):
        return self.data.decode()



class rpctime:

    def __init__(self,data=None):
        #assume string data is in iso format YYYYMMDDTHH:MM:SS
        if type(data) is str:
            self.timestamp = time.strptime(data,"%Y%m%dT%H:%M:%S")
        elif type(data) is time.struct_time:
            self.timestamp = data
        elif data is None:
            self.timestamp = time.gmtime()
        else:
            raise ValueError()

    def iso8601(self):
        #return a iso8601 string
        return time.strftime("%Y%m%dT%H:%M:%S",self.timestamp)

    def __str__(self):
        return self.iso8601()
