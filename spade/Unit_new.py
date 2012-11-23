# -*- coding: utf-8 -*-
import random
import string

from xmpp import *
from Queue import *
import Behaviour


class CreationError(Exception):
    def __init__(self):
        Exception.__init__(self)


class NotValidName(CreationError):
    def __init__(self):
        CreationError.__init__(self)


class NotValidGoalChange(Exception):
    def __init__(self):
        Exception.__init__(self)


class NotValidType(CreationError):
    def __init__(self):
        CreationError.__init__(self)


class NotValidGoal(CreationError):
    def __init__(self):
        CreationError.__init__(self)


class NotCreatePermision(CreationError):
    def __init__(self):
        CreationError.__init__(self)


class NotSupervisor(CreationError):
    def __init__(self):
        CreationError.__init__(self)


class JoinError(Exception):
    def __init__(self):
        Exception.__init__(self)


class PaswordNeeded(JoinError):
    def __init__(self):
        JoinError.__init__(self)


class MembersOnly(JoinError):
    def __init__(self):
        JoinError.__init__(self)


class BanedUser(JoinError):
    def __init__(self):
        JoinError.__init__(self)


class NickNameConflict(JoinError):
    def __init__(self):
        JoinError.__init__(self)


class MaximumUsers(JoinError):
    def __init__(self):
        JoinError.__init__(self)


class LockedUnit(JoinError):
    def __init__(self):
        JoinError.__init__(self)


class Unavailable(Exception):
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


class Unit_new(Behaviour.OneShotBehaviour):

    def __init__(self, agent, nick, name, type="Team", goalList=[], agentList=[], contentLanguage="sl", password=None, create=True):
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
        self.password = password
        self.create = create
        self.parent_type = None
        self.parent = None
        id_base = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])  # @UnusedVariable
        self.ID = str(name) + str(self.myAgent.getAID().getName()) + id_base
        self.state = "unavailable"
        self.UnavailableMsg = "Unit"
        self.members = []
        self.owner = False
        self.orgOwner = None

    def setup(self):
        pass

    def myCreate(self):
        if not self.checkGoal(self.goalList):
            raise NotValidGoal
        elif not self.checkType():
            raise NotValidType
        elif self.type == "Hierarchy" and self.password is None:
            raise PaswordNeeded
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
        #dad = DF.DfAgentDescription()
        #ds = DF.ServiceDescription()
        #ds.setType("Unit: "+self.parent)
        #ds.setName(self.name)
        #dad.addService(ds)
        # res = self.myAgent.registerService(dad)
        #anyadimos el comportamiento que lee los presence
            self.owner = True
            p = Presence()
            t = Behaviour.MessageTemplate(p)
            self.presenceBehaviour = self.PresenceBehaviour(self.muc_name, self.name, self.nick, self)
            self.myAgent.addBehaviour(self.presenceBehaviour, t)

    def myJoin(self):
        #The Organization exists
        if not self.testUnitName():
            raise NotValidName
        #The room no existe
        elif not self.myJoinRoom():
            raise JoinError
        #No es una organizacion
        else:
            info = self.getInfo()
            if info:
                self.type = info["type"]
                self.contentLanguage = info["contentLanguage"]
                self.parent = info["parent"]
                parent_info = self.myAgent.getOrganizationInfo(self.parent)
                self.parent_type = parent_info["type"]
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

    def createRoom(self):
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Presence(frm=self.name + "@" + self.muc_name + "/" + self.nick)
        t1 = Behaviour.MessageTemplate(p)
        b = self.CreateRoomBehaviour(ID, self.muc_name, self.name, self.nick, self.parent, self.contentLanguage, self.type, self.goalList, self.password, self.orgOwner)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class CreateRoomBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, ID, muc_name, roomname, nick, parent, contentLanguage, type, goalList, password, orgOwner):
            Behaviour.OneShotBehaviour.__init__(self)
            self.result = False
            self.ID = ID
            self.nick = nick
            self.muc_name = muc_name
            self.name = roomname
            self.parent = parent
            self.contentLanguage = contentLanguage
            self.type = type
            self.goalList = goalList
            self.password = password
            self.orgOwner = orgOwner

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
                print "No configuration is possible: " + msg.getError()
                #cambiar
                iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
                x = Node(tag="x", attrs={"xmlns": "jabber:x:data", " type": "submit"})
                query.addChild(node=x)
                iq.addChild(node=query)
                self.myAgent.jabber.send(iq)
                #return False
                self.result = False
                return
            ispasswordprotected = False
            if self.type == "Hierarchy" or self.password is not None:
                ispasswordprotected = True
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            x = Node(tag="x", attrs={"xmlns": "jabber:x:data", " type": "submit"})
            resquery = msg.getQueryChildren()[0]  # nos quedamos con el hijo de query
            if resquery:
                items = resquery.getTags("field")
            if resquery is None:
                print "No configuration is possible"
                return False
            for item in items:
                if item.getAttr("var"):
                    value = None
                    if item.getAttr("var") == "muc#roomconfig_lang":
                        value = self.contentLanguage
                    if item.getAttr("var") == "muc#roomconfig_roomdesc":
                        value = self.type
                    if item.getAttr("var") == "muc#roomconfig_roomname":
                        value = self.name
                    if item.getAttr("var") == "muc#roomconfig_roomtype":
                        value = "Unit:" + self.parent
                    if item.getAttr("var") == "muc#roomconfig_presencebroadcast":
                        value = "moderator"
                    if item.getAttr("var") == "muc#roomconfig_persistentroom":
                        value = "1"
                    if item.getAttr("var") == "muc#roomconfig_publicroom":
                        value = "1"
                    if item.getAttr("var") == "muc#roomconfig_moderatedroom":
                        value = "1"
                    if item.getAttr("var") == "muc#roomconfig_passwordprotectedroom":
                        if self.type == "Hierarchy" or self.password is not None:
                            value = "1"
                        else:
                            value = "0"
                    if item.getAttr("var") == "muc#roomconfig_roomsecret":
                        value = self.password
                    if item.getAttr("var") == "muc#roomconfig_whois":
                        if self.type == "Hierarchy":
                            value = "moderators"
                        else:
                            value = "anyone"
                    #como configurar?????????????
                    if item.getAttr("var") == "muc#roomconfig_changesubject":
                        value = "1"
                    if item.getAttr("var") == "muc#roomconfig_allowinvites":
                        value = "1"
                ####################################333
                    if item.getAttr("var") == "muc#roomconfig_membersonly":
                        if self.type == "Flat":
                            value = "0"
                        else:
                            value = "1"
                    node = Node(tag="field", attrs={"var": item.getAttr("var")})
                    valnode = Node(tag="value")
                    valnode.addData(value)
                    node.addChild(node=valnode)
                    if(item.getAttr("var") != "muc#roomconfig_roomsecret" or ispasswordprotected) and value is not None:
                        x.addChild(node=node)
            query.addChild(node=x)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg and msg.getAttr("type") == "result":  # comprobar mejor el mensaje que se devuelve

                m = Message(to=self.name + "@" + self.muc_name, typ="groupchat")
                sub = Node(tag="subject")
                sub.addData(str(self.goalList))
                m.addChild(node=sub)
                self.myAgent.jabber.send(m)
                #añadiendo al owner de la organizacion
                self.myAgent.jabber.send(iq)
                iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                item = Node(tag="item", attrs={"affiliation": "owner", "jid": self.orgOwner})
                query.addChild(node=item)
                iq.addChild(node=query)
                self.myAgent.jabber.send(iq)
                self.result = True
            else:
                return False

    def myJoinRoom(self):
        p = Presence(frm=self.name + "@" + self.muc_name, attrs={"type": "error"})
        t1 = Behaviour.MessageTemplate(p)
        b = self.MyJoinRoomBehaviour(self.muc_name, self.name, self.nick, self.password)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class MyJoinRoomBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, nick, password):
            Behaviour.OneShotBehaviour.__init__(self)
            self.result = False
            self.nick = nick
            self.muc_name = muc_name
            self.name = roomname
            self.password = password

        def _process(self):
            p = Presence(to=self.name + "@" + self.muc_name + "/" + self.nick)
            x = Node(tag="x", attrs={"xmlns": "http://jabber.org/protocol/muc"})
            if self.password is not None:
                pas = Node(tag="password")
                pas.addData(self.password)
                x.addChild(node=pas)
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
                    raise MaximumNumber
                if error.getAttr("code") == "404":
                    raise LockedUnit
                self.result = False
                return
            self.result = True

    def checkGoal(self, goalList):
        #falta por implementar
        if goalList is not None:
            return True
        else:
            return False

    def checkType(self):
        types = ("Flat", "Team", "Hierarchy")
        if self.type in types:
            return True
        return False

    def testUnitName(self):
        info = self.getInfo()
        if info:
            if info["parent"] != "Organization" and info["parent"] != "":
                return True
        return False

    def invite(self, agentList):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        for agent in agentList:
            message = Node(tag="message", attrs={"to": self.name + "@" + self.muc_name})
            x = Node(tag="x", attrs={"xmlns": "http://jabber.org/protocol/muc#user"})
            y = Node(tag="invite", attrs={"to": agent})
            r = Node(tag="reason")
            r.addData("Inivitation to the Unit " + self.name)
            y.addChild(node=r)
            x.addChild(node=y)
            message.addChild(node=x)
            self.myAgent.jabber.send(message)

    def setGoal(self, goalList):
        """
        Updates organization goals
        """
        #comprobar que sea un objetivo valido
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        if not self.checkGoal(goalList):
            raise NotValidGoal
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Message(frm=self.name + "@" + self.muc_name, typ="error", attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.SetGoalBehaviour(self.muc_name, self.name, goalList, ID)
        self.myAgent.addBehaviour(b, t1)

    class SetGoalBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, goalList, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.goalList = goalList
            self.muc_name = muc_name
            self.name = roomname
            self.ID = ID

        def _process(self):
            m = Message(to=self.name + "@" + self.muc_name, typ="groupchat", attrs={"id": self.ID})
            sub = Node(tag="subject")
            sub.addData(str(self.goalList))
            m.addChild(node=sub)
            self.myAgent.jabber.send(m)
            msg = self._receive(True, 10)
            if msg:
                raise NotValidGoalChange

    def getGoal(self):
        """
        Retruns a list of goals
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, typ='result', attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetGoalBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetGoalBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = None

        def _process(self):
            goal = None
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
                            if item.getAttr("var") == "muc#roominfo_subject":
                                if item.getTags("value"):
                                    goal = item.getTags("value")[0].getData()
            if goal is None:
                print "Not goal"
            self.result = goal

    def getInfo(self):
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, typ='result', attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetInfoBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetInfoBehaviour(Behaviour.OneShotBehaviour):
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
                                    info["type"] = str(item.getTags("value")[0].getData())
                            if item.getAttr("var") == "muc#roominfo_subject":
                                if item.getTags("value"):
                                    info["goal"] = str(item.getTags("value")[0].getData())
                            if item.getAttr("var") == "muc#roominfo_type":
                                if item.getTags("value")[0].getData():
                                    if ':' in item.getTags("value")[0].getData():
                                        info["parent"] = str(item.getTags("value")[0].getData().split(':')[1])
                                    else:
                                        info["parent"] = str(item.getTags("value")[0].getData())
                            if item.getAttr("var") == "muc#roominfo_lang":
                                if item.getTags("value"):
                                    info["contentLanguage"] = str(item.getTags("value")[0].getData())
            self.result = info

    def getMemberList(self):
        """
        Returns a List with Agents' names belonging to the organization
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetMemberListBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetMemberListBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = []

        def _process(self):
                    # si es una unidad tambien hay que mirar si el presence broadcast est√° restringido
            # if  not checkOwner(self.myAgent):
                    #    print "This agent is not allowed to get the memberList"
            agents = []
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "member"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                error = msg.getError()
                if error is not None:
                    print error
                    return
                query = msg.getTag("query")
                if query:
                    items = query.getChildren()
                    for item in items:
                        agents.append(str(item.getAttr("jid")))
                    self.result = agents
                    return

    def getMaxAgents(self):
        """
        Returns Maximum agents allowed to enter inside the Organization
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetMaxAgentsBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetMaxAgentsBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = None

        def _process(self):

            maxAgents = None
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/disco#info")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                query = msg.getTag("query")
                if query:
                    x = query.getTag("x")
                    items = x.getChildren()
                    for item in items:
                        if item.getAttr("var") == "muc#roominfo_maxusers":
                            maxAgents = item.getTags("value")[0].getData()
            if maxAgents is None:
                print "Maximum agents has not been established"
            self.result = maxAgents

    def getMinAgents(self):
        """
        Returns Minimum agents needed to allow conversations inside
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetMinAgentsBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetMinAgentsBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = None

        def _process(self):
            minAgents = None
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/disco#info")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                query = msg.getTag("query")
                if query:
                    x = query.getTag("x")
                    items = x.getChildren()
                    for item in items:
                        if item.getAttr("var") == "muc#roominfo_minusers":
                            minAgents = item.getTags("value")[0].getData()
                if minAgents is None:
                    print "Minimum agents has not been established"
            self.result = minAgents

    def setMaxAgents(self, maxUsers):
        """
         Updates Maximum agents allowed to enter inside the Organization
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.SetMaxAgentsBehaviour(self.muc_name, self.name, ID, maxUsers)
        self.myAgent.addBehaviour(b, t1)
        b.join()

    class SetMaxAgentsBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, maxUsers):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.maxUsers = maxUsers

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg.getAttr("type") != "result":
                print "Forbidden. Not owner"  # completar un poco el error
                return
                #setting room configuration
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            x = Node(tag="x", attrs={"xmlns": "jabber:x:data", " type": "submit"})
            print msg.getQueryChildren()
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
                if item.getAttr("var") == "muc#roomconfig_maxusers":
                    value = self.maxUsers
                if value:
                    node = Node(tag="field", attrs={"var": item.getAttr("var")})
                    valnode = Node(tag="value")
                    valnode.addData(value)
                    node.addChild(node=valnode)
                    x.addChild(node=node)
            query.addChild(node=x)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)

    def setMinAgents(self, minUsers):
        """
        Updates Minimum agents needed to allow conversations inside
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.SetMinAgentsBehaviour(self.muc_name, self.name, ID, minUsers)
        self.myAgent.addBehaviour(b, t1)
        b.join()

    class SetMinAgentsBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, minUsers):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.minUsers = minUsers

        def _process(self):
            self.myAgent.register_mailbox(typ="iq", id=self.ID)
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg.getAttr("type") != "result":
                print "Forbidden. Not owner"  # completar un poco el error
                return
            self.myAgent.register_mailbox(typ="iq", id=self.ID)
                #setting room configuration
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#owner")
            x = Node(tag="x", attrs={"xmlns": "jabber:x:data", " type": "submit"})
            print msg.getQueryChildren()
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
                if item.getAttr("var") == "muc#roomconfig_minusers":
                    value = self.minUsers
                if value:
                    node = Node(tag="field", attrs={"var": item.getAttr("var")})
                    valnode = Node(tag="value")
                    valnode.addData(value)
                    node.addChild(node=valnode)
                    x.addChild(node=node)
            query.addChild(node=x)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)

    def getNumberOfAgents(self):
        """
        Returns current number od agents that are inside
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetNumberOfAgentsBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        return b.result

    class GetNumberOfAgentsBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = None

        def _process(self):
            agents = None
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
                        if item.getAttr("var") == "muc#roominfo_occupants":
                            agents = item.getTags("value")[0].getData()
            if agents is None:
                print "Error"
            self.result = agents

    def getOwnerList(self):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetOwnerListBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class GetOwnerListBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = []

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "owner"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error
                    return
                query = msg.getQueryChildren()
                if query:
                    #items =query.getChildren()
                    owners = []
                    for item in query:
                        if item.getAttr("jid"):
                            owners.append(str(item.getAttr("jid")))
                    self.result = owners
            return

    def addAdmin(self, newAdminJID):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.AddAdminBehaviour(self.muc_name, self.name, ID, newAdminJID)
        self.myAgent.addBehaviour(b, t)
        b.join()

    class AddAdminBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, newAdminJID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.newAdminJID = newAdminJID
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "admin", "jid": self.newAdminJID})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") == "error":
                    print msg.getError()  # completar un poco el error

    def removeAdmin(self, AdminJID):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.RemoveAdminBehaviour(self.muc_name, self.name, ID, AdminJID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class RemoveAdminBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, newAdminJID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.newAdminJID = newAdminJID
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "admin"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            exists = False
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error
                    return
                query = msg.getQueryChildren()
                if query:
                    iqAns = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                    queryAns = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                    for item in query:
                        if str(item.getAttr("jid")) == self.newAdminJID:
                            i = Node(tag="item", attrs={"affiliation": "member", "jid": self.newAdminJID})
                            queryAns.addChild(node=item)

                    iqAns.addChild(node=queryAns)
                    self.myAgent.jabber.send(iqAns)
                    msgAns = self._receive(True, 10)
                    if msgAns:
                        if msgAns.getAttr("type") != "result":
                            print msgAns.getError()  # completar un poco el error
                        else:
                            exists = True
                if not exists:
                    print "The JID " + self.newAdminJID + " doesn't belong to a admin"
                return
            print "Error"  # completar un poco el error

    def getAdminList(self):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetAdminListBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class GetAdminListBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = []

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "admin"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error
                    return
                query = msg.getQueryChildren()
                if query:
                    #items =query.getChildren()
                    owners = []
                    for item in query:
                        if item.getAttr("jid"):
                            owners.append(str(item.getAttr("jid")))
                    self.result = owners
                    return

    def addModerator(self, newModeratorJID):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.AddModeratorBehaviour(self.muc_name, self.name, ID, newModeratorJID)
        self.myAgent.addBehaviour(b, t)
        b.join()

    class AddModeratorBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, newModeratorJID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.newModeratorJID = newModeratorJID
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"role": "moderator", "JID": self.newModeratorJID})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error

    def removeModerator(self, moderatorJID):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.RemoveModeratorBehaviour(self.muc_name, self.name, ID, moderatorJID)
        self.myAgent.addBehaviour(b, t)
        b.join()

    class RemoveModeratorBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, moderatorJID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.moderatorJID = moderatorJID
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"role": "moderator"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            exists = False
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error
                    return
                query = msg.getQueryChildren()
                if query:
                    iqAns = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                    queryAns = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                    for item in query:
                        if item.getAttr("jid") == self.moderatorJID:
                            i = Node(tag="item", attrs={"affiliation": "member", "jid": self.moderatorJID})
                            queryAns.addChild(node=i)
                        else:
                            exists = True
                    self.myAgent.register_mailbox(typ="iq", id=self.ID)
                    iqAns.addChild(node=queryAns)
                    self.myAgent.jabber.send(iqAns)
                    msgAns = self._receive(True, 10)
                    if msgAns:
                        if msgAns.getAttr("type") != "result":
                            print msgAns.getError()  # completar un poco el error
                if not exists:
                    print "The JID " + self.moderatorJID + " doesn't belong to a owner"
            print "Error"  # completar un poco el error

    def getModeratorList(self):
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetModeratorListBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class GetModeratorListBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"role": "moderator"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error
                    return
                query = msg.getQueryChildren()
                if query:
                    #items =query.getChildren()
                    owners = []
                    for item in query:
                        if item.getAttr("jid"):
                            owners.append(str(item.getAttr("jid")))
                    self.result = owners
                    return
            print "Error"  # completar un poco el error

    def leave(self):
        """
         Agent leaves and it is removed from the member list
          """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        if self.owner is False:
            p = Presence(to=self.name + "@" + self.muc_name + "/" + self.nick, typ="unavailable")
            self.myAgent.jabber.send(p)
            self.state = "unavailable"
            self.myAgent.removeBehaviour(self.presenceBehaviour)
            self.myAgent.removeBehaviour(self)
        else:
            raise LastOwner

    def destroy(self):
        """
       Unit owner destroys the unit
        """
        if self.state == "unavailable":
            print "The " + self.UnavailableMsg + " " + self.name + " is unavailable"
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.DestroyBehaviour(self.muc_name, self.name, ID, self.parent)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        if b.result:
            #destruir los comportamientos
            self.myAgent.removeBehaviour(self.presenceBehaviour)
            self.myAgent.removeBehaviour(self)
            self.state = "unavailable"
        else:
            raise DestroyError

    class DestroyBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, parent):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.parent = parent
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
                    #Desregistrando del OMS
                    #dad = DF.DfAgentDescription()
                    #sd = DF.DFServiceDescription()
                    #sd.setName(self.name)
                    #sd.setType("Unit: "+self.parent)
                    #dad.addService(sd)
                    #res = self.myAgent.deregisterService(dad)
                    #print res
                    self.result = True
                    return
            print "Error: el mensaje no se ha recibido"

    class PresenceBehaviour(Behaviour.Behaviour):
        def __init__(self, muc_name, roomname, nick, unit):
            Behaviour.Behaviour.__init__(self)
            self.muc_name = muc_name
            self.name = roomname
            self.nick = nick
            self.unit = unit

        def _process(self):
            msg = self._receive(True, 10)
            if msg:
                if msg.getType() == "unavailable":
                    if msg.getRole() == "none" and msg.getFrom() == self.name + "@" + self.muc_name + "/" + self.nick:
                        x = msg.getTag("x")
                        if x:
                            self.unit.state = "unavailable"
                            destroy = x.getTag("destroy")
                            if destroy:
                                print "The room has been destroyed"
                                return
                        if msg.getStatusCode() == "301":
                            print "You have been baned"
                            return
                        else:
                            if msg.getStatusCode() == "307":
                                print "You have been kicked"
                                return
                        print "You have left the room"
                    else:
                        if msg.getFrom() in self.unit.members:
                            self.unit.members.remove(msg.getFrom())
                        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
                        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
                        t1 = Behaviour.MessageTemplate(p)
                        b = self.MinAgentsBehaviour(self.muc_name, self.name, ID, self.unit)
                        self.myAgent.addBehaviour(b, t1)
                else:
                    if self.unit.owner:
                        if msg.getFrom() not in self.unit.members:
                            self.unit.members.append(msg.getFrom())
                            ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
                            p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
                            t1 = Behaviour.MessageTemplate(p)
                            b = self.MinAgentsBehaviour(self.muc_name, self.name, ID, self.unit)
                            self.myAgent.addBehaviour(b, t1)

        class MinAgentsBehaviour(Behaviour.OneShotBehaviour):
            def __init__(self, muc_name, roomname, ID, unit):
                Behaviour.OneShotBehaviour.__init__(self)
                self.ID = ID
                self.muc_name = muc_name
                self.name = roomname
                self.result = []
                self.unit = unit

            def _process(self):
                minAgents = None
                iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
                query = Protocol('query', xmlns="http://jabber.org/protocol/disco#info")
                iq.addChild(node=query)
                self.myAgent.jabber.send(iq)
                msg = self._receive(True, 10)
                if msg:
                    query = msg.getTag("query")
                    if query:
                        x = query.getTag("x")
                        items = x.getChildren()
                        for item in items:
                            if item.getAttr("var") == "muc#roominfo_minusers":
                                minAgents = item.getTags("value")[0].getData()
                    agents = None
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
                                if item.getAttr("var") == "muc#roominfo_occupants":
                                    agents = item.getTags("value")[0].getData()
                    if agents and minAgents and int(agents) < int(minAgents):
                        iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
                        query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                        item = Node(tag="item", attrs={"role": "participant"})
                        query.addChild(node=item)
                        iq.addChild(node=query)
                        self.myAgent.jabber.send(iq)
                        msg = self._receive(True, 10)
                        if msg:
                            error = msg.getError()
                            if error is not None:
                                print error
                                return
                            q = msg.getTag("query")
                            if q:
                                iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                                query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                                items = q.getChildren()
                                for item in items:
                                    i = Node(tag="item", attrs={"jid": str(item.getAttr("jid")), "role": "visitor"})
                                    query.addChild(node=i)
                                iq.addChild(node=query)
                                self.myAgent.jabber.send(iq)
                                self.unit.state = "locked"
                if agents and minAgents and int(agents) > int(minAgents) and self.unit.state == "locked":
                    iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
                    query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                    item = Node(tag="item", attrs={"role": "visitor"})
                    query.addChild(node=item)
                    iq.addChild(node=query)
                    self.myAgent.jabber.send(iq)
                    msg = self._receive(True, 10)
                    if msg:
                        error = msg.getError()
                        if error is not None:
                            print error
                            return
                        q = msg.getTag("query")
                        if q:
                            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                            items = q.getChildren()
                            for item in items:
                                i = Node(tag="item", attrs={"jid": str(item.getAttr("jid")), "role": "visitor"})
                                query.addChild(node=i)
                            iq.addChild(node=query)
                            self.myAgent.jabber.send(iq)
                            self.unit.state = "available"

    def kickAgent(self, agentNick):
        if self.state == "unavailable":
            raise Unavailable
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.KickAgentBehaviour(self.muc_name, self.name, ID, agentNick)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class KickAgentBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, agentNick):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.agentNick = agentNick
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"role": "none", "nick": self.agentNick})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()

    def addBanAgent(self, agentJID):
        if self.state == "unavailable":
            raise Unavailable
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.AddBanAgentBehaviour(self.muc_name, self.name, ID, agentJID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class AddBanAgentBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, agentJID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.agentJID = agentJID
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "outcast", "jid": self.agentJID})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print "Error"  # completar un poco el error

    def removeBanAgent(self, agentJID):
        if self.state == "unavailable":
            raise Unavailable
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.RemoveBanAgentBehaviour(self.muc_name, self.name, ID, agentJID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class RemoveBanAgentBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, agentJID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.agentJID = agentJID
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "outcast"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            exists = False
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error
                    return
                query = msg.getQueryChildren()
                if query:
                    iqAns = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
                    queryAns = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
                    for item in query:
                        if item.getAttr("jid") == self.agentJID:
                            queryAns.addChild(node=item)
                        else:
                            exists = True
                    iqAns.addChild(node=queryAns)
                    self.myAgent.jabber.send(iqAns)
                    msgAns = self._receive(True, 10)
                    if msgAns:
                        if msgAns.getAttr("type") != "result":
                            print msgAns.getError()  # completar un poco el error
                    if not exists:
                        print "The JID " + self.agentJID + " doesn't belong to a banned agent"
                return
            print "Error"  # completar un poco el error

    def getBanAgentList(self):
        if self.state == "unavailable":
            raise Unavailable
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetBanAgentListBehaviour(self.muc_name, self.name, ID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        return b.result

    class GetBanAgentListBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.result = None

        def _process(self):
            BanedList = []
            iq = Iq(to=self.name + "@" + self.muc_name, typ='get', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"affiliation": "outcast"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error
                    return
                query = msg.getQueryChildren()
                if query:
                    for item in query:
                        if item.getAttr("jid"):
                            BanedList.append(str(item.getAttr("jid")))
                    self.result = BanedList

    def giveVoice(self, nickname):
        if self.state == "unavailable":
            raise Unavailable
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GiveVoiceBehaviour(self.muc_name, self.name, ID, nickname)
        self.myAgent.addBehaviour(b, t)
        b.join()

    class GiveVoiceBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, nickname):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.nickname = nickname
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"nick": self.nickname, "role": "participant"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error

    def revokeVoice(self, nickname):
        if self.state == "unavailable":
            raise Unavailable
            return
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm=self.name + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.RevokeVoiceBehaviour(self.muc_name, self.name, ID, nickname)
        self.myAgent.addBehaviour(b, t)
        b.join()

    class RevokeVoiceBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, ID, nickname):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID = ID
            self.muc_name = muc_name
            self.name = roomname
            self.nickname = nickname
            self.result = None

        def _process(self):
            iq = Iq(to=self.name + "@" + self.muc_name, typ='set', attrs={"id": self.ID})
            query = Protocol('query', xmlns="http://jabber.org/protocol/muc#admin")
            item = Node(tag="item", attrs={"nick": self.nickname, "role": "visitor"})
            query.addChild(node=item)
            iq.addChild(node=query)
            self.myAgent.jabber.send(iq)
            msg = self._receive(True, 10)
            if msg:
                if msg.getAttr("type") != "result":
                    print msg.getError()  # completar un poco el error

    def sendMessage(self, message):
        if self.state == "unavailable":
            raise Unavailable
            return
        p = Message(frm=self.name + "@" + self.muc_name, typ="error")
        t = Behaviour.MessageTemplate(p)
        b = self.SendMessageBehaviour(self.muc_name, self.name, message)
        self.myAgent.addBehaviour(b, t)
        b.join()

    class SendMessageBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, muc_name, roomname, message):
            Behaviour.OneShotBehaviour.__init__(self)
            self.muc_name = muc_name
            self.name = roomname
            self.message = message

        def _process(self):
            m = Message(to=self.name + "@" + self.muc_name, typ="groupchat")
            x = Node(tag="body")
            x.addData(self.message)
            m.addChild(node=x)
            self.myAgent.jabber.send(m)
            msg = self._receive(True, 10)
            if msg:
                print "This message can't be sent"
            #falta comprobar la respuesta del servidor forbidden o not-acceptable(este no deberia producirse)

    def sendPrivateMessage(self, recName, message):
        if self.state == "unavailable":
            raise Unavailable
            return
        p = Message(frm=self.name + "@" + self.muc_name, typ="error")
        t = Behaviour.MessageTemplate(p)
        b = self.SendPrivateMessageBehaviour(recName, message)
        self.myAgent.addBehaviour(b, t)
        b.join()

    class SendPrivateMessageBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, recName, message):
            Behaviour.OneShotBehaviour.__init__(self)
            self.recName = recName
            self.message = message

        def _process(self):
            m = Message(to=self.recName, typ="chat")
            x = Node(tag="body")
            x.addData(message)
            m.addChild(node=x)
            self.myAgent.jabber.send(m)
            msg = self._receive(True, 10)
            if msg:
                print "This message can't be sent"
            #falta comprobar si la respuesta del servidorforbidden o not-acceptable(este no deberia producirse)

    def setRegistrationForm(self, dataForm):
        pass

    def addUnit(self, unit):
        """
          Creates a new unit inside an organization
          """
        if self.state == "unavailable":
            raise Unavailable
            return
        if self.checkTypes(self.parent_type, unit.type):
        #un sitwch para aquellas organizaciones donde todos puedan crear unidades
            if self.parent_type != "Matrix" and self.parent_type != "Federation":
                if self.checkOwnerAdmin(self.myAgent.JID):
                    unit.create = True
                    unit.parent = self.parent
                    unit.parent_type = self.parent_type
                    if self.orgOwner is None:
                        self.orgOwner = self.getOwnerList()[0]
                    unit.orgOwner = self.orgOwner
                    print self.orgOwner
                    unit.orgOwner = self.orgOwner
                    self.myAgent.addBehaviour(unit)
                else:
                    raise NotCreatePermision
            elif self.checkSupervisor(self.myAgent.JID):
                unit.create = True
                unit.parent = self.parent
                unit.parent_type = self.parent_type
                if self.orgOwner is None:
                    self.orgOwner = self.getOwnerList()[0]
                unit.orgOwner = self.orgOwner
                self.myAgent.addBehaviour(unit)
            else:
                raise NotSupervisor
        else:
            raise NotValidType

    def checkOwnerAdmin(self, agentJID):
        adminList = self.getAdminList()
        ownerList = self.getOwnerList()
        try:
            adminList.index(agentJID)
        except:
            try:
                ownerList.index(agentJID)
            except:
                return False
        return True

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

    def checkSupervisor(self, myAgentJID):
        supervisor = self.getSupervisorList()
        if myAgentJID in supervisor:
            return True
        else:
            return False

    def getSupervisorList(self):
        list = []
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm="Team:" + self.parent + "@" + self.muc_name, attrs={"id": ID})
        t1 = Behaviour.MessageTemplate(p)
        b = self.GetMemberListBehaviour(self.muc_name, "Team:" + self.parent, ID)
        self.myAgent.addBehaviour(b, t1)
        b.join()
        member = b.result
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm="Team:" + self.parent + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetOwnerListBehaviour(self.muc_name, "Team:" + self.parent, ID)
        self.myAgent.addBehaviour(b, t)
        b.join()
        owner = b.result
        ID = "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(5)])
        p = Iq(frm="Team:" + self.parent + "@" + self.muc_name, attrs={"id": ID})
        t = Behaviour.MessageTemplate(p)
        b = self.GetAdminListBehaviour(self.muc_name, "Team:" + self.parent, ID)
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

    def run(self):
        if self.create:
            self.myCreate()
        else:
            self.myJoin()
        self.onStart()
        while (not self.done()) and (not self._forceKill.isSet()):
            self._process()
            #time.sleep(0)
        self.onEnd()
        self.myAgent.removeBehaviour(self)

    def _process(self):
        pass

"""
    def run(self):
        if self.create:
            self.myCreate()
        else:
            self.myJoin()
        self.onStart()
        while (not self.done()) and (not self._forceKill.isSet()):
            self._process()
            #time.sleep(0)
        self.onEnd()
        self.myAgent.removeBehaviour(self)


   def addUNit(self,Name,Type,GoalList,AgentList):
        if checkTypes(self.type,Type):
            if checkOwner(self.myAgent.getJID()):
                return Unit(self.myAgent,self.nick,Name,Type,GoalList,AgentList)
            else:
                print "The Agent isn't the owner of the Organization"
        else:
            print "Unit Type is not a valid type"

   def checkTypes(orgType,unitType):
        if orgType=="Flat":
            return True
        if orgType=="Team" and unitType=="Team":
            return True
        if orgType=="Hierarchy" and unitType=="Hierarchy":
            return True
        if orgType=="Bureaucracy" and unitType=="Hierarchy":
            return True
        if orgType=="Matrix" and unitType=="Team":
            return True
        if orgType=="Matrix" and unitType=="Hierarchy":
            return True
        if orgType=="Federation" and unitType=="Team":
            return True
        if orgType=="Federation" and unitType=="Hierarchy":
            return True
        if orgType=="Coalition" and unitType=="Team":
            return True
        if orgType=="Congregation" and unitType=="Hierarchy":
            return True
        if orgType=="Congregation" and unitType=="Team":
            return True
        if orgType=="Congregation" and unitType=="Flat":
            return True
        return False

   def checkOwner(self,agentJID):
        ownerList=getOwnerList()
        try:
            ownerList.index(agentJID)
        except:
            return False
        return True

   def join(self):
        p = Presence(to=self.name+"@"+self.muc_name+"/"+self.nick)
        x = Protocol("x", xmlns="http://jabber.org/protocol/muc")
        p.addChild(node=x)
        self.myAgent.jabber.send(p)
        #Falta comprobar que se ha unido a la sala sin problemas
        return True


   def setRegistrationForm(self,dataForm):
        pass



"""
