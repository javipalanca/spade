# -*- coding: utf-8 -*-
from logic import KB, get_object_type, get_object_instance
from pyxf import swipl
import random, string

class SWIKB(KB):
    '''SWI Prolog knowledge base'''
    def __init__(self, sentence=None, path='swipl'):
        '''Constructor method
        Usage: SWIKB( sentence, path )
        sentence - Prolog sentence to be added to the KB (default: None)
        path - path to SWI Prolog executable (default: 'swipl')'''
        self.swi = swipl(path)
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        '''Adds sentence to KB'''
        sentence = sentence.strip()
        if sentence[-1] == '.':
            sentence = sentence[:-1]
        return self.swi.query('assert(' + sentence + ')')

    def ask(self, query):
        '''Queries the KB'''
        return self.swi.query(query)

    def retract(self, sentence):
        '''Deletes sentence from KB'''
        sentence = sentence.strip()
        if sentence[-1] == '.':
            sentence = sentence[:-1]
        return self.swi.query('retract(' + sentence + ')')

    def loadModule(self, module):
        '''Loads module to KB
        Usage: instance.loadModule( path )
        path - path to module'''
        self.swi.load(module)

    def _encode(self, key, value):
        '''Encodes a given key value pair to the knowledge base 
        (internal, for use by kb.KB only)
        Usage: instance._encode( key, value )
        key - the key (variable name) to be encoded
        value - the (Python) value to be encoded'''
        if issubclass(value.__class__, str):
            self.tell("var('" + key + "','" + value + "', str)")

        elif issubclass(value.__class__, int):
            self.tell("var('" + key + "'," + str(value) + ", int)")

        elif issubclass(value.__class__, float):
            self.tell("var('" + key + "', " + str(value) + ", float)")

        elif issubclass(value.__class__, list):
            listID = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
            for elem in value:
                self._encode(listID, elem)
            self.tell("var('" + key + "', '" + listID + "', list)")

        elif issubclass(value.__class__, dict):
            dictID = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
            for k, v in value.items():
                elemID = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
                self._encode(elemID + "Key", k)
                self._encode(elemID + "Value", v)
                self.tell("pair('" + dictID + "','" + elemID + "')")
            self.tell("var('" + key + "','" + dictID + "',dict)")
        elif value is None:
            self.tell("var('" + key + "',none,noneType)")
        else:
            typ = str( value.__module__ + "." + value.__class__.__name__ )
            objID = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
            if value.__dict__ != {}:
                self._encode( objID, value.__dict__ )
            else:
                self.tell( "pair('" + objID + "', empty_object)" ) 
            self.tell( "var('" + key + "', '" + objID + "', '" + typ + "')" )

    def _decode(self, key):
        '''Decodes a given key and return its value from the knowledge base 
        (internal, for use by kb.KB only)
        Usage: instance._decode( key )
        key - the key (variable name) to be decoded'''
        gen = self._gen_decode(key)
        try:
            return gen.next()
        except StopIteration:
            return None

    def _gen_decode(self, key):
        '''Decoding generator
        (internal, for use by kb.KB only)
        Usage: instance._gen_decode( key )
        key - the key (variable name) to be decoded'''
        results = self.ask("var('" + key + "', Value, Type)")
        if isinstance(results, bool):
            yield None
        for res in results:
            value = str( res["Value"] )
            typ = str( res["Type"] )

            if typ == "int":
                yield int(value)
            elif typ == "str":
                yield str(value)
            elif typ == "float":
                yield float(value)
            elif typ == "list":
                l = []
                listID = str(value)
                gen = self._gen_decode(listID)
                hasElements = True
                while hasElements:
                    try:
                        l.append(gen.next())
                    except:
                        hasElements = False
                yield l
            elif typ == "dict":
                dictID = str(value)
                d = {}
                for i in self.ask("pair('" + dictID + "', ElemID)"):
                    elemID = str(i["ElemID"])
                    if elemID == 'empty_object':
                        continue
                    newkey = self._gen_decode(elemID + "Key").next()
                    newvalue = self._gen_decode(elemID + "Value").next()
                    d[newkey] = newvalue
                yield d
            elif typ == "noneType":
                yield None
            else:
                objid = str(key)
                res = self.ask("var('" + objid + "', Value, Type)")[0]
                classname = res["Type"]
                objdict = res["Value"]
                try:
                    module, clas = classname.split(".")
                    obj = get_object_instance(clas, module)
                    d = self._gen_decode(objdict).next()
                    if d == None:
                        d = {}
                        obj.__dict__ = d
                    yield obj
                except:
                    raise GeneratorExit, "No such class in namespace: %s" % classname
                

if __name__ == '__main__':
    kb = SWIKB()
    kb.tell('a(b,c)')
    kb.tell('a(c,d)')
    kb.tell('( p(_X,_Y) :- a(_X,_Y) )')
    kb.tell('( p(_X,_Y) :- a(_X,_Z), p(_Z,_Y) )')
    for result in kb.ask('p(X,Y)'):
        print result
    kb.retract('a(b,c)')
