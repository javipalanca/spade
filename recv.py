#!/usr/bin/env python

# $Id: recv.py,v 1.1 2004/02/06 20:48:49 jpalanca Exp $

# You may need to change the above line to point at
# python rather than python2 depending on your os/distro

import socket
from select import select
from string import split,strip,join,find
import sys,os
import smtplib
import telnetlib
import pprint
pp = pprint.PrettyPrinter(indent=4)

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import jabber

True = 1
False = 0

# Change this to 0 if you dont want a color xterm
USE_COLOR = 1

Who = ''
MyStatus = ''
MyShow   = ''

def XMLdecode(body):
	
    tag = getTag(body)
    if tag == "REQUEST":
        print "He recibido un REQUEST"
        
    return
def tellIQ(fromwho, agent, con, me):
	if fromwho != '':
            i = jabber.Iq(agent)
	    i.setType('set')
	    i.setFrom(me)
	    i.setID("search2")
	    i.setQuery("jabber:iq:search")
	    i.setQueryPayload("<last>Agent</last>")
	    pp.pprint(i)
            con.send(i)
	    '''
	    i.setType('set')
	    i.setFrom(me)
	    i.setID('register2')
	    i.setQuery("jabber:iq:register")
	    i.setQueryPayload("<query><first>PROVEMAN</first><last>FipperAgent</last><nick>AGENTONE</nick><email>a1@fipper.org</email></query>")
	    pp.pprint(i)
	    con.send(i)
	    '''
	return
	
def tellFortune(fromwho):
	os.system("fortune > out.txt")
	fsock = open('out.txt', 'r')
	s = fsock.read()
	fromwho = "/select "+str(fromwho)
	doCmd(con,fromwho)
	doCmd(con, s)
	fsock.close()
	os.system("rm out.txt")
	return

def tellGoogle(fromwho, what):
	that = 'links -dump "http://www.google.es/search?q='+what+'" > out-gg.txt'
	print that
	os.system(that)
	fsock = open('out-gg.txt', 'r')
	s = fsock.read()
	fromwho = "/select "+str(fromwho)
	doCmd(con,fromwho)
	doCmd(con, s)
	fsock.close()
	os.system("rm out-gg.txt")
	return
	
def tellWikipedia(fromwho, what):
	that = 'links -dump "http://en.wikipedia.org/w/wiki.phtml?search='+what+'&go=Go" > out-wp.txt'
	print that
	os.system(that)
	fsock = open('out-wp.txt', 'r')
	s = fsock.read()
	fromwho = "/select "+str(fromwho)
	doCmd(con,fromwho)
	doCmd(con, s)
	fsock.close()
	os.system("rm out-wp.txt")
	return
	
def tellMLD(fromwho):
	tn = telnetlib.Telnet("192.168.1.2", "4000")
	#~ tn.read_until(">")
	tn.write("ansi false\n")
	tn.write("vd\n")
	tn.write("q\n")
	thing = tn.read_until("blobloblo",2) # Dirty hack from hell
	i = thing.find("Downloaded")
	j = thing.rfind("Downloaded")
	thing = thing[i:j]
	fromwho = "/select "+str(fromwho)
	doCmd(con,fromwho)
	doCmd(con,str(thing))
	return
	
def tellMail(fromwho, maildata):
	md = split(maildata, sep=';;')
	print md
	if len(md) != 3:
		fromwho = "/select "+str(fromwho)
		doCmd(con,fromwho)
		doCmd(con,"MAIL SYNTAX ERROR")
	else:
		fw = fromwho
		server = smtplib.SMTP('maulo.ma.cx')
		msg = "Subject: "+str(md[1])+"\n"+str(md[2])
		i = find(str(fromwho),"/")
		fromwho = str(fromwho)[0:i]
		server.sendmail(str(fromwho), md[0], msg)
		server.quit()
		fw = "/select "+str(fw)
		doCmd(con,fw)
		doCmd(con,"Gracias por usar nuestro servicio de correo.\nPor favor, recuerde no abusar de ello.")
	return

def usage():
    print "%s: a simple python jabber client " % sys.argv[0]
    print "usage:"
    print "%s <server> - connect to <server> and register" % sys.argv[0]
    print "%s server> <username> <password> <resource>"    % sys.argv[0]
    print "            - connect to server and login   "
    sys.exit(0)


def doCmd(con,txt):
    global Who
    if txt[0] == '/' :
        cmd = split(txt)
        if cmd[0] == '/select':
            Who = cmd[1]
            print "%s selected" % cmd[1]
        elif cmd[0] == '/presence':
            to = cmd[1]
            type = cmd[2]
            con.send(jabber.Presence(to, type))
        elif cmd[0] == '/status':
            p = jabber.Presence()
            MyStatus = ' '.join(cmd[1:])
            p.setStatus(MyStatus)
            con.send(p)
        elif cmd[0] == '/show':
            p = jabber.Presence()
            MyShow = ' '.join(cmd[1:])
            p.setShow(MyShow)
            con.send(p)
        elif cmd[0] == '/subscribe':
            to = cmd[1]
            con.send(jabber.Presence(to, 'subscribe'))
        elif cmd[0] == '/unsubscribe':
            to = cmd[1]
            con.send(jabber.Presence(to, 'unsubscribe'))
        elif cmd[0] == '/roster':
            con.requestRoster()
            _roster = con.getRoster()
            for jid in _roster.getJIDs():
                print colorize("%s :: %s (%s/%s)" 
                               % ( jid, _roster.getOnline(jid),
                                   _roster.getStatus(jid),
                                   _roster.getShow(jid),
                                   ) , 'blue' )

        elif cmd[0] == '/agents':
            print con.requestAgents()
        elif cmd[0] == '/register':
            agent = ''
            if len(cmd) > 1:
                agent = cmd[1]
            con.requestRegInfo(agent)
            print con.getRegInfo()
	elif cmd[0] == "/iq":
	    tellIQ(JID, cmd[1], con, JID)
        elif cmd[0] == '/exit':
            con.disconnect()
            print colorize("Bye!",'red')
            sys.exit(0)
        elif cmd[0] == '/help':
            print "commands are:"
            print "   /select <jabberid>"
            print "      - selects who to send messages to"
            print "   /subscribe <jid>"
            print "      - subscribe to jid's presence"
            print "   /unsubscribe <jid>"
            print "      - unsubscribe to jid's presence"
            print "   /presence <jabberid> <type>"
            print "      - sends a presence of <type> type to the jabber id"
            print "   /status <status>"
            print "      - set your presence status message"
            print "   /show <status>"
            print "      - set your presence show message"
            print "   /roster"
            print "      - requests roster from the server and "
            print "        display a basic dump of it."
            print "   /exit"
            print "      - exit cleanly"
        else:
            print colorize("uh?", 'red')
    else:
        if Who != '':
            msg = jabber.Message(Who, strip(txt))
            msg.setType('chat')
            print "<%s> %s" % (JID, msg.getBody())
            con.send(msg)
        else:
            print colorize('Nobody selected','red')
            

def messageCB(con, msg):
    """Called when a message is recieved"""
    if msg.getBody(): ## Dont show blank messages ##
        print colorize(
            '<' + str(msg.getFrom()) + '>', 'green'
            ) + ' ' + msg.getBody()
    
    #~ XMLdecode(msg.getBody())
    
    cuerpo = msg.getBody()
    if cuerpo == "CAPTAIN":
        doCmd(con,"WHAT_HAPPEN")
    elif cuerpo == "WHAT_HAPPEN":
	doCmd(con,"WE_GET_SIGNAL")
    elif cuerpo == "WE_GET_SIGNAL":
	doCmd(con,"MAIN_SCREEN_TURN_ON")
    elif cuerpo == "MAIN_SCREEN_TURN_ON":
	doCmd(con,"ITS_YOU")
    elif cuerpo == "ITS_YOU":
	doCmd(con,"HOW_ARE_YOU_GENTLEMEN")
    elif cuerpo == "HOW_ARE_YOU_GENTLEMEN":
	doCmd(con,"ALL_YOUR_BASE_ARE_BELONG_TO_US")
    elif cuerpo == "ALL_YOUR_BASE_ARE_BELONG_TO_US":
	doCmd(con,"WHAT_YOU_SAY")
    elif cuerpo == "FORTUNE":
	tellFortune(msg.getFrom())
    elif cuerpo[0:6] == "GOOGLE":
	    cuerpo = cuerpo[7:]
	    tellGoogle(msg.getFrom(),cuerpo)
    elif cuerpo[0:2] == "WP":
	    cuerpo = cuerpo[3:]
	    tellWikipedia(msg.getFrom(), cuerpo)
    elif cuerpo[0:4] == "MAIL":
	    cuerpo = cuerpo[5:]
	    tellMail(msg.getFrom(), cuerpo)
    elif cuerpo == "MLD":
	    tellMLD(msg.getFrom())

    return

def presenceCB(con, prs):
    """Called when a presence is recieved"""
    who = str(prs.getFrom())
    type = prs.getType()
    if type == None: type = 'available'

    # subscription request: 
    # - accept their subscription
    # - send request for subscription to their presence
    if type == 'subscribe':
        print colorize("subscribe request from %s" % (who), 'blue')
        con.send(jabber.Presence(to=who, type='subscribed'))
        con.send(jabber.Presence(to=who, type='subscribe'))

    # unsubscription request: 
    # - accept their unsubscription
    # - send request for unsubscription to their presence
    elif type == 'unsubscribe':
        print colorize("unsubscribe request from %s" % (who), 'blue')
        con.send(jabber.Presence(to=who, type='unsubscribed'))
        con.send(jabber.Presence(to=who, type='unsubscribe'))

    elif type == 'subscribed':
        print colorize("we are now subscribed to %s" % (who), 'blue')

    elif type == 'unsubscribed':
        print colorize("we are now unsubscribed to %s"  % (who), 'blue')

    elif type == 'available':
        print colorize("%s is available (%s / %s)" % \
                       (who, prs.getShow(), prs.getStatus()),'blue')
    elif type == 'unavailable':
        print colorize("%s is unavailable (%s / %s)" % \
                       (who, prs.getShow(), prs.getStatus()),'blue')


def iqCB(con,iq):
    """Called when an iq is recieved, we just let the library handle it at the moment"""
    print iq

def disconnectedCB(con):
    print colorize("Ouch, network error", 'red')
    sys.exit(1)

def colorize(txt, col):
    """Return colorized text"""
    if not USE_COLOR: return txt ## DJ - just incase it breaks your terms ;) ##
    cols = { 'red':1, 'green':2, 'yellow':3, 'blue':4}
    initcode = '\033[;3'
    endcode  = '\033[0m'
    if type(col) == type(1): 
        return initcode + str(col) + 'm' + txt + endcode
    try: return initcode + str(cols[col]) + 'm' + txt + endcode
    except: return txt


if len(sys.argv) == 1: usage()
Server = sys.argv[1]
Username = ''
Password = ''
Resource = 'default'


con = jabber.Client(host=Server,debug=False ,log=sys.stderr)

# Experimental SSL support
#
# con = jabber.Client(host=Server,debug=True ,log=sys.stderr,
#                    port=5223, connection=xmlstream.TCP_SSL)

try:
    con.connect()
except IOError, e:
    print "Couldn't connect: %s" % e
    sys.exit(0)
else:
    print colorize("Connected",'red')

con.setMessageHandler(messageCB)
con.setPresenceHandler(presenceCB)
con.setIqHandler(iqCB)
con.setDisconnectHandler(disconnectedCB)

if len(sys.argv) == 2:
    # Set up a jabber account
    con.requestRegInfo()
    req = con.getRegInfo()
    print req[u'instructions']
    for info in req.keys():
        if info != u'instructions' and \
           info != u'key':
            print "enter %s;" % info
            con.setRegInfo( info,strip(sys.stdin.readline()) )
    con.sendRegInfo()
    req = con.getRegInfo()
    Username = req['username']
    Password = req['password']
else:
    Username = sys.argv[2]
    Password = sys.argv[3]
    Resource = sys.argv[4]

print colorize("Attempting to log in...", 'red')


if con.auth(Username,Password,Resource):
    print colorize("Logged in as %s to server %s" % ( Username, Server), 'red')
else:
    print "eek -> ", con.lastErr, con.lastErrCode
    sys.exit(1)

print colorize("Requesting Roster Info" , 'red')
con.requestRoster()
con.sendInitPresence()
print colorize("Ok, ready" , 'red')
print colorize("Type /help for help", 'red')

JID = Username + '@' + Server + '/' + Resource

while(1):
    inputs, outputs, errors = select([sys.stdin], [], [],1)

    if sys.stdin in inputs:
        doCmd(con,sys.stdin.readline())
    else:
        con.process(1)
    
        









