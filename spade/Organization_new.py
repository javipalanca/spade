# -*- coding: utf-8 -*-
import random
import string

from xmpp import *
from Queue import *
import Unit_new
import DF
import Behaviour


class CreationError(Exception):
    def __init__(self):
        Exception.__init__(self)


class NotValidName(CreationError):
    def __init__(self):
        Exception.__init__(self)


class NotValidType(CreationError):
    def __init__(self):
        Exception.__init__(self)


class NotValidGoal(CreationError):
    def __init__(self):
        Exception.__init__(self)


class NotCreatePermision(CreationError):
    def __init__(self):
        Exception.__init__(self)


class NotSupervisor(CreationError):
    def __init__(self):
        Exception.__init__(self)


class JoinError(Exception):
    def __init__(self):
        Exception.__init__(self)


class PaswordNeeded(JoinError):
    def __init__(self):
        pass


class MembersOnly(JoinError):
    def __init__(self):
        Exception.__init__(self)


class BanedUser(JoinError):
    def __init__(self):
        Exception.__init__(self)


class NickNameConflict(JoinError):
    def __init__(self):
        Exception.__init__(self)


class MaximumUsers(JoinError):
    def __init__(self):
        pass


class LockedOrganization(JoinError):
    def __init__(self):
        Exception.__init__(self)


class MemberOfFederation(JoinError):
    def __init__(self):
        Exception.__init__(self)


class Unavailable(Exception):
    def __init__(self):
        Exception.__init__(self)


class UnavailableFunction(Exception):
    def __init__(self):
        Exception.__init__(self)


class DestroyError(Exception):
    def __init__(self):
        Exception.__init__(self)


class NotValidUnit(Exception):
    def __init__(self):
        Exception.__init__(self)


class LastOwner(Exception):
    def __init__(self):
        Exception.__init__(self)


class Organization_new(Unit_new.Unit_new):

    def __init__(self, agent, nick, name, type=None, goalList=None, agentList=[], contentLanguage="sl", create=True):
        Behaviour.OneShotBehaviour.__init__(self)
        self.myAgent = agent
        self.name = name
        self.type = type
        self.goalList = goalList
        self.agentList = agentList
        self.contentLanguage = contentLanguage
        self.platform = self.myAgent.getSpadePlatformJID()
        self.muc_name = self.myAgent.getMUC()
        self._roster = {}
        self.nick = nick
        self.create = create
        id_base = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])  # @UnusedVariable
        self.ID = str(name) + str(self.myAgent.getAID().getName()) + id_base
        self.state = "unavailable"
        self.UnavailableMsg = "Organization"
        self.members = []
        self.owner = False
        self.orgOwner = None

    def setup(self):
        pass

    def myCreate(self):
        if not self.checkGoal(self.goalList):
            raise NotValidGoal
        elif not self.checkType():
            raise NotVvalidType
        elif not self.testRoomName():
            raise NotValidName
        elif not self.createRoom():
            raise CreationError
        else:
            self.state = "available"
            if self.agentList != []:
        #enviando invitaciones
                self.invite(self.agentList)
         #registrando en el DF
               # dad = DF.DfAgentDescription()
               # ds = DF.ServiceDescription()
               # ds.setType("ORGANIZATION")
               # ds.setName(self.name)
               # dad.setAID(self.myAgent.getAID())
               # dad.addService(ds)
               # res = self.myAgent.registerService(dad)

            self.owner = True
            self.orgOwner = self.myAgent.JID
            p = Presence()
            t = Behaviour.MessageTemplate(p)
            self.presenceBehaviour = self.PresenceBehaviour(self.muc_name, self.name, self.nick, self)
            self.myAgent.addBehaviour(self.presenceBehaviour, t)
            if self.type == "Matrix" or self.type == "Federation":
                self.createTeam()

    def myJoin(self):
        #The Organization exists
        if not self.testOrganizationName():
        #The room no existe
            raise NotValidName
        elif not self.myJoinRoom():
            #No es una organizacion
            #raise JoinError
            pass
        else:
            info = self.getInfo()
            if info:
                self.type = info["type"]
                self.contentLanguage = info["contentLanguage"]
                self.parent = info["parent"]
                self.goal = info["goal"]
            self.state = "available"
            p = Presence()
            t = Behaviour.MessageTemplate(p)
            self.presenceBehaviour = self.PresenceBehaviour(self.muc_name, self.name, self.nick, self)
            self.myAgent.addBehaviour(self.presenceBehaviour, t)

    def testRoomName(self):
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        iq = Iq(frm=self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(iq)
        b = self.TestRoomNameBehaviour(ID, self.muc_name, self.name)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class TestRoomNameBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, ID, muc_name, roomname):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.result = False
            self.muc_name = muc_name
            self.roomname = roomname

        def _process(self):
            iq = Iq(to=self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/disco#items")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if query:
                    self.result = True
                    items = msg.getQueryChildren()
                    for item in items:
                        if item.getAttr("jid") == str(self.roomname + "@" + self.muc_name):
                            self.result = False
                else:
                    self.result = False

    def testOrganizationName(self):
        info = self.getInfo()
        if info:
            if info["parent"] == "Organization":
                return True
        return False

    def createRoom(self):
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Presence(frm=self.name + "@" + self.muc_name + "/" + self.nick)
        t1 = Behaviour.MessageTemplate(p)
        b = self.CreateRoomBehaviour(ID, self.muc_name, self.name, self.nick, self.contentLanguage, self.type, self.goalList)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class CreateRoomBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, ID, muc_name, roomname, nick, contentLanguage, type, goal):
            Behaviour.OneShotBehaviour.__init__(self)
            self.result = False
            self.ID = ID
            self.nick = nick
            self.muc_name = muc_name
            self.name = roomname
            self.contentLanguage = contentLanguage
            self.type = type
            self.goal = goal

        def _process(self):
            p = Presence(to=self.name + "@" + self.muc_name + "/" + self.nick)
            x = Protocol("x", xmlns="http://jabber.org/protocol/muc")
            p.addChild(node=x)
            self.myAgent.jabber.send(p)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") == "error":
                    print "Room creation is restricted"
                    self.result = False
                    return
            else:
                self.result = False
                return
            template = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": self.ID})
            t = Behaviour.MessageTemplate(template)
            self.setTemplate(t)
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            #para descartar los presence anteriores
            while msg and msg.getName() != "iq":
                msg = self._receive(True, 10)

            #setting room configuration
            if not msg or msg.getAttr("type") == "error":
                print "No configuration is possible: "
                self.result = False
                return
            #falta por revisar!!!!
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            x = Node(tag="x", attrs={"xmlns": "jabber:x:data", " type": "submit"})
            resquery = msg.getQueryChildren()[0]  # nos quedamos con el hijo de query
            if resquery:
                items = resquery.getTags("field")
            if resquery is None:
                print "No configuration is possible"
                self.result = False
            for item in items:
                value = None
                if item.getAttr("var") == "muc#roomconfig_lang":
                    value = self.contentLanguage
                if item.getAttr("var") == "muc#roomconfig_roomdesc":
                    value = self.type
                if item.getAttr("var") == "muc#roomconfig_roomtype":
                    value = "Organization"
                if item.getAttr("var") == "muc#roomconfig_roomname":
                    value = self.name
                if item.getAttr("var") == "muc#roomconfig_presencebroadcast":
                    value = "moderator"
                if item.getAttr("var") == "muc#roomconfig_persistentroom":
                    value = "1"
                if item.getAttr("var") == "muc#roomconfig_publicroom":
                    value = "1"
                if item.getAttr("var") == "muc#roomconfig_moderatedroom":
                    value = "1"
                if item.getAttr("var") == "muc#roomconfig_membersonly":
                    value = "0"
                if item.getAttr("var") == "muc#roomconfig_passwordprotectedroom":
                    value = "0"
                if item.getAttr("var") == "muc#roomconfig_whois":
                    value = "moderators"  # como es esto??
                ###CAMBIA############################################3
                if item.getAttr("var") == "muc#roomconfig_changesubject":
                    value = "1"
                if value:
                    node = Node(tag="field", attrs={"var": item.getAttr("var")})
                    valnode = Node(tag="value")
                    valnode.addData(value)
                    node.addChild(node=valnode)
                    x.addChild(node=node)
            query.addChild(node=x)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg and msg.getAttr("type") == "result":  # comprobar mejor el mensaje que se devuelve
                #modifying the Room Subject
                m = Message(to=self.name + "@" + self.muc_name, typ="groupchat")
                sub = Node(tag="subject")
                sub.addData(str(self.goal))
                m.addChild(node=sub)
                self.myAgent.jabber.send(m)
                self.result = True
            else:
                self.result = False

    def createTeam(self):
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Presence(frm="Team:" + self.name + "@" + self.muc_name + "/" + self.nick)
        t1 = Behaviour.MessageTemplate(p)
        b = self.CreateTeamBehaviour(ID, self.muc_name, self.name, self.nick, self.contentLanguage, self.goalList, self.agentList)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class CreateTeamBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, ID, muc_name, roomname, nick, contentLanguage, goal, agentList):
            Behaviour.OneShotBehaviour.__init__(self)
            self.result = False
            self.ID = ID
            self.nick = nick
            self.muc_name = muc_name
            self.name = "Team:" + roomname
            self.parent = roomname
            self.contentLanguage = contentLanguage
            self.type = "Team"
            self.goal = goal
            self.agentList = agentList

        def _process(self):
            p = Presence(to=self.name + "@" + self.muc_name + "/" + self.nick)
            x = Protocol("x", xmlns="http://jabber.org/protocol/muc")
            p.addChild(node=x)
            self.myAgent.jabber.send(p)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") == "error":
                    print "Room creation is restricted"
                    self.result = False
                    return
            else:
                self.result = False
                return
            template = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": self.ID})
            t = Behaviour.MessageTemplate(template)
            self.setTemplate(t)
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            #para descartar los presence anteriores
            while msg and msg.getName() != "iq":
                msg = self._receive(True, 10)

            #setting room configuration
            if not msg or msg.getAttr("type") == "error":
                print "No configuration is possible: "
                self.result = False
                return
            #falta por revisar!!!!
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            x = Node(tag="x", attrs={"xmlns": "jabber:x:data", " type": "submit"})
            resquery = msg.getQueryChildren()[0]  # nos quedamos con el hijo de query
            if resquery:
                items = resquery.getTags("field")
            if resquery is None:
                print "No configuration is possible"
                self.result = False
            for item in items:
                value = None
                if item.getAttr("var"):
                    value = item.getAttr("value")  # tomamos el valor
                if item.getAttr("var") == "muc#roomconfig_lang":
                    value = self.contentLanguage
                if item.getAttr("var") == "muc#roomconfig_roomdesc":
                    value = self.type
                if item.getAttr("var") == "muc#roomconfig_roomtype":
                    value = "Unit:" + self.parent
                if item.getAttr("var") == "muc#roomconfig_roomname":
                    value = self.name
                if item.getAttr("var") == "muc#roomconfig_presencebroadcast":
                    value = "moderator"
                if item.getAttr("var") == "muc#roomconfig_persistentroom":
                    value = "1"
                if item.getAttr("var") == "muc#roomconfig_publicroom":
                    value = "1"
                if item.getAttr("var") == "muc#roomconfig_moderatedroom":
                    value = "0"
                if item.getAttr("var") == "muc#roomconfig_membersonly":
                    value = "1"
                if item.getAttr("var") == "muc#roomconfig_passwordprotectedroom":
                    value = "0"
                if item.getAttr("var") == "muc#roomconfig_whois":
                    value = "anyone"  # como es esto??
                if item.getAttr("var") == "muc#roomconfig_changeSubject":
                    value = "0"
                if value:
                    node = Node(tag="field", attrs={"var": item.getAttr("var")})
                    valnode = Node(tag="value")
                    valnode.addData(value)
                    node.addChild(node=valnode)
                    x.addChild(node=node)
            query.addChild(node=x)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg and msg.getAttr("type") == "result":  # comprobar mejor el mensaje que se devuelve
                #añadiendo los members invitacion
                for agent in self.agentList:
                    iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                    query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                    item = Node(tag="item", attrs={"affiliation": "owner", "jid": agent})
                    query.addChild(node=item)
                    iq.addChild(node=query)
                    self.myAgent.jabber.send(iq)
                m = Message(to=self.name + "@" + self.muc_name, typ="groupchat")
                sub = Node(tag="subject")
                sub.addData(str(self.goal))
                m.addChild(node=sub)
                self.myAgent.jabber.send(m)
                self.result = True
            else:
                self.result = False

    def checkGoal(self, goalList):
        #falta por implementar
        if goalList is not None:
            return True
        else:
            return False

    def checkType(self):
        types = ("Flat", "Team", "Hierarchy", "Bureaucracy", "Matrix", "Federation", "Coalition", "Congregation")
        if self.type in types:
            return True
        return False

    def invite(self, agentList):
        if self.state == "unavailable":
            raise Unavailable
            return
        for agent in agentList:
            message = Node(tag="message", attrs={"to": self.name + "@" + self.muc_name})
            x = Node(tag="x", attrs={"xmlns": "http://jabber.org/protocol/muc#user"})
            y = Node(tag="invite", attrs={"to": agent})
            r = Node(tag="reason")
            r.addData("Inivitation to the Organization " + self.name)
            y.addChild(node=r)
            x.addChild(node=y)
            message.addChild(node=x)
            self.myAgent.jabber.send(message)

    def myJoinRoom(self):
        p = Presence(frm=self.name + "@" + self.muc_name + "/" + self.nick, attrs={"type": "error"})
        t1 = Behaviour.MessageTemplate(p)
        b = self. MyJoinRoomBehaviour(self.muc_name, self.name, self.nick)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class  MyJoinRoomBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, nick):
            Behaviour.OneShotBehaviour.__init__(self)
            self.result = False
            self.nick = nick
            self.muc_name = muc_name
            self.name = roomname

        def _process(self):
            p = Presence(to=self.name + "@" + self.muc_name + "/" + self.nick)
            x = Protocol("x", xmlns="http://jabber.org/protocol/muc")
            p.addChild(node=x)
            self.myAgent.jabber.send(p)
            msg = self._receive(True, 10)
            if msg:
                error = msg.getTag("error")
                if error.getAttr("code") == "401":
                    raise PaswordNeeded
                if error.getAttr("code") == "407":
                    raise MembersOnly
                if error.getAttr("code") == "403":
                    raise BanedUser
                if error.getAttr("code") == "409":
                    raise NickNameConflict
                if error.getAttr("code") == "503":
                    raise MaximumUsers
                if error.getAttr("code") == "404":
                    raise LockedOrganization
                self.result = False
                return
            self.result = True

    def getRegistrationForm(self, unitName):
        """
        Returns a dataform with all requested information for joining
        """
        if self.state == "unavailable":
            raise Unavailable
            return
        if unitName not in self.getUnitList():
            raise NotValidUnit
            return

        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=unitName + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetRegistrationFormBehaviour(self.muc_name, ID, unitName)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetRegistrationFormBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, ID, unitName):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.unitName = unitName
            self.result = None

        def _process(self):
            iq = Iq(to=self.unitName + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="jabber:iq:register")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    error = msg.getError()
                    print error
                    return
                else:
                    if msg.getTag("register") is not None:
                        print "The agent has yet registered in the Unit " + self.unitName
                    else:
                        self.result = msg.getChildren()[0]
#cambiar

    def sendRegistrationForm(self, unitName, dataForm):
        """
        Sends a dataform for a specific unit. If valid, agent is registered and allowed to join
        """
        if self.state == "unavailable":
            raise Unavailable
            return
        #comprobando que es una unidad de la organizacion
        if unitName not in self.getUnitList():
            raise NotValidUnit
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=unitName + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetRegistrationFormBehaviour(self.muc_name, self.name, ID, unitName, dataForm)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class SendRegistrationFormBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, unitName, dataForm):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.unitName = unitName
            self.dataForm = dataForm
            self.result = None

        def _process(self):
            iq = Iq(to=self.unitName + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="jabber:iq:register")
            query.addNode(node=self.dataForm)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    error = msg.getTag("error")
                    if error.getAttr("code") == "409":
                        print "Error: Conflict, this nickname is already reserved"
                    if error.getAttr("code") == "503":
                        print "Error: Resgistration Not Supported"
                    if error.getAttr("code") == "400":
                        print "Error: Bad Request"

    def getUnitList(self):
        """
        Returns a dataform with all requested information for joining
        """
        if self.state == "unavailable":
            raise Unavailable
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        iq = Iq(frm=self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(iq)
        b = self.GetUnitListBehaviour(ID, self.muc_name, self.name)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class GetUnitListBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, ID, muc_name, roomname):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.result = []
            self.muc_name = muc_name
            self.roomname = roomname

        def _process(self):
            self.result = []
            iq = Iq(to=self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/disco#items")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if query:
                    items = msg.getQueryChildren()
                    for item in items:
                        if item.getAttr("jid"):
                            iq = Iq(to=item.getAttr("jid"), typ='get', attrs={"id": self.ID})
                            query = Protocol('query', xmlns="http://jabber.org/protocol/disco#info")
                            iq.addChild(node=query)
                            name = str(item.getAttr("name"))
                            self.myAgent.jabber.send(iq)
                            template = Iq(frm=item.getAttr("jid"), typ='result', attrs={"id": self.ID})
                            t = Behaviour.MessageTemplate(template)
                            self.setTemplate(t)
                            msg = self._receive(True, 10)
                            if msg:
                                query = msg.getTag("query")
                                if query:
                                    x = query.getTag("x")
                                    if x:
                                        items = x.getChildren()
                                        for item in items:
                                            value = None
                                            if item.getAttr("var") == "muc#roominfo_type":
                                                if item.getTags("value"):
                                                    value = item.getTags("value")[0].getData()
                                                    if  value == "Unit:" + self.roomname:
                                                        self.result.append(name)

    def getUnitInfo(self, unitname):
        if self.state == "unavailable":
            raise Unavailable
            return
        if unitname not in selg.getUnitList():
            raise NotValidUnit
            return

        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, typ='result', attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetUnitInfoBehaviour(self.muc_name, unitname, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetUnitInfoBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = None

        def _process(self):
            info = {}
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/disco#info")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                query = msg.getTag("query")
                if query:
                    x = query.getTag("x")
                    if x:
                        items = x.getChildren()
                        for item in items:
                            if item.getAttr("var") == "muc#roominfo_description":
                                if item.getTags("value"):
                                    info["type"] = item.getTags("value")[0].getData()
                            if item.getAttr("var") == "muc#roominfo_subject":
                                if item.getTags("value"):
                                    info["goal"] = item.getTags("value")[0].getData()
                            if item.getAttr("var") == "muc#roominfo_type":
                                if item.getTags("value"):
                                    info["contentLanguage"] = item.getTags("value")[0].getData()
            self.result = info

    def leave(self):
        """
       Agent leaves and it is removed from the member list
        """
        if self.state == "unavailable":
            raise Unavailable
            return
        owners = self.getOwnerList()
        if self.owner is not True:
            units = self.getUnitList()
            units.append(self.name)
            for u in units:
                p = Presence(to=u + "@" + self.muc_name + "/" + self.nick, typ="unavailable")
                self.myAgent.jabber.send(p)
                self.state = "unavailable"
                self.myAgent.removeBehaviour(self.presenceBehaviour)
                self.myAgent.removeBehaviour(self)
        else:
            raise LastOwner

    def destroy(self):
        #deberia implicar dejar tambien las salas de la organizacion???
        """
       Organization owner destroys the organization
        """
        if self.state == "unavailable":
            raise Unavailable
            return
        units = self.getUnitLis
        units.append(self.name)
        if self.owner is True:
            for u in units:
                ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
                p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
                t1 = Behaviour.MessageTemplate(p)
                b = self.DestroyBehaviour(self.muc_name, u, ID)
                self.myAgent.addBehaviour(b, t1)
                b.join()
            #destruir los comportamientos
            self.myAgent.removeBehaviour(self.presenceBehaviour)
            self.myAgent.removeBehaviour(self)
            self.state = "unavailable"
            #destruir las unidades
        else:
            raise DestroyError

    class DestroyBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = False

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            item = Node(tag="destroy")
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
            #print "Error: This agent is not a owner of the organization"
                    print msg.getError()
                    return
                else:
                    self.result = True

    def joinUnit(self, unit):
        if self.state == "unavailable":
            raise Unavailable
            return
        if unit.name not in self.getUnitList():
            raise NotValidUnit
            return
        if self.type == "Federation":
            if self.checkIsMember(unit.name):
                raise MemberOfFederation
                return
        unit.create = False
        self.myAgent.addBehaviour(unit)

    def checkIsMember(self, unit):
        ismember = False
        units = self.getUnitList()
        if unit in units:
            units.remove(unit)
        team = "Team:" + self.name
        if team in units:
            units.remove(team)
        jid = str(self.myAgent.JID)
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=jid, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.IsMemberBehaviour(jid, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        b.result
        for u in units:
            if u in b.result:
                ismember = True
        return ismember

    class IsMemberBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, jid, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.jid = jid
            self.result = []

        def _process(self):
            iq = Iq(to=self.jid, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/disco#items", attrs={"node": "http://jabber.org/protocol/muc#rooms"})
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                items = msg.getChildren()
                for item in items:
                    if item.getAttr("jid"):
                        sala = str(item.getAttr("jid"))
                        self.result.append(sala.split('@')[0])

    def addUnit(self, unit):
        """
          Creates a new unit inside an organization
          """
        if self.state == "unavailable":
            raise Unavailable
            return
        if self.checkTypes(self.type, unit.type):
        #un sitwch para aquellas organizaciones donde todos puedan crear unidades
            if self.type != "Matrix" and self.type != "Federation":
                if self.checkOwnerAdmin(self.myAgent.JID):
                    unit.create = True
                    unit.parent = self.name
                    unit.parent_type = self.type
                    if self.orgOwner is None:
                        self.orgOwner = self.getOwnerList()[0]
                    unit.orgOwner = self.orgOwner
                    self.myAgent.addBehaviour(unit)
                else:
                    raise NotCreatePermision
            elif self.checkSupervisor(self.myAgent.JID):
                unit.create = True
                unit.parent = self.name
                unit.parent_type = self.type
                if self.orgOwner is None:
                    self.orgOwner = self.getOwnerList()[0]
                unit.orgOwner = self.orgOwner
                self.myAgent.addBehaviour(unit)
            else:
                raise NotSupervisor
        else:
            raise NotValidType

    def checkTypes(self, orgType, unitType):
        if orgType == "Flat":
            return True
        if orgType == "Team" and unitType == "Team":
            return True
        if orgType == "Hierarchy" and unitType == "Hierarchy":
            return True
        if orgType == "Bureaucracy" and unitType == "Hierarchy":
            return True
        if orgType == "Matrix" and unitType == "Hierarchy":
            return True
        if orgType == "Federation" and unitType == "Hierarchy":
            return True
        if orgType == "Coalition" and unitType == "Team":
            return True
        if orgType == "Congregation" and unitType == "Hierarchy":
            return True
        if orgType == "Congregation" and unitType == "Team":
            return True
        if orgType == "Congregation" and unitType == "Flat":
            return True
        return False

    def getSupervisorList(self):
        list = []
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm="Team:" + self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetMemberListBehaviour(self.muc_name, "Team:" + self.name, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        member = b.result
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm="Team:" + self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetOwnerListBehaviour(self.muc_name, "Team:" + self.name, ID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        owner = b.result
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetAdminListBehaviour(self.muc_name, "Team:" + self.name, ID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        admin = b.result
        for i in owner:
            list.append(i)
        for i in member:
            list.append(i)
        for i in admin:
            list.append(i)
        return list

    def sendMessage(self, message):
        raise UnavailableFunction

    def sendPrivateMessage(self, recName, message):
        raise UnavailableFunction

    def giveVoice(self, nickname):
        raise UnavailableFunction

    def revokeVoice(self, nickname):
        raise UnavailableFunction

    def _process(self):
        pass
