# -*- coding: utf-8 -*-
from xmpp import *

import cPickle as marshal
import cPickle as unmarshal
import copy
import threading

mutex = threading.RLock()

class DictWatch(dict):
    def __init__(self, *args):
        dict.__init__(self, args)

    def __getitem__(self, key):
        with mutex:
            val = dict.__getitem__(self, key)
        return val

    def __setitem__(self, key, val):
        with mutex:
            dict.__setitem__(self, key, val)

db = DictWatch()

def build_database(server_instance):
    global db
    for a_registered_server in server_instance.servernames:
        server_instance.DEBUG('server', 'DB: Building database tree for %s' % a_registered_server, 'info')
        if a_registered_server not in db.keys():
            db[a_registered_server] = DictWatch()

        db[a_registered_server]['__ir__'] = {}
        db[a_registered_server]['__ir__']['storage'] = {'karma': {'down': 307200, 'up': 307200307200307200, 'last_time': 0.0, 'tot_down': 0, 'tot_up': 0}}
        db[a_registered_server]['__ir__']['password'] = 'test'
        db[a_registered_server]['__ir__']['anon_allow'] = 'yes'
        db[a_registered_server]['__ir__']['roster'] = {}
        db[a_registered_server]['__ir__']['groups'] = {}

        """
        db[a_registered_server]['t'] = {}
        db[a_registered_server]['t']['password'] = 'thx1138.dsic.upv.es'
        db[a_registered_server]['t']['anon_allow'] = 'yes'
        db[a_registered_server]['t']['roster'] = {}
        #db[a_registered_server]['t']['roster']['t2@thx1138.dsic.upv.es'] = {'subscription':'both'}
        db[a_registered_server]['t']['groups'] = {}
        db[a_registered_server]['t2'] = {}
        db[a_registered_server]['t2']['password'] = 'thx1138.dsic.upv.es'
        db[a_registered_server]['t2']['anon_allow'] = 'yes'
        db[a_registered_server]['t2']['roster'] = {}
        #db[a_registered_server]['t2']['roster']['t@thx1138.dsic.upv.es'] = {'subscription':'both'}
        db[a_registered_server]['t2']['groups'] = {}

        db[a_registered_server]['t3'] = {}
        db[a_registered_server]['t3']['password'] = 't3'
        db[a_registered_server]['t3']['anon_allow'] = 'yes'
        db[a_registered_server]['t3']['roster'] = {}
        db[a_registered_server]['t3']['groups'] = {}
        db[a_registered_server]['t3']['name'] = "T3"

        db[a_registered_server]['t4'] = {}
        db[a_registered_server]['t4']['password'] = 't4'
        db[a_registered_server]['t4']['anon_allow'] = 'yes'
        db[a_registered_server]['t4']['roster'] = {}
        db[a_registered_server]['t4']['groups'] = {}
        db[a_registered_server]['t4']['name'] = "T4"


        db[a_registered_server]['test'] = {}
        db[a_registered_server]['test']['storage'] = {'karma':{'down':307200,'up':307200307200307200,'last_time':0.0,'tot_down':0,'tot_up':0}}
        db[a_registered_server]['test']['password'] = 'test'
        #Anon_allow tells the privacy subsystem if it's okay for someone to contact you
        #without any subscription at all.
        db[a_registered_server]['test']['anon_allow'] = 'no'
        db[a_registered_server]['test']['roster'] = {}
        #    {'jid':'test2@172.16.1.34','name':'Test Account 2','subscription':'both'},
        #    {'jid':'test3@172.16.1.34','subscription':'both'}]
        db[a_registered_server]['test']['groups'] = {}
        db[a_registered_server]['test']['groups']['Friends'] = ['test2@172.16.1.34','test3@172.16.1.34']

        db[a_registered_server]['test2'] = {}
        db[a_registered_server]['test2']['storage'] = {'karma':{'down':307200,'up':307200,'last_time':0.0,'tot_down':0,'tot_up':0}}
        db[a_registered_server]['test2']['password'] = 'test'
        db[a_registered_server]['test2']['anon_allow'] = 'yes'

        db[a_registered_server]['test2']['roster'] = {}
        db[a_registered_server]['test2']['roster']['test3@'+a_registered_server] = {'subscription':'both'}

        db[a_registered_server]['test2']['groups'] = {}
        db[a_registered_server]['test2']['groups']['Friends'] = ['test3@172.16.1.34','test3@172.16.0.2','test3@'+a_registered_server]

        db[a_registered_server]['test3'] = {}
        db[a_registered_server]['test3']['storage'] = {'karma':{'down':307200,'up':307200,'last_time':0.0,'tot_down':0,'tot_up':0}}
        db[a_registered_server]['test3']['password'] = 'test'
        db[a_registered_server]['test3']['anon_allow'] = 'yes'
        db[a_registered_server]['test3']['name'] = 'テスト・アカウント#3'
        #Roster Info
        ##Roster Items
        db[a_registered_server]['test3']['roster'] = {}
        db[a_registered_server]['test3']['roster']['test2@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['test3']['roster']['pixelcort@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['test3']['roster']['kris_tate@'+a_registered_server] = {'subscription':'both'}

        ##Item Groups
        db[a_registered_server]['test3']['groups'] = {}
        db[a_registered_server]['test3']['groups']['かっこういいな人'] = ['test2@172.16.1.34','test2@172.16.0.2','test2@'+a_registered_server,'pixelcort@'+a_registered_server,'kris_tate@'+a_registered_server]

        db[a_registered_server]['pixelcort'] = {}
        db[a_registered_server]['pixelcort']['storage'] = {'karma':{'down':307200,'up':307200,'last_time':0.0,'tot_down':0,'tot_up':0}}
        db[a_registered_server]['pixelcort']['password'] = 'test'
        db[a_registered_server]['pixelcort']['anon_allow'] = 'yes'
        db[a_registered_server]['pixelcort']['name'] = 'Cortland Klein'
        #Roster Info
        ##Roster Items
        db[a_registered_server]['pixelcort']['roster'] = {}
        db[a_registered_server]['pixelcort']['roster']['tekcor@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['pixelcort']['roster']['kris_tate@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['pixelcort']['roster']['mvanveen@'+a_registered_server] = {'subscription':'both'}

        ##Item Groups
        db[a_registered_server]['pixelcort']['groups'] = {}
        db[a_registered_server]['pixelcort']['groups']['Friends'] = ['tekcor@'+a_registered_server,'mvanveen@'+a_registered_server]
        db[a_registered_server]['pixelcort']['groups']['Kris'] = ['kris_tate@'+a_registered_server]

        db[a_registered_server]['kris_tate'] = {}
        db[a_registered_server]['kris_tate']['storage'] = {'karma':{'down':307200,'up':1000,'last_time':0.0,'tot_down':0,'tot_up':0}}
        db[a_registered_server]['kris_tate']['password'] = 'test'
        db[a_registered_server]['kris_tate']['anon_allow'] = 'yes'
        db[a_registered_server]['kris_tate']['name'] = 'Kristopher Tate'
        #Roster Info
        ##Roster Items
        db[a_registered_server]['kris_tate']['roster'] = {}
        db[a_registered_server]['kris_tate']['roster']['tekcor@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['kris_tate']['roster']['pixelcort@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['kris_tate']['roster']['mvanveen@'+a_registered_server] = {'subscription':'both'}

        ##Item Groups
        db[a_registered_server]['kris_tate']['groups'] = {}
        db[a_registered_server]['kris_tate']['groups']['かっこういいな人'] = ['tekcor@'+a_registered_server,'pixelcort@'+a_registered_server,'mvanveen@'+a_registered_server]

        db[a_registered_server]['tekcor'] = {}
        db[a_registered_server]['tekcor']['storage'] = {'karma':{'down':307200,'up':307200,'last_time':0.0,'tot_down':0,'tot_up':0}}
        db[a_registered_server]['tekcor']['password'] = 'test'
        db[a_registered_server]['tekcor']['anon_allow'] = 'yes'
        db[a_registered_server]['tekcor']['name'] = 'Thom McGrath'
        #Roster Info
        ##Roster Items
        db[a_registered_server]['tekcor']['roster'] = {}
        db[a_registered_server]['tekcor']['roster']['pixelcort@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['tekcor']['roster']['kris_tate@'+a_registered_server] = {'subscription':'both'}

        ##Item Groups
        db[a_registered_server]['tekcor']['groups'] = {}
        db[a_registered_server]['tekcor']['groups']['Friends'] = ['kris_tate@'+a_registered_server,'pixelcort@'+a_registered_server]


        db[a_registered_server]['mvanveen'] = {}
        db[a_registered_server]['mvanveen']['storage'] = {'karma':{'down':307200,'up':307200,'last_time':0.0,'tot_down':0,'tot_up':0}}
        db[a_registered_server]['mvanveen']['password'] = 'test'
        db[a_registered_server]['mvanveen']['anon_allow'] = 'yes'
        db[a_registered_server]['mvanveen']['name'] = 'Mike Van Veen'
        #Roster Info
        ##Roster Items
        db[a_registered_server]['mvanveen']['roster'] = {}
        db[a_registered_server]['mvanveen']['roster']['pixelcort@'+a_registered_server] = {'subscription':'both'}
        db[a_registered_server]['mvanveen']['roster']['kris_tate@'+a_registered_server] = {'subscription':'both'}

        ##Item Groups
        db[a_registered_server]['mvanveen']['groups'] = {}
        db[a_registered_server]['mvanveen']['groups']['Friends'] = ['kris_tate@'+a_registered_server,'pixelcort@'+a_registered_server]
        """
        #for guy in db[a_registered_server].keys():
        #    db[a_registered_server][guy]['roster'][a_registered_server] = {'subscription':'to','name':"Help Desk"}


class AUTH(PlugIn):
    NS = ''

    def getpassword(self, node, domain):
        try:
            return db[domain][node]['password']
        except KeyError:
            pass

    def isuser(self, node, domain):
        try:
            if node in db[str(domain)].keys():
                return True
        except:
            pass

        if str(domain) in self._owner.components.keys():
            return True
        return False


class DB(PlugIn):
    NS = ''

    def plugin(self, server):
        self.DEBUG('Building Database tree!', 'info')
        self.load_database()
        build_database(server)  # Building database!

    def store(self, domain, node, stanza, id='next_unique_id'):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            self.DEBUG("Storing to database:\n%s:%s::%s:%s" % (domain, node, id, stanza), 'info')
            db[domain][node]['storage'][id] = stanza
            self.save_database()
            return True
        except KeyError:
            self.DEBUG("Could not store in database:\n%s:%s::%s:%s" % (domain, node, id, stanza), 'error')
            return False

    def get_store(self, domain, node, id):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            return db[domain][node]['storage'][id]
        except KeyError:
            return False

    def get_storage(self, domain, node):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            l = copy.copy(db[domain][node]['storage'].values())
            db[domain][node]['storage'].clear()
            return l
        except KeyError:
            return []
        except:
            return []

    def save(self, domain, node, stanza, id='next_unique_id'):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            self.DEBUG("Saving to database:\n%s:%s::%s:%s" % (domain, node, id, stanza), 'info')
            db[domain][node][id] = stanza
            self.save_database()
            return True
        except KeyError:
            self.DEBUG("DB ERR: Could not save to database:\n%s:%s::%s:%s" % (domain, node, id, stanza), 'warn')
            return False

    def save_to_roster(self, domain, node, jid, info, add_only_if_already=False):
        if not node:
            node, domain = domain.split(".", 1)
        self.DEBUG("Saving roster info to database %s-->(%s) [%s]:\n" % (jid, node + '@' + domain, str(info)), 'info')
        if jid in db[domain][node]['roster'].keys() and add_only_if_already is False:
            db[domain][node]['roster'][jid].update(info)
        else:
            db[domain][node]['roster'][jid] = info
        self.save_database()

    def pull_roster(self, domain, node, jid):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            data = db[domain][node]['roster'][jid]
            if 'subscription' not in data.keys():
                data.update({'subscription': 'none'})
            return data
        except KeyError:
            self.DEBUG('DB ERR: Could not retrieve %s@%s roster for %s' % (node, domain, jid), 'warn')
            return None

    def del_from_roster(self, domain, node, jid):
        if not node:
            node, domain = domain.split(".", 1)
        self.DEBUG("Deleting roster info from database %s--X(%s):\n" % (jid, node + '@' + domain), 'info')
        try:
            del(db[domain][node]['roster'][jid])
            self.save_database()
            return True
        except KeyError, err:
            self.DEBUG('DB ERR: A Client tried to remove a contact that wasn\'t even added! (%s::%s::%s)' % (domain, node, jid), 'warn')
            return False

    def del_from_roster_jid(self, domain, node, jid, what):
        if not node:
            node, domain = domain.split(".", 1)
        self.DEBUG("Deleting roster info from database %s--X(%s):\n" % (jid, node + '@' + domain), 'info')
        try:
            del(db[domain][node]['roster'][jid][what])
            self.save_database()
            return True
        except KeyError, err:
            self.DEBUG('DB ERR: A Client tried to remove a contact attr that wasn\'t even added! (%s::%s::%s)' % (domain, node, jid), 'warn')
            return False

    def save_groupie(self, domain, node, jid, groups):
        if not node:
            node, domain = domain.split(".", 1)
        temp = [x for x in groups]
        group_list = temp #[0] # will crash if empty!
        self.DEBUG("Saving groupie jid to database %s-->(%s) [%s]:\n" % (jid, node + '@' + domain, unicode(groups).encode('utf-8')), 'info')
        if db[domain][node]['groups'] == DictWatch():
            for gn in group_list:
                db[domain][node]['groups'][gn] = [jid]
        '''for gn, gm in db[domain][node]['groups'].items():
            if gn not in group_list and jid in db[domain][node]['groups'][gn]:
                db[domain][node]['groups'][gn].remove(jid)
            elif gn in group_list and jid not in db[domain][node]['groups'][gn]:
                db[domain][node]['groups'][gn] += [jid]
        '''
        for gn in group_list:
            if gn not in db[domain][node]['groups'].keys():
                db[domain][node]['groups'][gn] = [jid]
            else:
                if jid not in db[domain][node]['groups'][gn]:
                    db[domain][node]['groups'][gn] += [jid]
        for gn,gm in db[domain][node]['groups'].items():
            if (gn not in group_list) and (jid in gm):
                db[domain][node]['groups'][gn].remove(jid)

        self.DEBUG("Saved groupie jid to database %s-->(%s) [%s]:\n" % (jid, db[domain][node], unicode(groups).encode('utf-8')), 'info')
        self.save_database()

    def del_groupie(self, domain, node, jid):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            self.DEBUG("Deleting groupie from database %s--X(%s):\n" % (jid, node + '@' + domain), 'info')
            for gn, gm in db[domain][node]['groups'].iteritems():
                if jid in db[domain][node]['groups'][gn]:
                    db[domain][node]['groups'][gn].remove(jid)
        except Exception, err:
            self.DEBUG('DB ERR: A groupie went mad! %s::%s::%s' % (domain, node, jid), 'warn')
        self.save_database()

    def get(self, domain, node, what):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            return db[domain][node][what]
        except KeyError:
            self.DEBUG('DB ERR: Could not retrieve %s::%s::%s' % (domain, node, what), 'warn')
            return None

    def delete(self, domain, node, what):
        if not node:
            node, domain = domain.split(".", 1)
        try:
            del(db[domain][node][what])
            self.save_database()
            return True
        except KeyError:
            self.DEBUG('DB ERR: Could not delete %s::%s::%s' % (domain, node, what), 'warn')
            return None

    def getNumRegistered(self, server):
        return len(db[server].keys())

    def register_user(self, domain, node, password, name):
        try:
            db[domain][node] = DictWatch()
            db[domain][node]['password'] = password
            db[domain][node]['roster'] = DictWatch()
            db[domain][node]['storage'] =DictWatch()
            db[domain][node]['groups'] = DictWatch()
            db[domain][node]['name'] = name
            db[domain][node]['anon_allow'] = 'yes'
            db[domain][node]['roster'] = DictWatch()
            #db[domain][node]['roster'][domain] = {'subscription':'to','name':"Help Desk"}
            self.DEBUG("Registered user %s in domain %s" % (node, domain), 'info')
            self.save_database()
            return True
        except:
            self.DEBUG('Error registering username %s in domain %s' % (node, domain), 'error')
            return False

    def save_database(self, filename="user_db.xml"):
        try:
            global db
            #print "#### userdbfile = " + str(self.userdbfile)
            #print "#### spoolpath = " + str(self.spoolpath)
            """
                if not os.path.exists(self.spoolpath):
                        self.DEBUG("spoolpath does no exist.", 'warn')
                        p = self.spoolpath.split(os.sep)
                        tmpitem=''
                        for item in p:
                                tmpitem+=os.sep+str(item)
                                if not os.path.exists(tmpitem):
                                        self.DEBUG("mkdir " + str(tmpitem), 'info')
                                        os.mkdir(tmpitem)
            """
            fh = open(filename, 'w')
            with mutex:
                marshal.dump(db, fh)
            fh.close()
            self.DEBUG('save_database: User database saved!', 'info')
            return True
        except:
            self.DEBUG('save_database: Could not save user database', 'error')
            return False

    def load_database(self, filename="user_db.xml"):
        """
        Loads an entire database from disk
        """
        try:
            global db
            fh = open(filename, 'r')
            with mutex:
                db = unmarshal.load(fh)
            fh.close()
            self.DEBUG('load_database: User database loaded', 'info')
            return True
        except:
            self.DEBUG('load_database: Could not load user database', 'error')
            return False

    def __str__(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        with mutex:
            return pp.pformat(db)

    @property
    def db(self):
        return db

    def print_database(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        with mutex:
            pp.pprint(db)
