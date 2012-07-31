from logic import FolKB, fol_bc_ask, expr, is_definite_clause, variables

import random
import string
import types

class KBNameNotString(Exception): pass
class KBValueNotKnown(Exception): pass

class KBConfigurationFailed(Exception):
    def __init__(self, msg=""):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class SpadeKB(FolKB):
    def tell(self, sentence):
        if issubclass(sentence.__class__,str):
            sentence = expr(sentence)
        if is_definite_clause(sentence):
            self.clauses.append(sentence)
        else:
            raise Exception("Not a definite clause: %s" % sentence)

    def retract(self, sentence):
        if issubclass(sentence.__class__,str):
            sentence = expr(sentence)
        self.clauses.remove(sentence)

    def ask(self, q):
        e = expr(q)
        vars = variables(e)
        ans = fol_bc_ask(self, [e])
        res = []
        for a in ans:
            res.append(dict([(x, v) for (x, v) in a.items() if x in vars]))
        res.sort(key=str)
        
        if res==[]: return False
        for r in res:
            if r!={}:
                return res
        return True #res is a list of empty dicts

    def _encode(self, key,value):
        key = key.capitalize()
        if issubclass(value.__class__, str):
            self.tell("Var("+key+","+value.capitalize()+",Str)")

        elif issubclass(value.__class__,int):
            self.tell("Var("+key+","+str(value)+",Int)")

        elif issubclass(value.__class__,float):
            self.tell("Var("+key+","+str(value) + ",Float)")

        elif issubclass(value.__class__,list):
            listID = ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase) for x in range(8))
            listID = listID.capitalize() #listID.replace(listID[0],listID[0].lower(),1)
            for elem in value:
                self._encode(listID, elem)
            self.tell("Var("+ key + ","+ listID +",List)")

        elif issubclass(value.__class__,dict):
            dictID = ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase) for x in range(8))
            dictID = dictID.capitalize() #listID.replace(listID[0],listID[0].lower(),1)
            for k,v in value.items():
                elemID = ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase) for x in range(8))
                elemID = elemID.capitalize() #elemID.replace(elemID[0],elemID[0].lower(),1)
                self._encode(elemID+"Key",k)
                self._encode(elemID+"Value",v)
                self.tell("Pair("+dictID+","+elemID+")")
            self.tell("Var("+key+","+dictID+",Dict)")

        else:
            raise KBValueNotKnown

    def _decode(self, key):
        gen = self._gen_decode(key)
	try:
            return gen.next()
	except StopIteration:
            return None

    def _gen_decode(self, key):
        key = key.capitalize()
        results = self.ask("Var("+key+", value, type)")
        if type(results)==types.BooleanType:
            yield None
        for res in  results:
            value = str(res[expr("value")])
            typ   = str(res[expr("type")])

            if   typ == "Int": yield int(value)
            elif typ == "Str": yield str(value).lower()
            elif typ == "Float": yield float(value)
            elif typ == "List":
                l = []
                listID = str(value)
                gen = self._gen_decode(listID)
                hasElements=True
                while hasElements:
                    try:
                        l.append(gen.next())
                    except:
                        hasElements=False
                yield l
            elif typ == "Dict":
                dictID = str(value)
                d = {}
                for i in self.ask("Pair("+dictID+", elemid)"):
                    elemID = str(i[expr("elemid")])
                    newkey   = self._gen_decode(elemID+"Key").next()
                    newvalue = self._gen_decode(elemID+"Value").next()
                    d[newkey] = newvalue
                yield d 
                    

                

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
            if typ=="Spade":
                self.kb = SpadeKB()
                return
            elif   typ=="SPARQL": import SPARQLKB
            elif typ=="XSB":    import XSBKB
            elif typ=="Flora2": import Flora2KB
            elif typ=="SWI":    import SWIKB
            elif typ=="ECLiPSe":import ECLiPSeKB
            else: raise KBConfigurationFailed("Could not import "+str(typ)+" KB.")

        except KBConfigurationFailed as e:
            #self.myAgent.DEBUG(str(e)+" Using Fol KB.", 'warn')
            typ = "Spade"

        self.type = typ
        typ+="KB"

        if typ=="SpadeKB":
            self.kb = SpadeKB()
        elif path!=None:
            self.kb = eval(typ+"."+typ+"("+str(sentence)+", '"+path+"')")
        else:
            self.kb = eval(typ+"."+typ+"("+str(sentence)+")")

    def tell(self, sentence):
        return self.kb.tell(sentence)

    def retract(self, sentence):
        return self.kb.retract(sentence)

    def ask(self, sentence):
        return self.kb.ask(sentence)

    def set(self, key, value):
        if not issubclass(key.__class__, str):
            raise KBNameNotString

        self.kb._encode(key,value)

    def get(self, key):
        return self.kb._decode(key)


if __name__ == "__main__":

    kb0 = KB()

    kb0.set("varname1",1234)
    a = kb0.get("varname1")
    print a, a.__class__

    kb0.set("varname2","myString")
    a = kb0.get("varname2")
    print a, a.__class__

    kb0.set("varname3",1.34)
    a = kb0.get("varname3")
    print a, a.__class__


    kb0.set("varname4",[5,6,7,8])
    a = kb0.get("varname4")
    print a, a.__class__

    kb0.set("varname5",[5,6.23,"7",[8,9]])
    a = kb0.get("varname5")
    print a, a.__class__

    kb0.set("varname6",{'a':123,'b':456,789:"c"})
    a = kb0.get("varname6")
    print a, a.__class__

    kb0.set("varname7",{'a':[123.25],'b':[4,5,6],789:{'a':1,'b':2}})
    a = kb0.get("varname7")
    print a, a.__class__

    try:
        kb0.set(123,"newvalue")
    except KBNameNotString:
        print "Test KBNameNotString passed."


    class A: pass
    try:
        kb0.set("i8", A())
    except KBValueNotKnown:
        print "Test KBValueNotKnown passed."


    a = kb0.get("varname9")
    print a, a.__class__

    #print kb0.kb.clauses
