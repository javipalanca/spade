# -*- coding: utf-8 -*-
import random
import string

from .logic import FolKB, fol_bc_ask, expr, is_definite_clause, variables, get_object_instance
from .utils import deprecated


class KBNameNotString(Exception):
    pass


class KBValueNotKnown(Exception):
    pass


class KBConfigurationFailed(Exception):
    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class SpadeKB(FolKB):
    def tell(self, sentence):
        if issubclass(sentence.__class__, str):
            sentence = expr(sentence)
        if is_definite_clause(sentence):
            self.clauses.append(sentence)
        else:
            raise Exception("Not a definite clause: %s" % sentence)

    def retract(self, sentence):
        if issubclass(sentence.__class__, str):
            sentence = expr(sentence)
        self.clauses.remove(sentence)

    def ask(self, q):
        e = expr(q)
        vars = variables(e)
        ans = fol_bc_ask(self, [e])
        res = []
        for a in ans:
            res.append(dict([(x, v) for (x, v) in list(a.items()) if x in vars]))
        res.sort(key=str)

        if res == []:
            return False
        for r in res:
            if r != {}:
                return res
        return True  # res is a list of empty dicts

    def _encode(self, key, value):
        key = key.capitalize()
        if issubclass(value.__class__, str):
            self.tell("Var(" + key + "," + value.capitalize() + ",Str)")

        elif issubclass(value.__class__, int):
            self.tell("Var(" + key + "," + str(value) + ",Int)")

        elif issubclass(value.__class__, float):
            self.tell("Var(" + key + "," + str(value) + ",Float)")

        elif issubclass(value.__class__, list):
            list_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
            list_id = list_id.capitalize()  # list_id.replace(list_id[0],list_id[0].lower(),1)
            for elem in value:
                self._encode(list_id, elem)
            self.tell("Var(" + key + "," + list_id + ",List)")

        elif issubclass(value.__class__, dict):
            dict_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
            dict_id = dict_id.capitalize()  # list_id.replace(list_id[0],list_id[0].lower(),1)
            for k, v in list(value.items()):
                elemID = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
                elemID = elemID.capitalize()  # elemID.replace(elemID[0],elemID[0].lower(),1)
                self._encode(elemID + "Key", k)
                self._encode(elemID + "Value", v)
                self.tell("Pair(" + dict_id + "," + elemID + ")")
            self.tell("Var(" + key + "," + dict_id + ",Dict)")
        elif value is None:
            self.tell("Var(" + key + ",None,NoneType)")
        else:
            try:
                typ = str(value.__module__ + "." + value.__class__.__name__)
                objID = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(8))
                objID = objID.capitalize()
                if value.__dict__ != {}:
                    self._encode(objID, value.__dict__)
                else:
                    self.tell("Pair(" + objID + ", Empty_object)")
                    self.tell("Var(" + key + ", " + objID + ", " + typ + ")")
            except:
                raise KBValueNotKnown

    def _decode(self, key):
        gen = self._gen_decode(key)
        try:
            return next(gen)
        except StopIteration:
            return None

    def _gen_decode(self, key):
        key = key.capitalize()
        results = self.ask("Var(" + key + ", value, type)")
        if isinstance(results, bool):
            yield None
        for res in results:
            value = str(res[expr("value")])
            typ = str(res[expr("type")])

            if typ == "Int":
                yield int(value)
            elif typ == "Str":
                yield str(value).lower()
            elif typ == "Float":
                yield float(value)
            elif typ == "List":
                l = []
                listID = str(value)
                gen = self._gen_decode(listID)
                hasElements = True
                while hasElements:
                    try:
                        l.append(next(gen))
                    except:
                        hasElements = False
                yield l
            elif typ == "Dict":
                dictID = str(value)
                d = {}
                for i in self.ask("Pair(" + dictID + ", elemid)"):
                    elemID = str(i[expr("elemid")])
                    if elemID == "Empty_object":
                        continue
                    newkey = next(self._gen_decode(elemID + "Key"))
                    newvalue = next(self._gen_decode(elemID + "Value"))
                    d[newkey] = newvalue
                yield d
            elif typ == "NoneType":
                yield None
            else:
                objid = str(key)
                res = self.ask("Var(" + objid + ", value, type)")[0]
                classname = str(res[expr("type")])
                objdict = str(res[expr("value")])
                try:
                    module, clas = classname.split(".")
                    obj = get_object_instance(clas, module)
                    d = next(self._gen_decode(objdict))
                    if d is None:
                        d = {}
                        obj.__dict__ = d
                        yield obj
                except:
                    raise GeneratorExit("No such class in namespace: %s" % classname)


class KB:
    def __init__(self):
        self.kb = SpadeKB()
        self.type = "Spade"

    def configure(self, typ, sentence=None, path=None):
        """
        Supported Knowledge Bases are: ["ECLiPSe", "Flora2", "SPARQL", "SWI", "XSB", "Spade"]
        """
        try:
            if typ not in ["ECLiPSe", "Flora2", "SPARQL", "SWI", "XSB", "Spade"]:
                raise KBConfigurationFailed(typ + " is not a valid KB.")
            if typ == "Spade":
                self.kb = SpadeKB()
                return
            elif typ == "SPARQL":
                from . import SPARQLKB
            elif typ == "XSB":
                from . import XSBKB
            elif typ == "Flora2":
                from . import Flora2KB
            elif typ == "SWI":
                from . import SWIKB
            elif typ == "ECLiPSe":
                from . import ECLiPSeKB
            else:
                raise KBConfigurationFailed("Could not import " + str(typ) + " KB.")

        except KBConfigurationFailed as e:
            # self.myAgent.DEBUG(str(e)+" Using Fol KB.", 'warn')
            typ = "Spade"

        self.type = typ

        if typ == "Spade":
            self.kb = SpadeKB()
        elif typ == "SPARQL":
            self.kb = SPARQLKB.SPARQLKB(sentence=sentence, path=path)
        elif typ == "XSB":
            self.kb = XSBKB.XSBKB(sentence=sentence, path=path)
        elif typ == "Flora2":
            self.kb = Flora2KB.Flora2KB(sentence=sentence, path=path)
        elif typ == "SWI":
            self.kb = SWIKB.SWIKB(sentence=sentence, path=path)
        elif typ == "ECLiPSe":
            self.kb = ECLiPSeKB.ECLiPSeKB(sentence=sentence, path=path)

    def tell(self, sentence):
        return self.kb.tell(sentence)

    def retract(self, sentence):
        return self.kb.retract(sentence)

    def ask(self, sentence):
        return self.kb.ask(sentence)

    def set(self, key, value):
        if not issubclass(key.__class__, str):
            raise KBNameNotString

        self.kb._encode(key, value)

    def get(self, key):
        return self.kb._decode(key)

    def load_module(self, module, into=None):
        if self.type in ['Spade', 'SPARQL']:
            raise ValueError('%s does not support loading modules!' % self.type)
        else:
            self.kb.load_module(module, into)

    loadModule = deprecated(load_module, "loadModule")


if __name__ == "__main__":

    kb0 = KB()
    kb0.set("varname1", 1234)
    a = kb0.get("varname1")
    print(a, a.__class__)

    kb0.set("varname2", "myString")
    a = kb0.get("varname2")
    print(a, a.__class__)

    kb0.set("varname3", 1.34)
    a = kb0.get("varname3")
    print(a, a.__class__)

    kb0.set("varname4", [5, 6, 7, 8])
    a = kb0.get("varname4")
    print(a, a.__class__)

    kb0.set("varname5", [5, 6.23, "7", [8, 9]])
    a = kb0.get("varname5")
    print(a, a.__class__)

    kb0.set("varname6", {'a': 123, 'b': 456, 789: "c"})
    a = kb0.get("varname6")
    print(a, a.__class__)

    kb0.set("varname7", {'a': [123.25], 'b': [4, 5, 6], 789: {'a': 1, 'b': 2}})
    a = kb0.get("varname7")
    print(a, a.__class__)

    try:
        kb0.set(123, "newvalue")
    except KBNameNotString:
        print("Test KBNameNotString passed.")


    class A:
        x = 1
        y = 2

        def test(self):
            print("Hello!")


    kb0.set("varname9", A())

    a = kb0.get("varname9")
    print(a, a.__class__, a.x, a.y)
    a.test()


    class B:
        pass


    kb0.set("varname10", B())

    b = kb0.get("varname10")
    print(b, b.__class__)

    kb0.set("varname11", None)

    n = kb0.get("varname11")
    print(n, n.__class__)
