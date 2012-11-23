# -*- coding: utf-8 -*-
from xmpp import *
import types
import copy

import pickle


class BadPassword(Exception):
    '''
    The user provided a wrong password
    '''
    def __init__(self):
        pass


class NotAMember(Exception):
    '''
    The user is not a member of the room
    '''
    def __init__(self):
        pass


class Blacklisted(Exception):
    '''
    The user is in the black list of the room
    '''
    def __init__(self):
        pass


class MaxUsers(Exception):
    '''
    The maximum number of users for this room has been reached
    '''
    def __init__(self):
        pass


class NoVoice(Exception):
    '''
    The user has no voice in this room
    '''
    def __init__(self):
        pass


class NickLockedDown(Exception):
    '''
    The nickname that the user is trying to set is already locked down
    '''
    def __init__(self):
        pass


class Participant:
    """
    A client that participates in a MUC room
    """
    def __init__(self, fulljid, barejid=None, nick=None, role=None, affiliation=None):
        # Get data from constructor
        self.fulljid = fulljid
        # If there was no barejid, build it
        if not barejid:
            self.barejid = str(fulljid).split('/')[0]
        else:
            self.barejid = barejid
        # If there was no nick, take the barejid instead
        if not nick:
            self.nick = self.barejid
        else:
            self.nick = nick
        # If there was no role, take the 'none' role
        if not role:
            self.role = 'none'
        else:
            self.role = role
        # Same as role
        if not affiliation:
            self.affiliation = 'none'
        else:
            self.affiliation = affiliation

    def __str__(self):
        return '<' + str(self.fulljid) + ' barejid="' + str(self.barejid) + '" nick="' + str(self.nick) + '" role="' + str(self.role) + '" affiliation="' + str(self.affiliation) + '">'

    def getFullJID(self):
        """
        Get the participant's full JID
        """
        return self.fulljid

    def getBareJID(self):
        """
        Get the participant's bare JID
        """
        return self.barejid

    def getNick(self):
        """
        Get the participant's nickname
        """
        return self.nick

    def getRole(self):
        """
        Get the participant's role
        """
        if self.role:
            return self.role.lower()
        else:
            return 'none'

    def getAffiliation(self):
        """
        Get the participant's affiliation
        """
        if self.affiliation:
            return self.affiliation.lower()
        else:
            return 'none'

    def setFullJID(self, fulljid):
        """
        Set the participant's full JID
        """
        self.fulljid = fulljid

    def setBareJID(self, barejid):
        """
        Set the participant's bare JID
        """
        self.barejid = barejid

    def setNick(self, nick):
        """
        Set the participant's nickname
        """
        self.nick = nick

    def setRole(self, role):
        """
        Set the participant's role
        """
        self.role = role

    def setAffiliation(self, affiliation):
        """
        Set the participant's affiliation
        """
        self.affiliation = affiliation


class SerializableRoom:
    """
    A serializable (reduced) version of a Room
    """
    def __init__(self, orig):
        # Get original room's important data
        self.config = orig.config
        self.name = orig.name
        self.locked = orig.locked
        self.role_privileges = orig.role_privileges
        self.subject = orig.getSubject()
        self.whitelist = orig.whitelist
        self.blacklist = orig.blacklist
        self.creator = orig.creator


class Room:
    """
    A MUC room
    """
    def __init__(self, name, muc, subject=None, template=None, creator=None, whitelist=[], blacklist=[], password=None):
        # Configuration dict
        self.config = {}

        # The Conference that owns the room
        self.muc = muc
        # Get data from constructor
        self.name = name
        self.config['muc#roomconfig_roomname'] = ""
        self.config['muc#roomconfig_roomdesc'] = ""
        self.config['muc#roomconfig_enablelogging'] = 0
        self.config['muc#roomconfig_lang'] = "en"
        self.config['muc#roomconfig_changesubject'] = 1
        self.config['muc#roomconfig_allowinvites'] = 0
        self.config['muc#roomconfig_maxusers'] = 100
        self.config['muc#roomconfig_minusers'] = 1
        self.config['muc#roomconfig_presencebroadcast'] = ["moderator", "participant", "visitor"]
        self.config['muc#roomconfig_publicroom'] = 1
        self.config['muc#roomconfig_persistentroom'] = 0
        self.config['muc#roomconfig_moderatedroom'] = 0
        self.config['muc#roomconfig_allowregister'] = 0
        self.config['muc#roomconfig_nicklockdown'] = 0
        self.config['muc#roomconfig_membersonly'] = 0
        self.config['muc#roomconfig_passwordprotectedroom'] = 0
        self.config['muc#roomconfig_roomsecret'] = ""
        self.config['muc#roomconfig_whois'] = ""  # FULLY_ANONYMOUS
        self.config['muc#roomconfig_roomadmins'] = []
        self.config['muc#roomconfig_roomowners'] = []

        # Init DEBUG
        self.DEBUG = self.muc.DEBUG

        # Initialize default room specific values
        #self.hidden = False
        #self.open = True
        #self.moderated = False
        #self.anonymous = 'fully'
        #self.unsecured = True
        #self.password = password
        #self.persistent = False
        #self.maxusers = 0  # No max
        self.locked = False  # Locked for other clients than the owner. See MUC XEP Section 9.1.1

        # Initialize default role privileges
        # Every privilege is expressed in a hierarchical form.
        # If a given privilege is granted to a client with the role of 'visitor',
        # all superior roles, will have that privilege too (i.e. 'participant' and 'moderator')
        self.role_privileges = {}
        self.role_privileges['change_nick'] = 'visitor'
        self.role_privileges['send_private'] = 'visitor'
        self.role_privileges['invite'] = 'visitor'
        self.role_privileges['send'] = 'participant'
        self.role_privileges['subject'] = 'participant'

        # If there was no subject, take the first part of the jid instead
        if not subject:
            #self.subject = name
            self.setSubject("")
        else:
            #self.subject = subject
            self.setSubject(subject)
        # If there was a template, change values by default
        if template:
            self.DEBUG("TODO: Implement room templates", 'warn')

        # Initialize white and blacklists
        self.whitelist = copy.copy(whitelist)
        self.blacklist = copy.copy(blacklist)

        # Moderators, owners, voices, etc...
        # Roles. A standard client is considered a "participant", role-wise
        self.moderators = []
        self.visitors = []
        # Initialize participants dict. It will be indexed by the participants full JIDs
        self.participants = {}  # 'jid':'Participant_instance'

        # Affiliations. A outcast is so if he/she is placed in the blacklist
        #self.owners = []
        #self.admins = []

        # List of reserved nicks
        self.reserved_nicks = {}

        # If there was a creator, add it to the participants dict
        if creator:
            self.creator = creator
            #self.owners.append(creator.getBareJID())
            self.addRoomOwner(creator.getBareJID())
            #if self.moderated:
            if self.isModeratedRoom():
                creator.setRole('moderator')
            else:
                creator.setRole('participant')
            creator.setAffiliation('owner')
            self.participants[creator.getFullJID()] = creator
            self.reserved_nicks[creator.getBareJID()] = creator.getNick()
        else:
            self.creator = None

    def getName(self):
        """
        Get the room's true Name
        """
        return self.name

    def setName(self, n):
        """
        Set the room's true Name
        """
        self.name = str(n)

    def getRoomName(self):
        """
        Get the room's RoomName (display name)
        """
        return self.config["muc#roomconfig_roomname"]

    def setRoomName(self, name):
        """
        Set the room's RoomName (display name)
        """
        self.config["muc#roomconfig_roomname"] = name

    def getSubject(self):
        """
        Get the room's Subject (topic)
        """
        return self.subject

    def setSubject(self, name):
        """
        Set the room's Subject (topic)
        """
        self.subject = name

    def getRoomDesc(self):
        """
        Get the room's Description
        """
        return self.config["muc#roomconfig_roomdesc"]

    def setRoomDesc(self, name):
        """
        Set the room's Description
        """
        self.config["muc#roomconfig_roomdesc"] = name

    def isLogging(self):
        """
        Check if message logging is enabled in the room
        """
        return self.config["muc#roomconfig_enablelogging"]

    def setLogging(self, val):
        """
        Enable or disable message logging in the room
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_enablelogging"] = val

    def getLang(self):
        """
        Get the language used in the room
        """
        return self.config["muc#roomconfig_lang"]

    def setLang(self, name):
        """
        Set the language used in the room
        """
        self.config["muc#roomconfig_lang"] = name

    def isChangeSubject(self):  # Enforce this on subject change
        """
        Check wether the subject can be changed in the room
        """
        return self.config["muc#roomconfig_changesubject"]

    def setChangeSubject(self, val):
        """
        Allow or disallow users to change the subject of the room
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_changesubject"] = val

    def isAllowInvites(self):
        """
        Check wether invitations are allowed in the room
        """
        return self.config["muc#roomconfig_allowinvites"]

    def setAllowInvites(self, val):
        """
        Enable or disable invitations to the room
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_allowinvites"] = val

    def getMaxUsers(self):
        """
        Gets maximum number of concurrent users in the room
        """
        return self.config["muc#roomconfig_maxusers"]

    def setMaxUsers(self, m):
        """
        Gets maximum number of concurrent users in the room
        """
        try:
            im = int(m)
            self.config["muc#roomconfig_maxusers"] = im
        except:
            self.config["muc#roomconfig_maxusers"] = 0
        return

    def getMinUsers(self):
        """
        Gets minimum number of concurrent users in the room
        """
        return self.config["muc#roomconfig_minusers"]

    def setMinUsers(self, m):
        """
        Gets maximum number of concurrent users in the room
        """
        try:
            im = int(m)
            self.config["muc#roomconfig_minusers"] = im
        except:
            self.config["muc#roomconfig_minusers"] = 0
        return

    def getPresenceBroadcast(self):  # Enforce this on presence broadcasting
        """
        Get the list of roles which receive presence stanzas broadcasted in the room
        """
        return self.config["muc#roomconfig_presencebroadcast"]

    def addPresenceBroadcast(self, name):
        """
        Add a role to the list of roles which receive presence stanzas broadcasted in the room
        """
        if name not in self.config["muc#roomconfig_presencebroadcast"]:
            self.config["muc#roomconfig_presencebroadcast"].append(name)

    def delPresenceBroadcast(self, name):
        """
        Remove a role from the list of roles which receive presence stanzas broadcasted in the room
        """
        if name in self.config["muc#roomconfig_presencebroadcast"]:
            self.config["muc#roomconfig_presencebroadcast"].remove(name)

    def isPublicRoom(self):
        """
        Check wether the room is public
        """
        return self.config["muc#roomconfig_publicroom"]

    def setPublicRoom(self, val):
        """
        Stablish wether the room public or not. If a room is not public, then it is hidden
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_publicroom"] = val

    def isPersistentRoom(self):
        """
        Check wether the room is persistent
        """
        return self.config["muc#roomconfig_persistentroom"]

    def setPersistentRoom(self, val):
        """
        Set the persistency of the room. If the room is not persistent, then it is temporary
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_persistentroom"] = val

    def isModeratedRoom(self):
        """
        Check wether the room is moderated
        """
        return self.config["muc#roomconfig_moderatedroom"]

    def setModeratedRoom(self, val):
        """
        Make the room (un)moderated. All the required notifications and role changes will take effect
        """
        if val in [0, '0', False]:
            self.config["muc#roomconfig_moderatedroom"] = 0
            for j in self.visitors + self.moderators:
                for k in self.participants.keys():
                    if j in k:
                        self.participants[k].setRole('participant')
                        try:
                            self.visitors.remove(j)
                        except:
                            self.moderators.remove(j)
                for k, to in self.participants.items():
                    #service informs remaining occupants
                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                    relative_frm = self.fullJID() + '/' + to.getNick()
                    newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                    for other in self.participants.values():
                        if self.getWhois() == "anyone" \
                                or self.getWhois() == "moderators" and to.getRole() == "moderator":
                            newitem.setAttr('jid', other.getFullJID())
                        x.addChild(node=newitem)

                        reply = Presence(other.getFullJID(), frm=relative_frm)
                        reply.addChild(node=x)
                        s = self.muc.server.getsession(other.getFullJID())
                        if s:
                            s.enqueue(reply)

        else:
            self.DEBUG("Room %s set to be Moderated" % (self.getName()), "info")
            self.config["muc#roomconfig_moderatedroom"] = 1
            for k, to in self.participants.items():
                self.DEBUG("Checking %s with affiliation %s" % (to.getNick(), to.getAffiliation()))
                if to.getAffiliation() in ['admin', 'owner']:
                    to.setRole("moderator")
                    try:
                        if to.getBareJID() in self.visitors:
                            self.visitors.remove(to.getBareJID())
                        if to.getBareJID() not in self.moderators:
                            self.moderators.append(to.getBareJID())
                        self.DEBUG("Changed role of %s to moderator" % (to.getBareJID()), "ok")
                    except:
                        self.DEBUG("Could not change role for %s" % (to.getBareJID()), "error")
                        return

                    #service informs remaining occupants
                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                    relative_frm = self.fullJID() + '/' + to.getNick()
                    newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                    for other in self.participants.values():
                        if self.getWhois() == "anyone" \
                                or self.getWhois() == "moderators" and to.getRole() == "moderator":
                            newitem.setAttr('jid', other.getFullJID())
                        x.addChild(node=newitem)

                        reply = Presence(other.getFullJID(), frm=relative_frm)
                        reply.addChild(node=x)
                        s = self.muc.server.getsession(other.getFullJID())
                        if s:
                            s.enqueue(reply)
        return

    def isLockedDown(self):
        """
        Check wether the room is locked down. A room is locked down while the owner is configuring it for the first time
        """
        return self.config["muc#roomconfig_nicklockdown"]

    def setLockedDown(self, val):
        """
        Lock or unlock down the room
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_nicklockdown"] = val

    def isAllowRegister(self):
        """
        Check wether the room allows the registration process
        """
        return self.config["muc#roomconfig_allowregister"]

    def setAllowRegister(self, val):
        """
        Enable or disable the registration process to the room
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_allowregister"] = val

    def isMembersOnly(self):
        """
        Check wether the room is members-only
        """
        return self.config["muc#roomconfig_membersonly"]

    def setMembersOnly(self, val):
        """
        Set or unset the room to members-only. If the rooms becomes members-only,
        all the non-members, non-admins and non-owners participants will be
        miserably kicked out
        """
        if val in [0, '0', False]:
            val = 0
            self.DEBUG("Room set to be NOT Members Only", "info")
        else:
            val = 1
            # Copy admins and owner to the whitelist
            """
            for memb in self.getRoomAdmins():
                if memb not in self.whitelist:
                    self.whitelist.append(memb)
            for memb in self.getRoomOwners():
                if memb not in self.whitelist:
                    self.whitelist.append(memb)
            """
            self.DEBUG("Room set to be Members Only", "info")
            # Kick all non-members, non-owners and non-admins out of the room
            for k, to in self.participants.items():
                if to.getBareJID() not in self.whitelist \
                        and to.getAffiliation() in ['outcast', 'none']:

                    to.setRole('none')

                    #service removes kicked occupant
                    self.DEBUG("User %s got his ass kicked" % (str(to)), "warn")
                    relative_frm = self.fullJID() + "/" + to.getNick()
                    p = Presence(to=to.getFullJID(), frm=relative_frm, typ='unavailable')
                    x = Node('x', {'xmlns': "http://jabber.org/protocol/muc#user"})
                    newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole()})
                    reason = Node('reason')
                    reason.addData("Room is now Members-Only")
                    newitem.addChild(node=reason)
                    actor = Node('actor', {'jid': self.fullJID()})
                    newitem.addChild(node=actor)
                    x.addChild(node=newitem)
                    status = Node('status', {'code': '307'})
                    x.addChild(node=status)
                    p.addChild(node=x)
                    s = self.muc.server.getsession(to.getFullJID())
                    if s:
                        s.enqueue(p)
                    self.deleteParticipant(to.getFullJID())

                    #service informs remaining occupants
                    relative_frm = self.fullJID() + '/' + to.getNick()
                    # If 'to' equals the 'relative from' of the sender, exit the room
                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                    status = Node('status', {'code': '307'})
                    x.addChild(node=status)
                    for other in self.participants.values():
                        item = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole()})
                        if self.getWhois() != "" and other.getRole() == "moderator":
                            item.setAttr('jid', to.getFullJID())
                        x.addChild(node=item)
                        reply = Presence(other.getFullJID(), 'unavailable', frm=relative_frm)
                        reply.addChild(node=x)
                        s = self.muc.server.getsession(other.getFullJID())
                        if s:
                            s.enqueue(reply)

        self.config["muc#roomconfig_membersonly"] = val

    def isPasswordProtectedRoom(self):
        """
        Check wether entrance to the room is protected by a password
        """
        return self.config["muc#roomconfig_passwordprotectedroom"]

    def setPasswordProtectedRoom(self, val):
        """
        Enable or disable password-protection. Note that this method does NOT set the password itself. To set the actual password use I{setPassword}
        """
        if val in [0, '0', False]:
            val = 0
        else:
            val = 1
        self.config["muc#roomconfig_passwordprotectedroom"] = val

    def getPassword(self):
        """
        Get the password of the room
        """
        return self.config["muc#roomconfig_roomsecret"]

    def setPassword(self, name):
        """
        Set the actual password of the room
        """
        self.config["muc#roomconfig_roomsecret"] = name

    def getWhois(self):
        """
        Get the whois permission
        """
        return self.config["muc#roomconfig_whois"]

    def setWhois(self, name):
        """
        Set the whois permission. Possible values are:
        - 'anyone' : the room is non-anonymous
        - 'moderators' : the room is semi-anonymous
        - '' (empty) : the room is fully-anonymous
        """
        if name in ['anyone', 'moderators', '']:
            self.config["muc#roomconfig_whois"] = name

    def getRoomAdmins(self):
        """
        Get the list of room admins
        """
        return self.config["muc#roomconfig_roomadmins"]

    def addRoomAdmin(self, name):
        """
        Add an admin to the room
        """
        if name not in self.config["muc#roomconfig_roomadmins"]:
            self.config["muc#roomconfig_roomadmins"].append(name)
        else:
            return
        barejid = JID(name).getStripped()
        self.reserveNick(barejid, None)  # Pre-reserve nick

        for k, v in self.participants.items():
            if barejid in k:
                # Set this participant (k,v) to admin
                self.DEBUG("Granting admin privileges to " + k, "info")
                v.setAffiliation('admin')
                self.reserveNick(v.getBareJID(), v.getNick())
                # Add the participant to the correct lists and change the role
                if barejid not in self.moderators:
                    if barejid in self.visitors:
                        self.visitors.remove(barejid)
                    if self.isModeratedRoom():
                        v.setRole('moderator')
                        self.moderators.append(barejid)
                    else:
                        v.setRole('participant')
                    if self.isMembersOnly():
                        if barejid not in self.whitelist:
                            self.whitelist.append(barejid)
                break

        #service informs remaining occupants
        #if jid in self.participants.keys():
        for p in self.participants.values():
            if p.getBareJID() == barejid:
                nick = p.getNick()
                relative_frm = self.fullJID() + '/' + nick
                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                newitem = Node('item', {'affiliation': 'admin'})
                newitem.setAttr('role', p.getRole())
                if nick:
                    newitem.setAttr('nick', nick)
                if self.getWhois() == "anyone" \
                        or self.getWhois() == "moderators" and other.getRole() == "moderator":
                    newitem.setAttr('jid', barejid)
                x.addChild(node=newitem)

                for other in self.participants.values():
                    reply = Presence(other.getFullJID(), frm=relative_frm)
                    reply.addChild(node=x)
                    s = self.muc.server.getsession(other.getFullJID())
                    if s:
                        s.enqueue(reply)
                return

    def delRoomAdmin(self, name):
        """
        Remove an admin from the room
        """
        if name in self.config["muc#roomconfig_roomadmins"]:
            self.config["muc#roomconfig_roomadmins"].remove(name)
        else:
            return
        barejid = JID(name).getStripped()

        for k, v in self.participants.items():
            if barejid in k:
                    # Set this participant (k,v) to member
                self.DEBUG("Removing admin privileges to " + k, "info")
                if self.isMembersOnly():
                    v.setAffiliation('member')
                else:
                    v.setAffiliation('none')
                    try:
                        del self.reserved_nicks[barejid]
                    except:
                        pass
                # Add the participant to the correct lists and change the role
                if self.isModeratedRoom():
                    if barejid in self.moderators:
                        self.moderators.remove(barejid)
                    v.setRole('participant')
                else:
                    v.setRole('visitor')
                    if barejid not in self.visitors:
                        self.visitors.append(barejid)

                break

        #service informs remaining occupants
        for p in self.participants.values():
            if p.getBareJID() == barejid:
                nick = p.getNick()
                relative_frm = self.fullJID() + '/' + nick
                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                newitem = Node('item', {'affiliation': p.getAffiliation()})
                newitem.setAttr('role', p.getRole())
                if nick:
                    newitem.setAttr('nick', nick)
                if self.getWhois() == "anyone" \
                        or self.getWhois() == "moderators" and other.getRole() == "moderator":
                    newitem.setAttr('jid', barejid)
                x.addChild(node=newitem)

                for other in self.participants.values():
                    reply = Presence(other.getFullJID(), frm=relative_frm)
                    reply.addChild(node=x)
                    s = self.muc.server.getsession(other.getFullJID())
                    if s:
                        s.enqueue(reply)
                return

    def getRoomOwners(self):
        """
        Get the list of room owners
        """
        return self.config["muc#roomconfig_roomowners"]

    def addRoomOwner(self, name):
        """
        Add a room owner
        """
        if name not in self.config["muc#roomconfig_roomowners"]:
            self.config["muc#roomconfig_roomowners"].append(name)
        else:
            return
        barejid = JID(name).getStripped()
        self.reserveNick(barejid, None)  # Pre-reserve nick

        for k, v in self.participants.items():
            if barejid in k:
                    # Set this participant (k,v) to admin
                self.DEBUG("Granting owner privileges to " + k, "info")
                v.setAffiliation('owner')
                self.reserveNick(v.getBareJID(), v.getNick())
                # Add the participant to the correct lists and change the role
                if barejid not in self.moderators:
                    if barejid in self.visitors:
                        self.visitors.remove(barejid)
                    if self.isModeratedRoom():
                        v.setRole('moderator')
                        self.moderators.append(barejid)
                    else:
                        v.setRole('participant')
                    if self.isMembersOnly():
                        if barejid not in self.whitelist:
                            self.whitelist.append(barejid)

                break

        #service informs remaining occupants
        #if jid in self.participants.keys():
        for p in self.participants.values():
            if p.getBareJID() == barejid:
                nick = p.getNick()
                relative_frm = self.fullJID() + '/' + nick
                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                newitem = Node('item', {'affiliation': 'owner'})
                newitem.setAttr('role', p.getRole())
                if nick:
                    newitem.setAttr('nick', nick)
                if self.getWhois() == "anyone" \
                        or self.getWhois() == "moderators" and other.getRole() == "moderator":
                    newitem.setAttr('jid', barejid)
                x.addChild(node=newitem)

                for other in self.participants.values():
                    reply = Presence(other.getFullJID(), frm=relative_frm)
                    reply.addChild(node=x)
                    s = self.muc.server.getsession(other.getFullJID())
                    if s:
                        s.enqueue(reply)
                return

    def delRoomOwner(self, name):
        """
        Remove an owner from the room. Will not work if there is only one owner and tries to step down
        """
        if name in self.config["muc#roomconfig_roomowners"]:
            self.config["muc#roomconfig_roomowners"].remove(name)
        else:
            return
        barejid = JID(name).getStripped()

        for k, v in self.participants.items():
            if barejid in k:
                    # Set this participant (k,v) to member
                self.DEBUG("Removing owner privileges to " + k, "info")
                if self.isMembersOnly():
                    v.setAffiliation('member')
                else:
                    v.setAffiliation('none')
                    try:
                        del self.reserved_nicks[barejid]
                    except:
                        pass
                # Add the participant to the correct lists and change the role
                if self.isModeratedRoom():
                    if barejid in self.moderators:
                        self.moderators.remove(barejid)
                    v.setRole('participant')
                else:
                    v.setRole('visitor')
                    if barejid not in self.visitors:
                        self.visitors.append(barejid)
                break

        #service informs remaining occupants
        for p in self.participants.values():
            if p.getBareJID() == barejid:
                nick = p.getNick()
                relative_frm = self.fullJID() + '/' + nick
                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                newitem = Node('item', {'affiliation': p.getAffiliation()})
                newitem.setAttr('role', p.getRole())
                if nick:
                    newitem.setAttr('nick', nick)
                if self.getWhois() == "anyone" \
                        or self.getWhois() == "moderators" and other.getRole() == "moderator":
                    newitem.setAttr('jid', barejid)
                x.addChild(node=newitem)

                for other in self.participants.values():
                    reply = Presence(other.getFullJID(), frm=relative_frm)
                    reply.addChild(node=x)
                    s = self.muc.server.getsession(other.getFullJID())
                    if s:
                        s.enqueue(reply)
                return

    def __str__(self):
        """
        Return a string representation of the room
        """
        """
        s = str(self.name) + ": " + self.subject
        s = s + "\nLocked = " + str(self.locked)
        s = s + "\nHidden = " + str(self.hidden) + "\nOpen = " + str(self.open) + "\nModerated = " + str(self.moderated) + "\nAnonymous = " + str(self.anonymous) + "\nUnsecured = " + str(self.unsecured) + "\nPersistent = " + str(self.persistent)
        s = s + "\nRole Privileges = " + str(self.role_privileges)
        s = s + "\nParticipants = " + str(self.participants.keys())
        if self.creator:
            s = s + "\nCreator = " + str(self.creator.getFullJID())
        s = s + "\nWhitelist = " + str(self.whitelist)
        s = s + "\nBlacklist = " + str(self.blacklist)
        s = s + "\nOwners = " + str(self.owners)
        s = s + "\nAdmins = " + str(self.admins)
        s = s + "\nModerators = " + str(self.moderators)
        s = s + "\nVisitors = " + str(self.visitors)
        """
        s = ""
        s = str(self.name) + ": " + self.subject
        s = s + "\nLocked = " + str(self.locked)
        s = s + "\nParticipants = " + str(self.participants.keys())
        if self.creator:
            s = s + "\nCreator = " + str(self.creator.getFullJID())
        s = s + "\nWhitelist = " + str(self.whitelist)
        s = s + "\nBlacklist = " + str(self.blacklist)
        s = s + "\nModerators = " + str(self.moderators)
        s = s + "\nVisitors = " + str(self.visitors)
        s = s + "\nReserved Nicks = " + str(self.reserved_nicks) + "\n"
        for k in self.config.keys():
            s = s + str(k) + ": " + str(self.config[k]) + "\n"
        return s

    def fullJID(self):
        """
        Returns the room's full JID in the form of I{room@muc.platform}
        """
        return str(self.name) + '@' + str(self.muc.jid)

    def dispatch(self, session, stanza):
        """
        Mini-dispatcher for the jabber stanzas that arrive to the room
        """
        self.muc.DEBUG("Room '" + self.getName() + "' dispatcher called")
        if stanza.getName() == 'iq':
            self.IQ_cb(session, stanza)
        elif stanza.getName() == 'presence':
            self.Presence_cb(session, stanza)
        elif stanza.getName() == 'message':
            self.Message_cb(session, stanza)
        # TODO: Implement the rest of protocols

    def Message_cb(self, session, stanza):
        """
        Manages messages directed to a room
        """
        self.DEBUG("Message callback of room %s called" % (self.getName()), "info")
        frm = str(session.peer)
        to = stanza['to']
        typ = stanza.getAttr('type')
        if typ == 'groupchat':
            # Message should be to the room itself
            if str(to) == self.fullJID():
                self.DEBUG("Message directed to the room itself: " + str(self.getName()), 'info')
                subject = stanza.getTag('subject')
                # A 'subject'-change message
                if subject:
                    if self.isChangeSubject():
                        if not self.isModeratedRoom():
                            # Unmoderated room, change the subject
                            try:
                                # Get the participant who changes the subject
                                p = self.participants[frm]
                                self.setSubject(subject.getData())
                                self.DEBUG("Subject changed to " + str(subject.getData()), "info")
                                self.muc.saveRoomDB()
                            except:
                                # Not a participant of this room
                                return
                        else:
                            # Moderated room, check permissions
                            try:
                                p = self.participants[frm]
                                if p.getRole() == 'moderator':
                                    #Change the subject
                                    self.setSubject(subject.getData())
                                    self.DEBUG("Subject changed to " + str(subject.getData()), "info")
                                    self.muc.saveRoomDB()
                                else:
                                    # Not enough permissions
                                    self.DEBUG("Not enough permissions to change subject", "warn")
                                    stanza.setTo(frm)
                                    stanza.setFrom(self.fullJID())
                                    stanza.setType('error')
                                    err = Node('error', {'code': '403', 'type': 'auth'})
                                    badr = Node('forbidden', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                                    err.addChild(node=badr)
                                    stanza.addChild(node=err)
                                    session.enqueue(stanza)
                                    return
                            except:
                                # Error changing the subject
                                return
                        # Notify the change of subject
                        try:
                            relative_frm = self.fullJID() + '/' + p.getNick()
                            stanza.setFrom(relative_frm)
                            for participant in self.participants.values():
                                stanza.setTo(participant.getFullJID())
                                s = self.muc.server.getsession(participant.getFullJID())
                                s.enqueue(stanza)
                        except:
                            # Error sending the subject change
                            return
                    else:
                        # Not enough permissions
                        self.DEBUG("Not enough permissions to change subject", "warn")
                        stanza.setTo(frm)
                        stanza.setFrom(self.fullJID())
                        stanza.setType('error')
                        err = Node('error', {'code': '403', 'type': 'auth'})
                        badr = Node('forbidden', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                        err.addChild(node=badr)
                        stanza.addChild(node=err)
                        session.enqueue(stanza)
                        return

                # General message to everyone
                elif frm in self.participants:
                    try:
                        if self.isModeratedRoom() and JID(frm).getStripped() in self.visitors:  # Visitor in a moderated room
                            raise NoVoice

                        self.DEBUG("General message from %s to everyone in room %s" % (str(frm), str(self.getName())), 'info')
                        # Change the 'from'
                        messenger = self.participants[frm]
                        stanza.setFrom(self.fullJID() + '/' + messenger.getNick())
                        for participant in self.participants.values():
                            stanza.setTo(participant.getFullJID())
                            s = self.muc.server.getsession(participant.getFullJID())
                            if s:
                                s.enqueue(stanza)

                        # Special bot-like commands
                        if stanza.getBody() == ".str" or stanza.getBody() == u".str":
                            print self
                        if stanza.getBody() == ".savedb" or stanza.getBody() == u".savedb":
                            self.muc.saveRoomDB()
                        if stanza.getBody() == ".rooms" or stanza.getBody() == u".rooms":
                            for k, v in self.muc.rooms.items():
                                print k, str(v)
                        return

                    except NoVoice:
                        self.DEBUG("This user has No voice", 'warn')
                        stanza.setTo(frm)
                        stanza.setFrom(self.fullJID())
                        stanza.setType('error')
                        err = Node('error', {'code': '403', 'type': 'auth'})
                        badr = Node('forbidden', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                        err.addChild(node=badr)
                        stanza.addChild(node=err)
                        session.enqueue(stanza)
                        return
                else:
                    self.DEBUG("Message from an outsider", "warn")
                    stanza.setTo(frm)
                    stanza.setFrom(self.fullJID())
                    stanza.setType('error')
                    err = Node('error', {'code': '406', 'type': 'cancel'})
                    badr = Node('not-acceptable', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                    err.addChild(node=badr)
                    stanza.addChild(node=err)
                    session.enqueue(stanza)
                    return

            else:
                self.DEBUG("Message of 'groupchat' type directed to a particular participant. That is wrong!", "warn")
                stanza.setTo(frm)
                stanza.setFrom(self.fullJID())
                stanza.setType('error')
                err = Node('error', {'code': '400', 'type': 'modify'})
                badr = Node('bad-request', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                err.addChild(node=badr)
                stanza.addChild(node=err)
                session.enqueue(stanza)
                return

        elif typ == 'chat':
            self.DEBUG("Private message within room " + self.getName(), "info")
            try:
                nick = to.getResource()
            except:
                return

            try:
                for k, v in self.participants.items():
                    if v.getNick() == nick:
                        self.DEBUG("Private message for nick " + nick)
                        stanza.setTo(k)
                        if frm not in self.participants:
                            return
                        stanza.setFrom(self.fullJID() + '/' + self.participants[frm].getNick())
                        s = self.muc.server.getsession(k)
                        if s:
                            s.enqueue(stanza)
                        return
            except:
                self.DEBUG("Error forwarding private message", "error")

        elif not typ:
            self.DEBUG("Not type!", "warn")
            # Is it an invitation?
            for child in stanza.getTags('x'):
                if child.getNamespace() == "http://jabber.org/protocol/muc#user":
                    if child.getTag('invite'):
                        if self.isAllowInvites():
                            self.DEBUG("An invitation", "info")
                            # It's an invitation
                            mess = Message()
                            mess.setFrom(self.fullJID())
                            invite_node = child.getTag('invite')
                            invite_to = invite_node.getAttr('to')
                            if invite_to:
                                # Add new member to the room if it is members only
                                #if not self.open:
                                if self.isMembersOnly():
                                    self.whitelist.append(invite_to)

                                mess.setTo(invite_to)
                                mess.setBody("You have been invited to room %s by %s" % (str(self.getName()), str(frm)))
                                x = Node('x', attrs={'xmlns': 'http://jabber.org/protocol/muc#user'})
                                inv = Node('invite', attrs={'from': frm})
                                for c in invite_node.getChildren():
                                    inv.addChild(node=c)
                                x.addChild(node=inv)
                                #if self.password:
                                if self.getPassword():
                                    pwd = Node('password')
                                    pwd.setData(self.getPassword())  # With two balls
                                    x.addChild(node=pwd)
                                mess.addChild(node=x)
                                x = Node('x', attrs={'xmlns': 'jabber:x:conference', 'jid': self.fullJID()})
                                reason = invite_node.getTagData('reason')
                                if reason:
                                    x.setData(reason)
                                mess.addChild(node=x)
                                s = self.muc.server.getsession(invite_to)
                                if s:
                                    s.enqueue(mess)
                                return
                            else:
                                #send an "item-not-found error" to the sender
                                reply = Message(frm, frm=self.fullJID(), typ='error')
                                err = Node('error', {'code': '404', 'type': 'cancel'})
                                reply.addChild(node=err)
                                session.enqueue(reply)
                                return

                        else:
                            #send a "not-allowed error" to the sender
                            reply = Message(frm, frm=self.fullJID(), typ='error')
                            na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                            err = Node('error', {'code': '405', 'type': 'cancel'})
                            err.addChild(node=na)
                            reply.addChild(node=err)
                            session.enqueue(reply)
                            return

                    elif child.getTag('decline'):
                        self.DEBUG("Decline invitation", "info")
                        mess = Message()
                        mess.setFrom(self.fullJID())
                        decline_node = child.getTag('decline')
                        decline_to = decline_node.getAttr('to')
                        if decline_to:
                            # Remove member to the room if it is members only
                            #if not self.open and decline_to in self.whitelist:
                            if self.isMembersOnly() and decline_to in self.whitelist:
                                self.whitelist.remove(decline_to)

                            mess.setTo(decline_to)
                            x = Node('x', attrs={'xmlns': 'http://jabber.org/protocol/muc#user'})
                            dec = Node('decline', attrs={'from': frm})
                            for c in decline_node.getChildren():
                                dec.addChild(node=c)
                            x.addChild(node=dec)
                            mess.addChild(node=x)

                            s = self.muc.server.getsession(decline_to)
                            if s:
                                s.enqueue(mess)
                            return
                        else:
                            #send an "item-not-found error" to the sender
                            reply = Message(frm, frm=self.fullJID(), typ='error')
                            err = Node('error', {'code': '404', 'type': 'cancel'})
                            reply.addChild(node=err)
                            session.enqueue(reply)
                            return

            self.DEBUG("Private message without 'chat' type. Re-dispatching", "info")
            stanza.setType('chat')
            self.dispatch(session, stanza)
            return

    def Presence_cb(self, session, stanza):
        """
        Manages presence stanzas directed to a room
        """
        self.muc.DEBUG("Room '" + self.getName() + "' presence handler called")
        # Analyze the 'to' element from the stanza
        to = stanza['to']
        room = to.getNode()
        domain = to.getDomain()
        nick = to.getResource()
        frm = str(session.peer)
        typ = stanza.getType()
        try:
            password = None
            for x in stanza.getTags('x'):
                if x.getNamespace() == "http://jabber.org/protocol/muc":
                    if x.getTag("password"):
                        password = x.T.password.getData()
        except:
            password = None

        if typ is None or typ == 'available':  # Not sure about the 'available' part
            # Process a client's request to join the room
            # Check wether the room is locked (for non-owners)
            if self.locked and JID(frm).getStripped() not in self.getRoomOwners():
                # Send a not-allowed error
                self.DEBUG("Non-owner trying to enter locked room. Nope.", "warn")
                rr = Node('item-not-found', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                err = Node('error', {'code': '404', 'type': 'cancel'})
                err.addChild(node=rr)
                p = Presence(frm, 'error', frm=self.fullJID())
                p.addChild(node=err)
                session.enqueue(p)
                return

            # If there is no nick, we must send back an error 400
            if nick == '':
                self.DEBUG("There is no nick, we must send back an error 400", 'warn')
                reply = Presence(frm, 'error', frm=self.fullJID())
                error = Node('error', {'code': '400', 'type': 'modify'})
                error.setTag('jid-malformed', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                reply.addChild(node=error)
                session.enqueue(reply)
                return
            else:
                # Check nick unicity
                for k, p in self.participants.items():
                    if p.getNick() == nick and frm != k:
                        # OMG nick conflict!
                        self.DEBUG("Nickname conflict !!!", "warn")
                        reply = Presence(frm, frm=self.fullJID(), typ='error')
                        err = Node('error', {'code': '409', 'type': 'cancel'})
                        conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                        err.addChild(node=conflict)
                        reply.addChild(node=err)
                        session.enqueue(reply)
                        return

            # Check wether the nick is reserved
            for j, n in self.reserved_nicks.items():
                if n and n == nick and j != JID(frm).getStripped():
                    # CONFLICT!
                    self.DEBUG("Nickname conflict", 'warn')
                    reply = Presence(frm, frm=self.fullJID(), typ='error')
                    err = Node('error', {'code': '409', 'type': 'cancel'})
                    conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                    err.addChild(node=conflict)
                    reply.addChild(node=err)
                    session.enqueue(reply)
                    return

            # Check if its a nick change
            if frm in self.participants:
                oldnick = self.participants[frm].getNick()
                if nick != oldnick:
                    # It is indeed a nick change
                    # Check wether the new nick is available
                    self.DEBUG("Nick change", 'info')
                    if self.isLockedDown():
                        # Nickname conflict, report back to the changer
                        self.DEBUG("Nickname conflict", 'warn')
                        reply = Presence(frm, frm=self.fullJID(), typ='error')
                        err = Node('error', {'code': '409', 'type': 'cancel'})
                        conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                        err.addChild(node=conflict)
                        reply.addChild(node=err)
                        session.enqueue(reply)
                        return
                    for p in self.participants.values():
                        if nick == p.getNick():
                            # Nickname conflict, report back to the changer
                            self.DEBUG("Nickname conflict", 'warn')
                            reply = Presence(frm, frm=self.fullJID(), typ='error')
                            err = Node('error', {'code': '409', 'type': 'cancel'})
                            conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                            err.addChild(node=conflict)
                            reply.addChild(node=err)
                            session.enqueue(reply)
                            return
                    # Now we must send an 'unavailable' Presence to everyone (in this room)
                    # with status code 303 (and the new nick) on behalf of the changer
                    p = self.participants[frm]
                    relative_frm = self.fullJID() + '/' + p.getNick()
                    pres = Presence(frm=relative_frm, typ='unavailable')
                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                    item = Node('item', {'affiliation': p.getAffiliation(), 'role': p.getRole(), 'nick': nick})
                    status = Node('status', {'code': '303'})
                    x.addChild(node=item)
                    x.addChild(node=status)
                    pres.addChild(node=x)
                    for participant in self.participants.values():
                        pres.setTo(participant.getFullJID())
                        s = self.muc.server.getsession(participant.getFullJID())
                        if s:
                            s.enqueue(pres)
                    # Change the nick in the participant instance
                    p.setNick(nick)

            try:
                # Try to add a participant to the room. If it everything goes well,
                # addParticipant will return True. Otherwise, it will throw a
                # specific exception, catched later
                if self.addParticipant(fulljid=frm, nick=nick, password=password):
                    self.DEBUG("New Participant has correct credentials", "info")
                    # Conform first standard reply
                    #reply = Presence( frm, frm=self.fullJID() )
                    #x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc'} )
                    #reply.addChild(node=x)
                    #session.enqueue(reply)

                    # Send presence information from existing participants to the new participant
                    for k, participant in self.participants.items():
                        relative_frm = self.fullJID() + '/' + participant.getNick()
                        reply = Presence(frm, frm=relative_frm)
                        x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                        item = Node('item', {'affiliation': participant.getAffiliation(), 'role': participant.getRole()})
                        #if self.anonymous == "semi":
                        if self.getWhois() == "moderators":
                            if self.participants[frm].getRole() == "moderator":
                                item.setAttr('jid', k)
                        #elif self.anonymous == "non":
                        elif self.getWhois() == "anyone":
                            item.setAttr('jid', k)
                        x.addChild(node=item)
                        reply.addChild(node=x)
                        # Get extended presence attributes
                        try:
                            p = self.muc.server.Router._data[participant.getBareJID()][JID(k).getResource()]
                            for child in p.getChildren():
                                reply.addChild(node=child)
                        except:
                            print self.muc.server.data
                        session.enqueue(reply)

                    # Send new participant's presence to all participants
                    relative_frm = self.fullJID() + '/' + nick  # Newcomer's relative JID
                    newcomer = self.participants[frm]
                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                    item = Node('item', {'affiliation': str(newcomer.getAffiliation()), 'role': str(newcomer.getRole())})
                    #if self.anonymous == "semi":
                    if self.getWhois() == "moderators":  # Semi-Anonymous
                        if newcomer.getRole() == "moderator":
                            item.setAttr('jid', frm)
                    #elif self.anonymous == "non":
                    elif self.getWhois() == "anyone":
                        item.setAttr('jid', frm)

                    x.addChild(node=item)
                    for participant in self.participants.values():
                        reply = Presence(participant.getFullJID(), frm=relative_frm)
                        reply.addChild(node=x)
                        for child in stanza.getChildren():
                            reply.addChild(node=child)
                        s = self.muc.server.getsession(participant.getFullJID())
                        self.DEBUG("Session " + str(s) + " found for client " + participant.getFullJID(), 'info')
                        if s:
                            s.enqueue(reply)
                    # If the room is non-anonymous, send a warning message to the new occupant
                    #if self.anonymous == "non":
                    if self.getWhois() == "anyone":
                        warning = Message(frm, "This room is not anonymous.", frm=self.fullJID(), typ="groupchat")
                        x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                        status = Node('status', {'code': 100})
                        x.addChild(node=status)
                        warning.addChild(node=x)
                        session.enqueue(warning)

                    if self.getSubject():
                        subj = Message(frm, frm=self.fullJID(), typ="groupchat")
                        s = Node('subject')
                        s.addData(self.getSubject())
                        subj.addChild(node=s)
                        session.enqueue(subj)

            except BadPassword:
                # The client sent a bad password
                self.DEBUG("The client sent a bad password", "warn")
                rr = Node('not-authorized', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                err = Node('error', {'code': '401', 'type': 'auth'})
                err.addChild(node=rr)
                p = Presence(frm, 'error', frm=self.fullJID())
                p.addChild(node=err)
                session.enqueue(p)

            except NotAMember:
                # the client is not a member of this room
                self.DEBUG("the client is not a member of this room", "warn")
                rr = Node('registration-required', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                err = Node('error', {'code': '407', 'type': 'auth'})
                err.addChild(node=rr)
                p = Presence(frm, 'error', frm=self.fullJID())
                p.addChild(node=err)
                session.enqueue(p)

            except Blacklisted:
                self.DEBUG("The client is blacklisted", "warn")
                rr = Node('forbidden', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                err = Node('error', {'code': '403', 'type': 'auth'})
                err.addChild(node=rr)
                p = Presence(frm, 'error', frm=self.fullJID())
                p.addChild(node=err)
                session.enqueue(p)

            except MaxUsers:
                self.DEBUG("MaxUsers reached", "warn")
                rr = Node('service-unavailable', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                err = Node('error', {'code': '503', 'type': 'wait'})
                err.addChild(node=rr)
                p = Presence(frm, 'error', frm=self.fullJID())
                p.addChild(node=err)
                session.enqueue(p)

            except NickLockedDown:
                self.DEBUG("The Nick is Locked Down", "warn")
                reply = Presence(frm, frm=self.fullJID(), typ='error')
                err = Node('error', {'code': '409', 'type': 'cancel'})
                conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                err.addChild(node=conflict)
                reply.addChild(node=err)
                session.enqueue(reply)
                return

            except Exception, e:
                self.DEBUG("Access Check failed with unknowk exception: " + str(e), 'error')

            return

        elif typ == 'unavailable':
            try:
                participant = self.participants[frm]
            except:
                return
            relative_frm = self.fullJID() + '/' + participant.getNick()
            # If 'to' equals the 'relative from' of the sender, exit the room
            if str(to) == relative_frm:
                # Send leaving participant's presence to all participants
                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                item = Node('item', {'affiliation': str(participant.getAffiliation()), 'role': str(participant.getRole())})
                x.addChild(node=item)
                for other in self.participants.values():
                    reply = Presence(other.getFullJID(), 'unavailable', frm=relative_frm)
                    reply.addChild(node=x)
                    if stanza.getTag('status'):
                        reply.addChild(node=stanza.getTag('status'))
                    s = self.muc.server.getsession(other.getFullJID())
                    self.DEBUG("Session " + str(s) + " found for client " + other.getFullJID(), 'info')
                    if s:
                        s.enqueue(reply)
            self.deleteParticipant(frm)
            # Check if an empty room must be destroyed (if its temporary)
            if len(self.participants.keys()) == 0:
                # Empty room
                if not self.isPersistentRoom():
                    del self.muc.rooms[self.getName()]

            # TODO:
            # If an 'unavailable' presence is sent from the owner of a room that is locked (configuring),
            # the Conference must delete such room

            return

    def IQ_cb(self, session, iq):
        """
        Manages IQ stanzas directed to a room
        """
        self.DEBUG("IQ callback of room %s called" % (self.getName()), "info")
        # Look for the query xml namespace
        query = iq.getTag('query')
        frm = str(session.peer)
        stanza = iq
        if query:
            try:
                ns = str(iq.getQueryNS())
                typ = str(iq.getType())
                nod = iq.getQuerynode()
                id = iq.getAttr('id')
                # Discovery Info
                if ns == NS_DISCO_INFO and typ == 'get' and nod is None:
                    # Build reply
                    reply = Iq('result', NS_DISCO_INFO, to=frm, frm=str(self.fullJID()))
                    rquery = reply.getTag('query')
                    if id:
                        reply.setAttr('id', id)
                    # Fill 'identity' item
                    identity = {'category': 'conference', 'type': 'text', 'name': self.getRoomName()}
                    rquery.setTag('identity', identity)
                    # Fill 'feature' items, representing the features that the room supports
                    feature = {'var': 'http://jabber.org/protocol/muc'}
                    rquery.setTag('feature', feature)
                    # See the specific features of the room
                    #if self.hidden:
                    if not self.isPublicRoom():
                        feature = {'var': 'muc_hidden'}
                        rquery.setTag('feature', feature)
                    #if self.open:
                    if not self.isMembersOnly():
                        feature = {'var': 'muc_open'}
                        rquery.setTag('feature', feature)
                    if not self.isModeratedRoom():
                        feature = {'var': 'muc_unmoderated'}
                        rquery.setTag('feature', feature)
                    #if self.anonymous == "non":
                    if self.getWhois() == "anyone":
                        feature = {'var': 'muc_nonanonymous'}
                        rquery.setTag('feature', feature)
                    if not self.isPersistentRoom():
                        feature = {'var': 'muc_temporary'}
                        rquery.setTag('feature', feature)
                    if self.isPasswordProtectedRoom():
                        feature = {'var': 'muc_passwordprotected'}
                        rquery.setTag('feature', feature)
                    # Fill in Extended Disco Info Results using DataForms
                    if self.isPublicRoom():
                        df = DataForm(typ="result")
                        field = DataField()
                        df.addChild(node=DataField(name="FORM_TYPE", value="http://jabber.org/protocol/muc#roominfo", typ="hidden"))
                        field = DataField(name="muc#roominfo_description", value=self.getRoomDesc())
                        field.setAttr('label', 'Description')
                        df.addChild(node=field)
                        field = DataField(name="muc#roominfo_subject", value=self.getSubject())
                        field.setAttr('label', 'Subject')
                        df.addChild(node=field)
                        field = DataField(name="muc#roominfo_occupants", value=str(len(self.participants.keys())))
                        field.setAttr('label', 'Number of occupants')
                        df.addChild(node=field)
                        field = DataField(name="muc#roominfo_maxusers", value=str(self.getMaxUsers()))
                        field.setAttr('label', 'Maximum number of occupants')
                        df.addChild(node=field)
                        field = DataField(name="muc#roominfo_minusers", value=str(self.getMinUsers()))
                        field.setAttr('label', 'Minimum number of occupants')
                        df.addChild(node=field)
                        field = DataField(name="muc#roominfo_lang", value=self.getLang())
                        field.setAttr('label', 'Language of discussion')
                        df.addChild(node=field)
                        rquery.addChild(node=df)
                    session.enqueue(reply)

                # Traffic is not supported at this time
                elif ns == NS_DISCO_INFO and typ == 'get' and nod == 'http://jabber.org/protocol/muc#traffic':
                    self.DEBUG("TRAFFIC IQ REQUEST", 'info')
                    # Generate an error 501
                    reply = Iq('error', NS_DISCO_INFO, to=frm, frm=self.fullJID())
                    rquery = reply.getTag('query')
                    id = iq.getAttr('id')
                    if id:
                        reply.setAttr('id', id)
                    error = Node('error', {'code': 501, 'type': 'cancel'})
                    error.setTag('feature-not-implemented', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                    text = Node('text', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                    text.addData('The feature requested is not implemented by the recipient or server and therefore cannot be processed.')
                    error.addChild(node=text)
                    reply.addChild(node=error)
                    session.enqueue(reply)
                    return

                elif ns == NS_DISCO_INFO and typ == 'get' and nod == 'x-roomuser-item':
                    # Forgetful user requesting his nick
                    self.DEBUG("User %s requests its own nick" % (frm), "info")
                    reply = stanza.buildReply(typ="result")
                    id = iq.getAttr('id')
                    if id:
                        reply.setAttr('id', id)
                    if JID(frm).getStripped() in self.reserved_nicks:
                        nick = self.reserved_nicks[JID(frm).getStripped()]
                        if nick:
                            i = reply.T.query.NT.identity
                            i.setAttr("name", nick)
                            i.setAttr("category", "conference")
                            i.setAttr("type", "text")
                    session.enqueue(reply)
                    return

                elif ns == NS_DISCO_ITEMS and typ == 'get':
                    # Return a list of participants in the rooms
                    # We leave it in TODO, for the moment, we return an empty list
                    self.DEBUG("NS_DISCO_ITEMS requested", "warn")
                    # Build reply
                    reply = Iq('result', NS_DISCO_ITEMS, to=iq.getFrom(), frm=str(self.fullJID()))
                    rquery = reply.getTag('query')
                    id = iq.getAttr('id')
                    if id:
                        reply.setAttr('id', id)
                    if self.isPublicRoom():
                        for k, p in self.participants.items():
                            item = Node('item', {'jid': self.fullJID() + "/" + p.getNick()})
                            rquery.addChild(node=item)
                    session.enqueue(reply)

                elif ns == "http://jabber.org/protocol/muc#admin" and typ == 'set':
                    self.DEBUG("Admin command", "info")
                    for item in query.getTags('item'):
                        nick = item.getAttr('nick')
                        affiliation = item.getAttr('affiliation')
                        role = item.getAttr('role')
                        jid = item.getAttr('jid')
                        to = None
                        for k, v in self.participants.items():
                            if nick:
                                if v.getNick() == nick:
                                    to = v
                                    jid = v.getBareJID()
                            elif jid:
                                if v.getBareJID() == jid:
                                    to = v
                                    nick = to.getNick()
                        if not to:
                            #build a 'virtual' participant
                            to = Participant(jid)
                            if nick:
                                to.setNick(nick)
                            if jid in self.moderators:
                                to.setRole('moderator')
                            elif jid in self.visitors:
                                to.setRole('visitor')
                            else:
                                to.setRole('none')
                            if jid in self.blacklist:
                                to.setAffiliation('outcast')
                            elif jid in self.whitelist:
                                to.setAffiliation('member')
                            elif jid in self.getRoomAdmins():
                                to.setAffiliation('admin')
                            elif jid in self.getRoomOwners():
                                to.setAffiliation('owner')
                            else:
                                to.setAffiliation('none')

                        # Role-related commands
                        if self.participants[frm].getRole() == 'moderator':
                            if role == "none" and (nick or jid) and not affiliation:  # kicked
                                # Compare affiliations
                                my_aff = self.participants[frm].getAffiliation()
                                if my_aff == "outcast" \
                                    or my_aff == "none" and to.getAffiliation() in ['none', 'member', 'admin', 'owner'] \
                                    or my_aff == "member" and to.getAffiliation() in ['admin', 'owner', 'member'] \
                                    or my_aff == "admin" and to.getAffiliation() in ['owner', 'admin'] \
                                        or to.getAffiliation() in ['owner']:
                                    self.DEBUG("Service returns error on atempt to kick user with higher affiliation", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                to.setRole('none')

                                #service removes kicked occupant
                                self.DEBUG("User %s got his ass kicked" % (str(to.getNick())), "info")
                                p = Presence(to=to.getFullJID(), frm=self.fullJID() + "/" + to.getNick(), typ='unavailable')
                                x = Node('x', {'xmlns': "http://jabber.org/protocol/muc#user"})
                                newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole()})
                                actor = Node('actor', {'jid': JID(frm).getStripped()})
                                status = Node('status', {'code': '307'})
                                for child in item.getChildren():
                                    newitem.addChild(node=child)
                                newitem.addChild(node=actor)
                                x.addChild(node=newitem)
                                x.addChild(node=status)
                                p.addChild(node=x)
                                s = self.muc.server.getsession(to.getFullJID())
                                if s:
                                    s.enqueue(p)
                                to_aff = to.getAffiliation()
                                self.deleteParticipant(to.getFullJID())

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                #service informs remaining occupants
                                relative_frm = self.fullJID() + '/' + nick
                                # If 'to' equals the 'relative from' of the sender, exit the room
                                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                status = Node('status', {'code': '307'})
                                x.addChild(node=status)
                                item = Node('item', {'affiliation': to_aff, 'role': to.getRole()})
                                if self.getWhois() != "" and self.participants[frm].getRole() == "moderator":
                                    item.setAttr('jid', to.getFullJID())
                                x.addChild(node=item)

                                for other in self.participants.values():
                                    reply = Presence(other.getFullJID(), 'unavailable', frm=relative_frm)
                                    reply.addChild(node=x)
                                    s = self.muc.server.getsession(other.getFullJID())
                                    if s:
                                        s.enqueue(reply)
                                return

                            elif role == "participant" and (nick or jid) and not affiliation:  # Granting voice to a visitor
                                # Compare affiliations
                                my_aff = self.participants[frm].getAffiliation()
                                if my_aff == "outcast" \
                                    or my_aff == "none" and to.getAffiliation() in ['none', 'member', 'admin', 'owner'] \
                                    or my_aff == "member" and to.getAffiliation() in ['admin', 'owner', 'member'] \
                                    or my_aff == "admin" and to.getAffiliation() in ['owner', 'admin'] \
                                        or to.getAffiliation() in ['owner']:
                                    self.DEBUG("Service returns error on atempt to kick user with higher affiliation", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                #if to.getRole() in ['moderator','participant']:
                                #	self.DEBUG("Cannot grant voice to a moderator or participant","warn")
                                #	return

                                to.setRole("participant")
                                try:
                                    self.visitors.remove(to.getBareJID())
                                except:
                                    self.DEBUG("Could not remove %s from visitors" % (to.getBareJID()), "warn")

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                #service informs remaining occupants
                                relative_frm = self.fullJID() + '/' + to.getNick()
                                # If 'to' equals the 'relative from' of the sender, exit the room
                                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                                if self.getWhois() != "" and self.participants[frm].getRole() == "moderator":
                                    newitem.setAttr('jid', to.getFullJID())
                                for child in item.getChildren():
                                    newitem.addChild(node=child)
                                x.addChild(node=newitem)

                                for other in self.participants.values():
                                    reply = Presence(other.getFullJID(), frm=relative_frm)
                                    reply.addChild(node=x)
                                    s = self.muc.server.getsession(other.getFullJID())
                                    if s:
                                        s.enqueue(reply)
                                return

                            elif role == "visitor" and (nick or jid) and not affiliation:  # Denying voice to a participant
                                if to.getRole() == 'moderator':
                                    # Special case: denying voice to a moderator. Compare affiliations
                                    my_aff = self.participants[frm].getAffiliation()
                                    if to.getAffiliation() in ['owner'] \
                                            or my_aff == 'admin' and to.getAffiliation() in ['owner', 'admin']:
                                        self.DEBUG("Affiliation is not high enough to deny voice", "warn")
                                        reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                        id = iq.getAttr('id')
                                        if id:
                                            reply.setAttr('id', id)
                                        reply.NT.query.addChild(node=item)
                                        reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                        na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                        err = Node('error', {'code': '405', 'type': 'cancel'})
                                        err.addChild(node=na)
                                        reply.addChild(node=err)
                                        session.enqueue(reply)
                                        return

                                to.setRole("visitor")
                                try:
                                    if to.getBareJID() not in self.visitors:
                                        self.visitors.append(to.getBareJID())
                                    if to.getBareJID() in self.moderators:
                                        self.moderators.remove(to.getBareJID())
                                except:
                                    self.DEBUG("Could not change role for %s" % (to.getBareJID()), "error")
                                    return

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                #service informs remaining occupants
                                relative_frm = self.fullJID() + '/' + to.getNick()
                                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                                if self.getWhois() == "anyone" \
                                        or self.getWhois() == "moderators" and self.participants[frm].getRole() == "moderator":
                                    newitem.setAttr('jid', to.getFullJID())
                                for child in item.getChildren():
                                    newitem.addChild(node=child)
                                x.addChild(node=newitem)

                                for other in self.participants.values():
                                    reply = Presence(other.getFullJID(), frm=relative_frm)
                                    reply.addChild(node=x)
                                    s = self.muc.server.getsession(other.getFullJID())
                                    if s:
                                        s.enqueue(reply)
                                return

                        if self.participants[frm].getAffiliation() in ['owner', 'admin']:
                            if role == "moderator" and (nick or jid) and not affiliation:  # Grant moderator privileges
                                if self.participants[frm].getAffiliation() not in ['owner', 'admin']:
                                    self.DEBUG("Affiliation is not enough to give moderation", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                to.setRole("moderator")
                                try:
                                    if to.getBareJID() in self.visitors:
                                        self.visitors.remove(to.getBareJID())
                                    if to.getBareJID() not in self.moderators:
                                        self.moderators.append(to.getBareJID())
                                except:
                                    self.DEBUG("Could not change role for %s" % (to.getBareJID()), "error")
                                    return

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                #service informs remaining occupants
                                relative_frm = self.fullJID() + '/' + to.getNick()
                                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                                if self.getWhois() == "anyone" \
                                        or self.getWhois() == "moderators" and self.participants[frm].getRole() == "moderator":
                                    newitem.setAttr('jid', to.getFullJID())
                                for child in item.getChildren():
                                    newitem.addChild(node=child)
                                x.addChild(node=newitem)
                                for other in self.participants.values():
                                    reply = Presence(other.getFullJID(), frm=relative_frm)
                                    reply.addChild(node=x)
                                    s = self.muc.server.getsession(other.getFullJID())
                                    if s:
                                        s.enqueue(reply)
                                return

                        # Affiliation-related commands
                        if self.participants[frm].getAffiliation() in ['owner', 'admin']:
                            if affiliation == "outcast" and jid and not role:  # Ban a user
                                my_aff = self.participants[frm].getAffiliation()
                                # Check if an owner is affecting himself
                                if JID(frm).getStripped() == to.getBareJID() and \
                                        my_aff in ['admin', 'owner']:
                                    # An owner is trying step down but he is the last of his kind
                                    # OR and admin or owner is trying to ban himself
                                    # We must prevent this to happen
                                    reply = stanza.buildReply(typ="error")
                                    err = Node('error', {'code': '409', 'type': 'cancel'})
                                    conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                                    err.addChild(node=conflict)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                if my_aff == "admin" and to.getAffiliation() not in ['member', 'none'] \
                                    or my_aff == "owner" and to.getAffiliation() not in ['admin', 'member', 'none']\
                                        or my_aff not in ['admin', 'owner']:
                                    self.DEBUG("Affiliation is not enough to Ban user", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                to.setAffiliation("outcast")
                                to.setRole('none')
                                try:
                                    if to.getBareJID() in self.whitelist:
                                        self.whitelist.remove(to.getBareJID())
                                    if to.getBareJID() not in self.blacklist:
                                        self.blacklist.append(to.getBareJID())
                                except:
                                    self.DEBUG("Could not change affiliation for %s" % (to.getBareJID()), "error")
                                    return

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                #service informs banned user (if he's present in the room)
                                if to.getFullJID() in self.participants.keys():
                                    other = self.participants[frm]
                                    relative_frm = self.fullJID() + '/' + to.getNick()
                                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                    newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                                    if self.getWhois() == "anyone" \
                                            or self.getWhois() == "moderators" and self.participants[frm].getRole() == "moderator":
                                        newitem.setAttr('jid', to.getFullJID())
                                        actor = Node('actor', {'jid': other.getBareJID()})
                                        x.addChild(node=actor)
                                    for child in item.getChildren():
                                        newitem.addChild(node=child)
                                    status = Node('status', {'code': '301'})
                                    x.addChild(node=newitem)
                                    x.addChild(node=status)
                                    reply = Presence(to=to.getFullJID(), frm=relative_frm, typ='unavailable')
                                    reply.addChild(node=x)
                                    s = self.muc.server.getsession(to.getFullJID())
                                    if s:
                                        s.enqueue(reply)
                                    self.deleteParticipant(to.getFullJID())

                                #service informs remaining occupants
                                relative_frm = self.fullJID() + '/' + to.getNick()
                                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                                if self.getWhois() == "anyone" \
                                        or self.getWhois() == "moderators" and self.participants[frm].getRole() == "moderator":
                                    newitem.setAttr('jid', to.getFullJID())
                                #for child in item.getChildren():
                                #	newitem.addChild(node=child)
                                status = Node('status', {'code': '301'})
                                x.addChild(node=newitem)
                                for other in self.participants.values():
                                    reply = Presence(other.getFullJID(), frm=relative_frm, typ='unavailable')
                                    reply.addChild(node=x)
                                    s = self.muc.server.getsession(other.getFullJID())
                                    if s:
                                        s.enqueue(reply)
                                return

                            elif affiliation == "none" and (jid or nick) and not role:  # Revoke membership
                                my_aff = self.participants[frm].getAffiliation()
                                # Check if an owner is affecting himself
                                if JID(frm).getStripped() == to.getBareJID() and \
                                        my_aff == "owner" and len(self.getRoomOwners()) == 1:
                                    # An owner is trying step down but he is the last of his kind
                                    # We must prevent this to happen
                                    reply = stanza.buildReply(typ="error")
                                    err = Node('error', {'code': '409', 'type': 'cancel'})
                                    conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                                    err.addChild(node=conflict)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                if my_aff == "admin" and to.getAffiliation() not in ['member', 'none', 'outcast'] \
                                    or my_aff == "owner" and to.getAffiliation() not in ['admin', 'member', 'none', 'outcast']\
                                        or my_aff not in ['admin', 'owner']:

                                    self.DEBUG("Affiliation is not enough to Grant membership", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                to.setAffiliation("none")
                                try:
                                    del self.reserved_nicks[barejid]
                                except:
                                    pass
                                #if self.isModeratedRoom() and to.getRole() in ['participant','moderator']:
                                #	to.setRole('visitor')

                                if jid in self.whitelist:
                                    self.whitelist.remove(jid)
                                if jid in self.blacklist:
                                    self.blacklist.remove(jid)

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                #service removes non-member
                                #if not self.open:
                                if self.isMembersOnly():
                                    other = self.participants[frm]
                                    relative_frm = self.fullJID() + '/' + to.getNick()
                                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                    newitem = Node('item', {'affiliation': to.getAffiliation(), 'role': to.getRole(), 'nick': to.getNick()})
                                    if self.getWhois() == "anyone" \
                                            or self.getWhois() == "moderators" and self.participants[frm].getRole() == "moderator":
                                        newitem.setAttr('jid', to.getFullJID())
                                    for child in item.getChildren():
                                        newitem.addChild(node=child)
                                    status = Node('status', {'code': '321'})
                                    actor = Node('actor', {'jid': frm})
                                    x.addChild(node=actor)
                                    x.addChild(node=newitem)
                                    reply = Presence(to=to.getFullJID(), frm=relative_frm, typ='unavailable')
                                    reply.addChild(node=x)
                                    s = self.muc.server.getsession(to.getFullJID())
                                    if s:
                                        s.enqueue(reply)
                                        self.deleteParticipant(to.getFullJID())

                                    #service informs remaining occupants
                                    #for p in self.participants.values():
                                    #   if p.getBareJID() == jid:
                                    relative_frm = self.fullJID() + '/' + to.getNick()
                                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                    newitem = Node('item', {'affiliation': to.getAffiliation()})
                                    newitem.setAttr('role', to.getRole())
                                    newitem.setAttr('nick', to.getNick())
                                    if self.getWhois() == "anyone" \
                                            or self.getWhois() == "moderators" and self.participants[frm].getRole() == "moderator":
                                        newitem.setAttr('jid', to.getFullJID())
                                    x.addChild(node=newitem)
                                    for other in self.participants.values():
                                        reply = Presence(other.getFullJID(), frm=relative_frm, typ='unavailable')
                                        reply.addChild(node=x)
                                        s = self.muc.server.getsession(other.getFullJID())
                                        if s:
                                            s.enqueue(reply)
                                    return

                            elif affiliation == "member" and (jid or nick) and not role:  # Grant membership
                                my_aff = self.participants[frm].getAffiliation()
                                # Check if an owner is affecting himself
                                if JID(frm).getStripped() == to.getBareJID() and \
                                        my_aff == "owner" and len(self.getRoomOwners()) == 1:
                                    # An owner is trying step down but he is the last of his kind
                                    # We must prevent this to happen
                                    self.DEBUG("The last owner MUST NOT step down", "warn")
                                    reply = stanza.buildReply(typ="error")
                                    err = Node('error', {'code': '409', 'type': 'cancel'})
                                    conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                                    err.addChild(node=conflict)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                if my_aff not in ['admin', 'owner']:
                                    self.DEBUG("Affiliation is not enough to Grant membership", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                self.DEBUG("Granting membership to " + to.getBareJID(), "info")

                                to.setAffiliation("member")
                                #to.setRole('participant')
                                if nick:
                                    self.reserveNick(to.getBareJID(), nick)
                                else:
                                    self.reserveNick(to.getBareJID(), None)  # Pre-reserve nick

                                if jid not in self.whitelist:
                                    self.whitelist.append(jid)
                                if jid in self.blacklist:
                                    self.blacklist.remove(jid)
                                if jid in self.visitors:
                                    self.visitors.remove(jid)

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                #service informs remaining occupants
                                #if jid in self.participants.keys():
                                for p in self.participants.values():
                                    if p.getBareJID() == jid:
                                        relative_frm = self.fullJID() + '/' + nick
                                        x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                                        newitem = Node('item', {'affiliation': to.getAffiliation()})
                                        newitem.setAttr('role', to.getRole())
                                        newitem.setAttr('nick', to.getNick())
                                        if self.getWhois() == "anyone" \
                                                or self.getWhois() == "moderators" and self.participants[frm].getRole() == "moderator":
                                            newitem.setAttr('jid', jid)
                                        x.addChild(node=newitem)

                                        for other in self.participants.values():
                                            reply = Presence(other.getFullJID(), frm=relative_frm)
                                            reply.addChild(node=x)
                                            s = self.muc.server.getsession(other.getFullJID())
                                            if s:
                                                s.enqueue(reply)
                                        return

                            elif affiliation == "admin" and (jid or nick) and not role:  # Grant admin privileges
                                my_aff = self.participants[frm].getAffiliation()
                                # Check if an owner is affecting himself
                                if JID(frm).getStripped() == to.getBareJID() and \
                                        my_aff == "owner" and len(self.getRoomOwners()) == 1:
                                        # An owner is trying step down but he is the last of his kind
                                        # We must prevent this to happen
                                    reply = stanza.buildReply(typ="error")
                                    err = Node('error', {'code': '409', 'type': 'cancel'})
                                    conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                                    err.addChild(node=conflict)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                if my_aff not in ['owner']:
                                    self.DEBUG("Affiliation is not enough to Grant administrative privileges", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                """
                                self.DEBUG("Granting admin privileges to "+str(to),"info")
                                if to:
                                    to.setAffiliation("admin")

                                for p in self.participants.values():
                                    if p.getBareJID() == jid:
                                    if jid not in self.moderators:
                                        if jid in self.visitors:
                                            self.visitors.remove(jid)
                                        if self.isModeratedRoom():
                                            to.setRole('moderator')
                                            self.moderators.append(jid)
                                        else:
                                            to.setRole('participant')
                                """

                                if jid not in self.getRoomAdmins():
                                    self.addRoomAdmin(jid)
                                if jid in self.getRoomOwners():
                                    self.delRoomOwner(jid)

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                """
                                #service informs remaining occupants
                                #if jid in self.participants.keys():
                                for p in self.participants.values():
                                    if p.getBareJID() == jid:
                                    relative_frm = self.fullJID() + '/' + nick
                                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'} )
                                    for other in self.participants.values():
                                        newitem = Node('item', {'affiliation': affiliation})
                                        newitem.setAttr('role',to.getRole())
                                        if nick: newitem.setAttr('nick',nick)

                                        #if self.anonymous == "non" \
                                        #or self.anonymous == "semi" and other.getRole() == "moderator":
                                        if self.getWhois()== "anyone" \
                                        or self.getWhois() == "moderators" and other.getRole() == "moderator":
                                            newitem.setAttr('jid', jid)
                                        x.addChild(node=newitem)
                                        reply = Presence( other.getFullJID(), frm=relative_frm )
                                        reply.addChild(node=x)
                                        s = self.muc.server.getsession(other.getFullJID())
                                        if s:
                                            s.enqueue(reply)
                                    return
                                """

                                return

                            elif affiliation == "owner" and (jid or nick) and not role:  # Grant admin privileges
                                if self.participants[frm].getAffiliation() not in ['owner']:
                                    self.DEBUG("Affiliation is not enough to Grant owner privileges", "warn")
                                    reply = Iq(frm=self.fullJID(), to=frm, typ="error")
                                    id = iq.getAttr('id')
                                    if id:
                                        reply.setAttr('id', id)
                                    reply.NT.query.addChild(node=item)
                                    reply.setQueryNS("http://jabber.org/protocol/muc#admin")
                                    na = Node('not-allowed', {'xmlns': "urn:ietf:params:xml:ns:xmpp-stanzas"})
                                    err = Node('error', {'code': '405', 'type': 'cancel'})
                                    err.addChild(node=na)
                                    reply.addChild(node=err)
                                    session.enqueue(reply)
                                    return

                                """
                                if to:
                                    to.setAffiliation("owner")
                                """

                                if jid not in self.getRoomOwners():
                                    self.addRoomOwner(jid)
                                if jid in self.getRoomAdmins():
                                    self.delRoomAdmin(jid)

                                """
                                for p in self.participants.values():
                                    if p.getBareJID() == jid:
                                    if jid not in self.moderators:
                                        if jid in self.visitors:
                                            self.visitors.remove(jid)
                                        if self.isModeratedRoom():
                                            to.setRole('moderator')
                                            self.moderators.append(jid)
                                        else:
                                            to.setRole('participant')
                                """

                                #service informs moderator of success
                                result = Iq(to=frm, frm=self.fullJID(), typ='result')
                                session.enqueue(result)

                                """
                                #service informs remaining occupants
                                #if jid in self.participants.keys():
                                for p in self.participants.values():
                                    if p.getBareJID() == jid:
                                    relative_frm = self.fullJID() + '/' + nick
                                    x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'} )
                                    for other in self.participants.values():
                                        newitem = Node('item', {'affiliation': affiliation})
                                        newitem.setAttr('role',to.getRole())
                                        if nick: newitem.setAttr('nick',nick)

                                        #if self.anonymous == "non" \
                                        #or self.anonymous == "semi" and other.getRole() == "moderator":
                                        if self.getWhois()== "anyone" \
                                        or self.getWhois() == "moderators" and other.getRole() == "moderator":
                                            newitem.setAttr('jid', jid)
                                        x.addChild(node=newitem)
                                        reply = Presence( other.getFullJID(), frm=relative_frm )
                                        reply.addChild(node=x)
                                        s = self.muc.server.getsession(other.getFullJID())
                                        if s:
                                            s.enqueue(reply)
                                    return
                                """
                                return

                elif ns == "http://jabber.org/protocol/muc#admin" and typ == 'get':
                    self.DEBUG("Admin query", "info")
                    if self.participants[frm].getRole() == "moderator" or \
                            self.participants[frm].getAffiliation() in ['admin', 'owner']:
                        for item in query.getTags('item'):
                            nick = item.getAttr('nick')
                            affiliation = item.getAttr('affiliation')
                            role = item.getAttr('role')
                            jid = item.getAttr('jid')
                            to = None
                            for k, v in self.participants.items():
                                if v.getNick() == nick:
                                    to = v
                            sender = self.participants[frm]
                            if role and not nick and not affiliation:
                                self.DEBUG("Retrieving list of " + role + "s", "info")
                                reply = Iq(typ='result', frm=self.fullJID(), to=frm, queryNS="http://jabber.org/protocol/muc#admin")
                                id = iq.getAttr('id')
                                if id:
                                    reply.setAttr('id', id)
                                for k, v in self.participants.items():
                                    if v.getRole() == role:
                                        newitem = Node('item', {'nick': v.getNick(), 'role': v.getRole(), 'affiliation': v.getAffiliation()})
                                        #if not self.anonymous == "fully":
                                        if self.getWhois():
                                            newitem.setAttr('jid', k)
                                        reply.T.query.addChild(node=newitem)
                                reply.setID(stanza.getID())
                                session.enqueue(reply)
                                return

                            elif affiliation and not nick and not role:
                                self.DEBUG("Retrieving list of " + affiliation + "s", "info")
                                reply = Iq(typ='result', frm=self.fullJID(), to=frm, queryNS="http://jabber.org/protocol/muc#admin")
                                id = iq.getAttr('id')
                                if id:
                                    reply.setAttr('id', id)
                                if affiliation == 'outcast':
                                    for v in self.blacklist:
                                        newitem = Node('item', {'affiliation': 'outcast'})
                                        newitem.setAttr('jid', v)
                                        reply.T.query.addChild(node=newitem)
                                elif affiliation == 'member':
                                    for v in self.whitelist:
                                        newitem = Node('item', {'affiliation': 'member'})
                                        newitem.setAttr('jid', v)
                                        if v in self.participants.keys():
                                            p = self.participants[v]
                                            newitem.setAttr('nick', p.getNick())
                                            newitem.setAttr('role', p.getRole())
                                        reply.T.query.addChild(node=newitem)

                                elif affiliation == 'owner':
                                    for v in self.getRoomOwners():
                                        newitem = Node('item', {'affiliation': 'owner'})
                                        newitem.setAttr('jid', v)
                                        if v in self.participants.keys():
                                            p = self.participants[v]
                                            newitem.setAttr('nick', p.getNick())
                                            newitem.setAttr('role', p.getRole())
                                        reply.T.query.addChild(node=newitem)

                                elif affiliation == 'admin':
                                    for v in self.getRoomAdmins():
                                        newitem = Node('item', {'affiliation': 'admin'})
                                        newitem.setAttr('jid', v)
                                        if v in self.participants.keys():
                                            p = self.participants[v]
                                            newitem.setAttr('nick', p.getNick())
                                            newitem.setAttr('role', p.getRole())
                                        reply.T.query.addChild(node=newitem)
                                reply.setID(stanza.getID())
                                session.enqueue(reply)
                                return

                elif ns == "http://jabber.org/protocol/muc#owner" and typ == 'set':
                    if self.participants[frm].getAffiliation() == "owner":
                        # Test for a destruction
                        try:
                            if stanza.T.query.getTag('destroy'):
                                destroy = True
                            else:
                                destroy = False
                        except:
                            destroy = False

                        if destroy:
                            self.DEBUG("Owner DESTROYING room " + self.getName())
                            self.muc.destroyRoom(self.getName(), session, stanza)
                        else:
                            # Owner sets room properties
                            self.DEBUG("Owner sends room configuration")
                            for child in stanza.T.query.getTags('x'):
                                if child.getNamespace() == "jabber:x:data" and child.getAttr('type') == "submit":
                                    # Confirmation of room. Let's see if there's a form
                                    if child.getTags('field'):  # If it has any children it's a form :-O
                                        self.DEBUG("Configuring room " + self.getName())
                                        self.configRoom(child)
                                    self.locked = False
                                    iq = Iq(frm=self.fullJID(), to=frm, typ='result')
                                    iq.setID(stanza.getID())
                                    session.enqueue(iq)
                                elif child.getNamespace() == "jabber:x:data" and child.getType() == "cancel":
                                    #del self if locked
                                    if self.locked:
                                        del self.muc.rooms[self.getName()]
                            self.muc.saveRoomDB()
                    else:
                        # Forbidden
                        reply = stanza.buildReply(typ="error")
                        err = Node('error', {'code': '403', 'type': 'auth'})
                        badr = Node('forbidden', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                        err.addChild(node=badr)
                        reply.addChild(node=err)
                        session.enqueue(reply)
                    return

                elif ns == "http://jabber.org/protocol/muc#owner" and typ == 'get':
                    if self.participants[frm].getAffiliation() == "owner":
                        # Owner requests room properties
                        #iq = Iq(frm=self.fullJID(), to=frm, typ='result')
                        iq = stanza.buildReply('result')
                        iq.setQueryNS(ns)
                        form = DataForm()
                        form.setTitle("Configuration for %s room" % (self.getName()))
                        form.setInstructions("Your room has been created\nThe default configuration is good enough for you.\nIf you want to screw up this implementation, please fill in the form.")
                        df = DataField("FORM_TYPE", "http://jabber.org/protocol/muc#roomconfig", "hidden")
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_roomname", typ="text-single")
                        df.addValue(self.getRoomName())
                        df.setAttr("label", "Natural-Language Room Name")
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_roomdesc", typ="text-single")
                        df.setAttr("label", "Short Description of Room")
                        df.addValue(self.getRoomDesc())
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_lang", typ="text-single")
                        df.setAttr("label", "Natural Language for Room Discussions")
                        df.addValue(self.getLang())
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_enablelogging", typ="boolean")
                        df.setAttr("label", "Enable Logging?")
                        df.addValue(str(self.isLogging()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_changesubject", typ="boolean")
                        df.setAttr("label", "Allow Occupants to Change Subject?")
                        df.addValue(str(self.isChangeSubject()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_allowinvites", typ="boolean")
                        df.setAttr("label", "Allow Occupants to Invite Others?")
                        df.addValue(str(self.isAllowInvites()))
                        form.addChild(node=df)
                        #df = DataField(name="muc#roomconfig_maxusers",typ="list-single")
                        df = DataField(name="muc#roomconfig_maxusers", typ="text-single")
                        df.setAttr("label", "Maximum Number of Occupants")
                        df.addValue(str(self.getMaxUsers()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_minusers", typ="text-single")
                        df.setAttr("label", "Minimum Number of Occupants")
                        df.addValue(str(self.getMinUsers()))
                        #df.addOption(('10',10))
                        #df.addOption(('20',10))
                        #df.addOption(('30',10))
                        #df.addOption(('50',10))
                        #df.addOption(('100',10))
                        #df.addOption(('None',""))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_presencebroadcast", typ="list-multi")
                        df.setAttr("label", "Roles for which Presence is Broadcast")
                        for v in self.getPresenceBroadcast():
                            df.addValue(str(v))
                        df.addOption(('Moderator', "moderator"))
                        df.addOption(('Participant', "participant"))
                        df.addOption(('Visitor', "visitor"))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_publicroom", typ="boolean")
                        df.setAttr("label", "Make Room Publicy Searchable?")
                        df.addValue(str(self.isPublicRoom()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_persistentroom", typ="boolean")
                        df.setAttr("label", "Make Room Persistent?")
                        df.addValue(str(self.isPersistentRoom()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_moderatedroom", typ="boolean")
                        df.setAttr("label", "Make Room Moderated?")
                        df.addValue(str(self.isModeratedRoom()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_membersonly", typ="boolean")
                        df.setAttr("label", "Make Room Members-Only?")
                        df.addValue(str(self.isMembersOnly()))
                        form.addChild(node=df)
                        # EYE! New custom fields
                        df = DataField(name="muc#roomconfig_allowregister", typ="boolean")
                        df.setAttr("label", "Allow users to register as members?")
                        df.addValue(str(self.isAllowRegister()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_nicklockdown", typ="boolean")
                        df.setAttr("label", "Force members to use the registered nickname?")
                        df.addValue(str(self.isLockedDown()))
                        form.addChild(node=df)
                        # End of custom fields
                        df = DataField(name="muc#roomconfig_passwordprotectedroom", typ="boolean")
                        df.setAttr("label", "Password Required to Enter?")
                        df.addValue(str(self.isPasswordProtectedRoom()))
                        form.addChild(node=df)
                        df = DataField(typ="fixed")
                        df.addValue("If a password is required to enter this room, you must specify the password below.")
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_roomsecret", typ="text-private")
                        df.setAttr("label", "Password")
                        df.addValue(str(self.getPassword()))
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_whois", typ="list-single")
                        df.setAttr("label", "Who May Discover Real JIDs?")
                        df.addOption(('Moderators Only', "moderators"))
                        df.addOption(('Anyone', "anyone"))
                        df.addOption(('Nobody (Fully-Anonymous)', ""))
                        df.addValue(self.getWhois())
                        form.addChild(node=df)
                        df = DataField(typ="fixed")
                        df.addValue("You may specify additional people who have administrative privileges in the room. Please provide one Jabber ID per line.")
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_roomadmins", typ="jid-multi")
                        df.setAttr("label", "Room Admins")
                        for a in self.getRoomAdmins():
                            df.addValue(a)
                        form.addChild(node=df)
                        df = DataField(typ="fixed")
                        df.addValue("You may specify additional owners for this room. Please provide one Jabber ID per line.")
                        form.addChild(node=df)
                        df = DataField(name="muc#roomconfig_roomowners", typ="jid-multi")
                        df.setAttr("label", "Room Owners")
                        for a in self.getRoomOwners():
                            df.addValue(a)
                        form.addChild(node=df)

                        iq.T.query.addChild(node=form)

                        session.enqueue(iq)
                        return

                elif ns == NS_REGISTER and typ == 'get':
                    # User wants registration information of a room
                    # Check wether the user is already registered
                    if JID(frm).getStripped() in self.whitelist or \
                        JID(frm).getStripped() in self.getRoomOwners() or \
                            JID(frm).getStripped() in self.getRoomAdmins():
                        # Already registered
                        reply = stanza.buildReply(typ="result")
                        reply.setTag("register")
                        session.enqueue(reply)
                        return
                    else:
                        # User not registered. Send a registration form
                        reply = stanza.buildReply(typ="result")
                        df = DataForm(typ="form", title=self.getRoomName() + " Registration Form")
                        df.addInstructions("Please fill in this form in order to register with this room.")
                        field = DataField(name="FORM_TYPE", value="http://jabber.org/protocol/muc#register", typ="hidden")
                        df.addChild(node=field)
                        field = DataField(name="muc#register_first", typ="text-single")
                        field.setAttr("label", "First Name")
                        df.addChild(node=field)
                        field = DataField(name="muc#register_last", typ="text-single")
                        field.setAttr("label", "Last Name")
                        df.addChild(node=field)
                        field = DataField(name="muc#register_roomnick", typ="text-single", required=1)
                        field.setAttr("label", "Desired Nickname")
                        df.addChild(node=field)
                        field = DataField(name="muc#register_url", typ="text-single")
                        field.setAttr("label", "Your URL")
                        df.addChild(node=field)
                        field = DataField(name="muc#register_email", typ="text-single")
                        field.setAttr("label", "Email Address")
                        df.addChild(node=field)
                        field = DataField(name="muc#register_faqentry", typ="text-multi")
                        field.setAttr("label", "FAQ Entry")
                        df.addChild(node=field)
                        reply.T.query.addChild(node=df)
                        session.enqueue(reply)
                        return

                elif ns == NS_REGISTER and typ == 'set':
                    # A user attempts to register in the room
                    self.DEBUG("User attempts to register in room " + self.getName(), "info")

                    if not self.isAllowRegister():
                        self.DEBUG("Registration is NOT allowed on room " + self.getName(), "warn")
                        reply = stanza.buildReply(typ="error")
                        err = Node('error', {'code': '503', 'type': 'cancel'})
                        err.setTag('service-unavailable', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                        reply.addChild(node=err)
                        session.enqueue(reply)
                        return

                    # Check wether the user is already registered
                    if JID(frm).getStripped() in self.whitelist or \
                        JID(frm).getStripped() in self.getRoomOwners() or \
                            JID(frm).getStripped() in self.getRoomAdmins():
                        # Already registered
                        reply = stanza.buildReply(typ="result")
                        reply.setTag("register")
                        session.enqueue(reply)
                        return

                    for child in stanza.T.query.getTags('x'):
                        if child.getNamespace() == "jabber:x:data" and child.getAttr('type') == "submit":
                            # Confirmation of registration. Let's see if there's a form
                            if child.getTags('field'):  # If it has any children it's a form :-O
                                self.DEBUG("Registering user in room " + self.getName())
                                if self.processRegistration(child, frm, stanza, session):
                                    iq = Iq(frm=self.fullJID(), to=frm, typ='result')
                                    session.enqueue(iq)
                    self.muc.saveRoomDB()

            except:
                self.DEBUG("No xmlns, don't know what to do", "error")

    def reserveNick(self, jid, nick=None):
        """
        Reserve a nick in a the room.
        A jid can make a pre-reservation (nick == None).
        If a jid already has a correct nick reserved, it cannot be changed.
        """
        # <internal_joke>
        # loop:   goto _start
        # _start: add r0,r2
        #         ld r4,(r0)
        #         bnez r4,_start
        # </internal_joke>

        if nick:
            for j, n in self.reserved_nicks.items():
                if nick == n:
                    self.DEBUG("Could not reserve nick " + str(nick), "warn")
                    return False
                if jid == j and n:
                    self.DEBUG("The jid %s already has a nick registered" % (str(j)), "warn")
                    return False

        self.reserved_nicks[jid] = nick
        self.DEBUG("Reserved nick %s for %s" % (str(nick), jid), "ok")
        return True

    def processRegistration(self, x, frm, stanza, session):
        """
        Process the registration form (to a room) of a user
        """
        try:
            self.DEBUG("Process Registration", "info")
            form = DataForm(node=x)
            self.DEBUG("DataForm parsed", "info")
        except:
            self.DEBUG("ERROR PARSING", "error")
            # We must send a "bad-request" error
            reply = stanza.buildReply(typ="error")
            err = Node('error', {'code': '400', 'type': 'modify'})
            err.setTag("bad-request", {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
            reply.addChild(node=err)
            session.enqueue(reply)
            return

        nick = None
        for field in form.getTags("field"):
            try:
                var = field.getVar()
                values = field.getValues()
                # Switch var
                if var == "muc#register_first":
                    self.DEBUG("First Name is %s" % (values[0]), "info")
                elif var == "muc#register_last":
                    self.DEBUG("Last Name is %s" % (values[0]), "info")
                elif var == "muc#register_roomnick":
                    nick = values[0]
                    self.DEBUG("Desired Nickname is %s" % (nick), "info")
                    if nick in self.reserved_nicks.values() and nick:
                        # Nick conflict
                        reply = stanza.buildReply(typ="error")
                        err = Node('error', {'code': '409', 'type': 'cancel'})
                        err.setTag("conflict", {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                        reply.addChild(node=err)
                        session.enqueue(reply)
                        return
                    else:
                        self.reserved_nicks[JID(frm).getStripped()] = nick
                elif var == "muc#register_url":
                    if values:
                        self.DEBUG("URL is %s" % (values[0]), "info")
                elif var == "muc#register_email":
                    if values:
                        self.DEBUG("Email is %s" % (values[0]), "info")
                elif var == "muc#register_faqentry":
                    if values:
                        self.DEBUG("Faq is %s" % (str(values)), "info")

            except:
                self.DEBUG("Registration of user %s in room %s failed" % (frm, self.getName()), "error")
                # We must send a "bad-request" error
                reply = stanza.buildReply(typ="error")
                err = Node('error', {'code': '400', 'type': 'modify'})
                err.setTag("bad-request", {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                reply.addChild(node=err)
                session.enqueue(reply)
                return

        self.DEBUG("Client %s successfully registered in room %s" % (frm, self.getName()), "ok")
        # Grant membership to this user and tell everyone he's now a member (if he's in the room)
        to = None
        for k, p in self.participants.items():
            if k == frm:
                to = p
                break

        if to:
            to.setAffiliation("member")
            #to.setRole('participant')
        else:
            to = Participant(fulljid=frm, nick=nick, role="none", affiliation="member")

        jid = to.getBareJID()
        if jid not in self.whitelist:
            self.whitelist.append(jid)
        if jid in self.blacklist:
            self.blacklist.remove(jid)
        if jid in self.visitors:
            self.visitors.remove(jid)

        # inform new member of his approved membership
        reply = stanza.buildReply(typ="result")
        session.enqueue(reply)

        #service informs remaining occupants
        #if jid in self.participants.keys():
        for p in self.participants.values():
            if p.getBareJID() == jid:
                relative_frm = self.fullJID() + '/' + to.getNick()
                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                newitem = Node('item', {'affiliation': to.getAffiliation()})
                newitem.setAttr('role', to.getRole())
                newitem.setAttr('nick', to.getNick())
                if self.getWhois() == "anyone" \
                        or self.getWhois() == "moderators" and other.getRole() == "moderator":
                    newitem.setAttr('jid', jid)
                x.addChild(node=newitem)

                for other in self.participants.values():
                    reply = Presence(other.getFullJID(), frm=relative_frm)
                    reply.addChild(node=x)
                    s = self.muc.server.getsession(other.getFullJID())
                    if s:
                        s.enqueue(reply)
                return

        self.muc.saveRoomDB()

    def configRoom(self, x):
        """
        Configurate a room given a dataform with the desired configuration
        """
        form = DataForm(node=x)
        self.DEBUG("DataForm parsed", "info")
        for field in form.getTags("field"):
            try:
                var = field.getVar()
                values = field.getValues()
                # Switch var
                if var == "muc#roomconfig_maxusers":
                    try:
                        self.setMaxUsers(values[0])
                    except:
                        pass
                if var == "muc#roomconfig_minusers":
                    try:
                        self.setMinUsers(values[0])
                    except:
                        pass
                elif var == "muc#roomconfig_presencebroadcast":
                    self.config[var] = []
                    for val in values:
                        if val in ["moderator", "participant", "visitor"]:
                            self.config[var].append(val)
                elif var == "muc#roomconfig_whois":
                    if values[0] in ["moderators", "anyone", ""]:
                        self.config[var] = str(values[0])
                elif var == "muc#roomconfig_roomadmins":
                    old_admin_list = copy.copy(self.config[var])
                    #self.config[var] = []
                    for val in values:
                        #self.config[var].append(val)
                        self.addRoomAdmin(val)
                    # We have to check if some admins have been deleted from the
                    # old list in order to notify it to the clients
                    for adm in old_admin_list:
                        if adm not in values:
                            # Deleted admin
                            self.delRoomAdmin(adm)
                elif var == "muc#roomconfig_roomowners":
                    self.config[var] = []
                    for val in values:
                        self.config[var].append(val)
                elif var == "muc#roomconfig_membersonly":
                    self.setMembersOnly(values[0])
                elif var == "muc#roomconfig_moderatedroom":
                    self.setModeratedRoom(values[0])
                elif var in ["muc#roomconfig_passwordprotectedroom", "muc#roomconfig_nicklockdown", "muc#roomconfig_allowregister",
                             "muc#roomconfig_persistentroom", "muc#roomconfig_publicroom", "muc#roomconfig_allowinvites",
                             "muc#roomconfig_changesubject", "muc#roomconfig_enablelogging"]:
                    if values[0] in [0, '0', False]:
                        self.config[var] = 0
                    elif values[0] in [1, '1', True]:
                        self.config[var] = 1
                elif var in ["muc#roomconfig_roomname", "muc#roomconfig_roomdesc", "muc#roomconfig_lang", "muc#roomconfig_roomsecret"]:
                    self.config[var] = str(values[0])

            except:
                self.DEBUG("Configuration of room %s failed" % (self.getName()), "error")

        self.DEBUG("Room %s successfully configured" % (self.getName()), "ok")
        self.muc.saveRoomDB()

    def addParticipant(self, nick, fulljid, password=None):
        """
        Add a participant to a room
        """
        self.DEBUG("addParticipant called with: " + str(fulljid) + " " + str(nick), 'info')

        # Check max users in this room
        if self.getMaxUsers() > 0 and len(self.participants) == self.getMaxUsers() and \
            JID(fulljid).getStripped() not in self.getRoomOwners() and \
                JID(fulljid).getStripped() not in self.getRoomAdmins():
            raise MaxUsers

        # fulljid must be a string
        if isinstance(fulljid, JID):
            fulljid = str(fulljid)

        if fulljid not in self.participants.keys():
            # Instantiate a new participant
            p = Participant(fulljid)
        else:
            # Modify an existing participant
            p = self.participants[fulljid]

        # Now, override the new participant's attributes
        p.setNick(nick)

        # Set the role
        if p.getBareJID() in self.moderators:
            p.setRole("moderator")
        elif p.getBareJID() in self.visitors and self.isModeratedRoom():
            p.setRole("visitor")
        else:
            p.setRole("participant")

        # Set the affiliation
        if p.getBareJID() in self.getRoomOwners():
            p.setAffiliation("owner")
        elif p.getBareJID() in self.getRoomAdmins():
            p.setAffiliation("admin")
        elif p.getBareJID() in self.whitelist:
            p.setAffiliation("member")
        elif p.getBareJID() in self.blacklist:
            p.setAffiliation("outcast")
        else:
            p.setAffiliation("none")

        # See wether the participant can be added to the room depending on the room's type
        # Case 0: The participant is blacklisted
        if p.getBareJID() in self.blacklist:
            # "I told you not to come back! Get the f**k out of here!"
            raise Blacklisted
        # Case 1: Open and without password. Free way
        #if self.open and self.unsecured:
        if not self.isMembersOnly() and not self.isPasswordProtectedRoom():
            # Set the participants role based on the room's moderation and the 'role' parameter provided
            self.participants[p.getFullJID()] = p
            self.DEBUG("Participant " + str(p.getFullJID()) + " has been granted the role of " + str(p.getRole()) + " at room " + self.getName(), 'info')
            return True
        # Case 2: Open but with password. "Say say say say the password"
        #elif self.open and not self.unsecured:
        elif not self.isMembersOnly() and self.isPasswordProtectedRoom():
            if password == self.getPassword():
                # Free way
                # Set the participants role based on the room's moderation and the 'role' parameter provided
                self.participants[p.getFullJID()] = p
                return True
            else:
                # Wrong password
                raise BadPassword
        # Case 3: Members-only but without password
        elif self.isMembersOnly() and not self.isPasswordProtectedRoom():
            #print "LA WHITELIST DE "+str(self.getName())+ " ES: "+str(self.whitelist)
            if p.getBareJID() in self.whitelist or \
                p.getBareJID() in self.getRoomAdmins() or \
                    p.getBareJID() in self.getRoomOwners():
                # "Welcome back, sir"
                # Check and/or register the nick
                if p.getBareJID() in self.reserved_nicks.keys():
                    if not self.reserved_nicks[p.getBareJID()]:
                        self.reserveNick(p.getBareJID(), p.getNick())
                    else:
                        if self.isLockedDown():
                            if p.getNick() != self.reserved_nicks[p.getBareJID()]:
                                raise NickLockedDown
                else:
                    # Strange case
                    raise NotAMember
                # Set the participants role based on the room's moderation and the 'role' parameter provided
                self.participants[p.getFullJID()] = p
                return True
            else:
                # "You're not on my list. Get lost"
                raise NotAMember
        # Case 4: Members-only and with password
        elif self.isMembersOnly() and self.isPasswordProtectedRoom():
            self.DEBUG("Case 4: Members-only and with password", "info")
            if p.getBareJID() in self.whitelist or \
                p.getBareJID() in self.getRoomAdmins() or \
                    p.getBareJID() in self.getRoomOwners():
                if password == self.getPassword():
                    # Check and/or register the nick
                    if p.getBareJID() in self.reserved_nicks.keys():
                        if not self.reserved_nicks[p.getBareJID()]:
                            self.reserved_nicks[p.getBareJID()] = p.getNick()
                        else:
                            if self.isLockedDown():
                                if p.getNick() != self.reserved_nicks[p.getBareJID()]:
                                    raise NickLockedDown
                    else:
                        # Strange case
                        raise NotAMember
                    # Free way
                    # Set the participants role based on the room's moderation and the 'role' parameter provided
                    self.participants[p.getFullJID()] = p
                    return True
                else:
                    # Bad password
                    raise BadPassword
            else:
                # Not a member. Get lost
                raise NotAMember

    def deleteParticipant(self, fulljid):
        """
        Delete a participant from a room
        """
        try:
            barejid = JID(fulljid).getStripped()
            if barejid in self.visitors:
                self.visitors.remove(barejid)
            if barejid in self.moderators:
                self.moderators.remove(barejid)
            del self.participants[fulljid]
            self.DEBUG("Participant %s deleted from room %s" % (fulljid, self.getName()), "info")
        except:
            # Participant not really in room
            pass

    def setAffiliation(self, participant, affiliation):
        """
        Set the affiliation of a participant
        """
        # If 'participant' is a string
        if isinstance(participant, types.StringType):
            jid = participant
        # If its an instance of JID or Participant
        elif isinstance(participant, types.InstanceType):
            if isinstance(participant, JID):
                jid = str(participant)
            elif isinstance(participant, Participant):
                jid = participant.getFullJID()

        # Change affiliation in the participants dict
        try:
            self.participants[jid].setAffiliation(affiliation)
            if affiliation == "owner":
                #self.owners.append(jid)
                self.addRoomOwner(jid)
            if affiliation == "admin":
                self.addRoomAdmin(jid)

        except:
            self.DEBUG("No such participant " + str(jid), 'error')


class MUC(PlugIn):
    """
    The conference component. Composed of multiple rooms
    """
    NS = ''
    #def __init__(self, jid, name):

    def plugin(self, server):
        self.server = server
        try:
            self.jid = server.plugins['MUC']['jid']
            self.name = server.plugins['MUC']['name']
        except:
            self.DEBUG("Could not find MUC jid or name", "error")
            return

        self.rooms = dict()
        self.loadRoomDB()

        general = Room('general', self, 'General Discussion')
        self.addRoom(general)
        coffee = Room('coffee', self, 'Coffee Room')
        self.addRoom(coffee)
        spade_room = Room('spade', self, 'SPADE Agents')
        self.addRoom(spade_room)
        member_room = Room('restricted', self, 'Restricted Area', whitelist=['q1@thx1138.dsic.upv.es'])
        #member_room.open = False
        member_room.setMembersOnly(True)
        self.addRoom(member_room)
        #black_room = Room('black', self, 'Black Note', blacklist=['q3@thx1138.dsic.upv.es'])
        black_room = Room('black', self, 'Black Note')
        #black_room.moderated = True
        black_room.setModeratedRoom(True)
        black_room.moderators.append('q1@thx1138.dsic.upv.es')
        #black_room.moderators.append('q2@thx1138.dsic.upv.es')
        black_room.visitors.append('q3@thx1138.dsic.upv.es')
        #black_room.owners.append('q1@thx1138.dsic.upv.es')
        black_room.addRoomOwner('q1@thx1138.dsic.upv.es')

        #black_room.admins.append('q2@thx1138.dsic.upv.es')
        #black_room.blacklist.append('q2@thx1138.dsic.upv.es')
        black_room.whitelist.append('q1@thx1138.dsic.upv.es')

        black_room.moderators.append('q1@tatooine.dsic.upv.es')
        #black_room.moderators.append('q2@tatooine.dsic.upv.es')
        black_room.visitors.append('q3@tatooine.dsic.upv.es')
        black_room.addRoomOwner('q1@tatooine.dsic.upv.es')
        #black_room.admins.append('q2@tatooine.dsic.upv.es')
        #black_room.whitelist.append('q1@tatooine.dsic.upv.es')
        #black_room.whitelist.append('q2@tatooine.dsic.upv.es')
        #black_room.whitelist.append('q3@tatooine.dsic.upv.es')
        #black_room.blacklist.append('q2@tatooine.dsic.upv.es')
        black_room.setMembersOnly(True)

        #black_room.maxusers = 1
        #black_room.password = "secret"
        #black_room.unsecured = False
        self.addRoom(black_room)
        non = Room('non', self, 'Non-Anonima')
        #non.anonymous = "non"
        non.setWhois("anyone")
        self.addRoom(non)
        fully = Room('fully', self, 'Fully-Anonima')
        #fully.anonymous = "fully"
        fully.setWhois("")
        self.addRoom(fully)

        self.DEBUG("Created MUC: '%s' '%s'" % (self.name, str(self.jid)), "warn")

    def printMUC(self):
        """
        Show a textual representation of the conference
        """
        return str(self.jid) + ": " + str(self.rooms)

    def addRoom(self, room=None, name=None):
        """
        Add a room to the conference
        """
        if room:
            # Add the given room
            room.muc = self
            #self.rooms[str(room.name)] = room
            self.rooms[str(room.getName())] = room
            self.saveRoomDB()
            return True
        elif name:
            # Create a new (empty) default room with given jid
            self.rooms[str(name)] = Room(name, self)
            self.saveRoomDB()
            return True
        else:
            # Error: no room and no jid. Don't know what to do
            return False

    def destroyRoom(self, name, owner_session, stanza):
        """
        Destroy a room (for a reason). A venue (alternative new room) may be declared
        to take place of the destroyed room
        """
        if name in self.rooms:
            room = self.rooms[name]
        else:
            return

        # Get venue and reason
        try:
            venue = stanza.T.query.getAttr('jid')
        except:
            venue = None
        try:
            reason = stanza.T.query.T.destroy.T.reason
        except:
            reason = None

        if reason:
            self.DEBUG("Destroying the room %s because: %s" % (name, reason.getData()), "info")
        else:
            self.DEBUG("Destroying the room %s" % (name), "info")
        x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
        item = Node('item', {'role': 'none', 'affiliation': 'none'})
        destroy = Node('destroy')
        if venue:
            destroy.setAttr('jid', venue)
        if reason:
            rea = Node('reason')
            rea.setData(reason.getData())
            destroy.addChild(node=rea)
        x.addChild(node=item)
        x.addChild(node=destroy)
        for k, p in room.participants.items():
            # Send a final presence
            relative_frm = room.fullJID() + "/" + p.getNick()
            pres = Presence(to=k, frm=relative_frm, typ="unavailable")
            pres.addChild(node=x)
            s = None
            s = self.server.getsession(k)
            if s:
                s.enqueue(pres)

        # Notify the owner of the success in destroying the room
        iq = stanza.buildReply(typ="result")
        owner_session.enqueue(iq)

        # Destroy room instance
        del self.rooms[name]
        del room

        # Execute persistency
        self.saveRoomDB()

        return

    def dispatch(self, session, stanza):
        """
        Mini-dispatcher for the jabber stanzas that arrive to the Conference
        """
        self.DEBUG("MUC dispatcher called", "warn")
        try:
            to = stanza['to']
            room = to.getNode()
            domain = to.getDomain()
        except:
            self.DEBUG("There was no 'to'", 'warn')

        # No room name. Stanza directed to the Conference
        if room == '' and domain == str(self.jid):
            if stanza.getName() == 'iq':
                self.IQ_cb(session, stanza)
            elif stanza.getName() == 'presence':
                self.Presence_cb(session, stanza)
            # TODO: Implement the rest of protocols
        # Stanza directed to a specific room
        if room in self.rooms.keys() and domain == str(self.jid):
            self.rooms[room].dispatch(session, stanza)
        else:
            # The room does not exist
            self.notExist_cb(session, stanza)

    def Presence_cb(self, session, stanza):
        '''
        Callback for presence stanzas directed to the conference itself
        '''
        self.DEBUG("Presence callback of the MUC called")
        pass

    def notExist_cb(self, session, stanza):
        '''
        Callback called when a stanza is directed to a room that does not (yet) exist
        '''
        self.DEBUG("NotExist handler called", "info")

        to = stanza['to']
        room = to.getNode()
        domain = to.getDomain()
        nick = to.getResource()
        frm = str(session.peer)
        typ = stanza.getType()
        name = stanza.getName()

        if name == "presence":
            if typ == "available" or not typ:  # Available
                # Create the room and add the client as the owner
                p = Participant(frm, nick=nick, affiliation='owner')
                room_node = Room(room, self, creator=p)
                self.addRoom(room_node)
                # Reply the client with an OK 201 code
                relative_frm = room_node.fullJID() + '/' + nick
                pres = Presence(frm=relative_frm)
                x = Node('x', {'xmlns': 'http://jabber.org/protocol/muc#user'})
                item = Node('item', {'affiliation': p.getAffiliation(), 'role': p.getRole()})
                status = Node('status', {'code': '201'})
                x.addChild(node=item)
                x.addChild(node=status)
                pres.addChild(node=x)
                session.enqueue(pres)
                # Check wether the room must be locked
                for tag in stanza.getChildren():
                    if tag.getName() == 'x':
                        if tag.getNamespace() == "http://jabber.org/protocol/muc":
                            # MUC protocol
                            room_node.locked = True
                        else:
                            # Groupchat 1.0 protocol
                            room_node.locked = False
                # Redirect the stanza to the handler of the new room
                room_node.dispatch(session, stanza)
                return

        if name == "iq":
            if stanza.getQueryNS() == NS_REGISTER:
                # User requesting registration in a non-existent room or requesting the registration form.
                # Either way it's WRONG
                self.DEBUG("Room does not exist", "warn")
                reply = stanza.buildReply(typ="error")
                err = Node('error', {'code': '503', 'type': 'cancel'})
                err.setTag('service-unavailable', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                reply.addChild(node=err)
                session.enqueue(reply)
                return

    def IQ_cb(self, session, iq):
        """
        Manages IQ stanzas directed to the Conference itself
        """
        self.DEBUG("MUC Iq callback called", "warn")
        # Look for the query xml namespace
        query = iq.getTag('query')
        if query:
            try:
                ns = str(iq.getQueryNS())
                typ = str(iq.getType())
                # Discovery Info
                if ns == NS_DISCO_INFO and typ == 'get':
                    # Build reply
                    reply = Iq('result', NS_DISCO_INFO, to=iq.getFrom(), frm=str(self.jid))
                    rquery = reply.getTag('query')
                    id = iq.getAttr('id')
                    if id:
                        reply.setAttr('id', id)
                    identity = {'category': 'conference', 'type': 'text', 'name': self.name}
                    feature = {'var': 'http://jabber.org/protocol/muc'}
                    rquery.setTag('identity', identity)
                    rquery.setTag('feature', feature)
                    session.enqueue(reply)
                # Discovery Items, i.e., the rooms
                elif ns == NS_DISCO_ITEMS:
                    self.DEBUG("NS_DISCO_ITEMS requested", "warn")
                    # Build reply
                    reply = Iq('result', NS_DISCO_ITEMS, to=iq.getFrom(), frm=str(self.jid))
                    rquery = reply.getTag('query')
                    id = iq.getAttr('id')
                    if id:
                        reply.setAttr('id', id)
                    # For each room in the conference, generate an 'item' element with info about the room
                    for room, v in self.rooms.items():
                        #if not v.hidden and not v.locked:
                        if v.isPublicRoom() and not v.locked:
                            #attrs = { 'jid': str(room+'@'+self.jid), 'name': str(v.subject) }
                            attrs = {'jid': str(room + '@' + self.jid), 'name': str(v.getName())}
                            rquery.setTag('item', attrs)
                    session.enqueue(reply)
                    self.DEBUG("NS_DISCO_ITEMS sent", "warn")

            except:
                self.DEBUG("No xmlns, don't know what to do", 'warn')

    def loadRoomDB(self):
        """
        Load persistent rooms and their configurations to the database
        """
        try:
            fh = open("roomdb.xml", 'r')
            roomdb = pickle.load(fh)
            fh.close()
            for r in roomdb.values():
                v = Room(name=r.name, subject=r.subject, muc=self, creator=r.creator, whitelist=copy.copy(r.whitelist), blacklist=copy.copy(r.blacklist))
                v.config = r.config
                v.locked = r.locked
                v.role_privileges = r.role_privileges
                self.rooms[v.getName()] = v
            self.DEBUG("Room Database Loaded", "info")
        except:
            self.DEBUG("Could not load Room Database", "error")

        return

    def saveRoomDB(self):
        """
        Save persistent rooms and their configurations to a static database
        """
        try:
            roomdb = dict()
            for k, v in self.rooms.items():
                if v.isPersistentRoom():
                    # Make a serializable object out of the room
                    r = SerializableRoom(v)
                    roomdb[k] = r

            fh = open("roomdb.xml", 'w')
            #pickle.dump(roomdb, fh, -1)
            pickle.dump(roomdb, fh)
            fh.close()
            self.DEBUG('Room database saved', 'info')
        except:
            self.DEBUG("Could not save room database", "error")

        return


# Debug main code
if __name__ == "__main__":
    conf = Conference("muc.localhost")
    p1 = Participant('p1@localhost/res', nick="PlayerOne")
    p2 = Participant('p2@localhost/Gaim', nick="PlayerTwo")
    r1 = Room('house@muc.localhost', conf, "My House", creator=p1)
    r2 = Room('auction@muc.localhost', conf, "Auction House", creator=p2)
    #r1.addParticipant(participant=p2)

    conf.addRoom(r1)
    conf.addRoom(r2)

    print p1
    print p2
    print r1
    print conf
