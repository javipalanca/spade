#! /usr/bin/python

import sys
import os
sys.path.append('../..')

from spade import *
import time
from string import *
import threading
import SocketServer
import SimpleHTTPServer
import copy
import random


PLATFORM_HOST = "127.0.0.1"

class WebAdminHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    _body_template = "<table><tr><td class=cabecera colspan=2>#TOP#</td></tr><tr><td class=lateral>#MENU_LEFT#</td><td>#PANEL_RIGHT#</td></tr><tr><td>#BOTTOM#</td></tr></table>"

    def header(self, title="SPADE BIDDER"):
        """
        try:
            os.stat("modules/web/webadmin.css")
            return "<html><head><link rel=stylesheet type='text/css' href='modules/web/webadmin.css'><title>" + title + "</title></head>"
        except:
            return "<html><head><link rel=stylesheet type='text/css' href='xmppd/modules/web/webadmin.css'><title>" + title + "</title></head>"
        """

        return "<html><head><script src='client.js'></script><link rel=stylesheet type='text/css' href='webadmin.css'><title>" + title + "</title></head>"

    def body(self, body = "", onload=""):
        if onload:
            onload = '''onload="''' + onload + '''"'''
        return "<body "+str(onload)+">" + str(body) # + "</body>"

    def footer(self, foot = ""):
        return foot+"</body>"+"</html>"

    def getPage(self, req):
        """
        Return the page name from a raw GET line
        """
        return req.split("?")[0]

    def getVars(self, req):
        """
        Return the variables and values from a raw GET or POST request line
        """
        d = dict()
        try:
            raw_vars = req.split("?")[1]
            #print "RAW_VARS", raw_vars
            for raw in raw_vars.split("&"):
                #print raw
                var = raw.split("=")
                if len(var) > 1:
                    # Check if this is a multi-valued var
                    if var[0] in d.keys():
                        try:
                            # Try to append value to the list
                            d[var[0]].append(var[1])
                        except:
                            # Create a list with the current value and append the new one
                            d[var[0]] = [d[var[0]]]
                            d[var[0]].append(var[1])
                    else:
                        d[var[0]] = var[1]
                else:
                    d[var[0]] = ""
                print var
        except:
            pass

        return d

    def setPageTemplate(self):
        self._body = copy.copy(self._body_template)
        self._body = self._body.replace("#TOP#", "<h1>SPADE BIDDER</h1>")
        #self._body = self._body.replace("#MENU_LEFT#", '<a class=lateral href="/">Main</a><br/><a class=lateral href="/pref">Preferences</a><br/><a class=lateral href="/clients">Active Clients</a><br/><a class=lateral href="/plugins">Plugins</a>')
        self._body = self._body.replace("#MENU_LEFT#", '')
        self._body = self._body.replace("#PANEL_RIGHT#", """<h2>MAIN CONTROL PANEL</h2><br>#MAINCP#""")


    def do_POST(self):
        print "POST"

        self._POST_REQ = ""
        try:
            length = int(self.headers.getheader('content-length'))
            self._POST_REQ = self.rfile.read(length)
        except:
            pass

        #print "_POST_REQ:", self._POST_REQ

        self.do_GET()

    def do_GET(self):
        """
        GET petitions handler
        """
        #print "ENVIRON: ", str(os.environ)

        request = self.raw_requestline.split()
        page = self.getPage(request[1])
        try:
            vars = self.getVars("?"+self._POST_REQ)
        except:
            vars = self.getVars(request[1])
        #print page, vars
        self._content = ""
        # Switch page
        #The CSS file
        if page.endswith("css") or page.endswith("js"):
                #self.copyfile(urllib.urlopen(self.path), self.wfile)
            try:
                f = open(page[1:], "r")
                self.copyfile(f, self.wfile)
                f.close()
            except:
                print "Could not open file: ", page[1:]

        #Log viewer
        elif page == "/log":
            self.setPageTemplate()
            cp = ""

            cp = cp + """<a href="/">Bidding Control</a><div>"""

            cp = cp + """<FORM ACTION="/log" METHOD="POST"><INPUT TYPE="submit" VALUE="Refresh"></FORM><div><br/>"""
            cp = cp + self.server.behav.myAgent.log

            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

        #Get Auction Data
        elif page == "/getauctiondata":
            s = ""
            try:
                for key in self.server.behav.myAgent.auctions.keys():
                    s = s + key + " "
                    s = s + str(self.server.behav.myAgent.auctions[key]["time"]) + " "
                    s = s + str(self.server.behav.myAgent.auctions[key]["price"]) + " "
                    if self.server.behav.myAgent.auctions[key]["current_bidder"]:
                        s = s + str(self.server.behav.myAgent.auctions[key]["current_bidder"]) + ";;"
                    else:
                        s = s + "-;;"
                self.wfile.write(s)
                return
            except:
                return

        # Main page
        elif page == "/":
            self.setPageTemplate()
            cp = ""

            # Check current price

            self.server.behav.myAgent.check_price()

            #Process POST vars
            if vars.has_key("do") and vars["do"] == "yes":
                for auction_key, auction in self.server.behav.myAgent.auctions.items():

                    if auction_key+"_max" in vars.keys() and vars[auction_key+"_max"]:
                        if auction["max"] and auction["bidding"]:
                            self.server.behav.myAgent.update_log("Updating bid to "+str(vars[auction_key+'_max']))
                            self.server.behav.myAgent.money=self.server.behav.myAgent.money-int(vars[auction_key+"_max"])+int(auction["max"])
                        auction["max"] = vars[auction_key+"_max"]
                    else:
                        auction["max"] = None
                    #print "AUCTION: ", str(auction)
                    if auction_key in vars.keys():# and vars[auction_key]:
                        if not auction["bidding"]:
                            if self.server.behav.myAgent.money >= int(vars[auction_key+"_max"]):
                                if int(vars[auction_key+"_max"]) >= int(auction["price"]):
                                    self.server.behav.myAgent.update_log("Now bidding ("+str(self.server.behav.myAgent.money)+" >= "+str(vars[auction_key+'_max'])+")")
                                    self.server.behav.myAgent.money= int(self.server.behav.myAgent.money) - int(vars[auction_key+"_max"])
                                else:
                                    # Join / Start a coallition
                                    if not self.server.behav.myAgent.inCoallition(auction_key):
                                        if self.server.behav.myAgent.start_org(auction_key, int(vars[auction_key+"_max"])):
                                            self.server.behav.myAgent.money= int(self.server.behav.myAgent.money) - int(vars[auction_key+"_max"])

                                auction["bidding"] = True
                            else:
                                auction["bidding"] = False
                                self.server.behav.myAgent.update_log("Not enough money ("+str(self.server.behav.myAgent.money)+" < "+str(vars[auction_key+'_max'])+")")
                    else:
                        if auction["bidding"]:
                            if auction["time"]>0 and self.server.behav.myAgent.getAID().getName()!=auction["current_bidder"]:
                                self.server.behav.myAgent.money=self.server.behav.myAgent.money+int(vars[auction_key+"_max"])
                                auction["bidding"] = False
                                self.server.behav.myAgent.update_log("Auction Cancelled")
                            else:
                                self.server.behav.myAgent.update_log("You cannot leave an auction when you are the current winner")

            cp = cp + "Agent: " + self.server.behav.myAgent.getAID().getName() + """<div>"""
            cp = cp + "Money: <b>" + str(self.server.behav.myAgent.money) + """</b><div>"""

            cp = cp + """<a href="/log">Agent Log</a><div>"""

            cp = cp + """Current auctions<div><FORM ACTION="/" METHOD="POST"><table>
            <tr><th>Product Image</th><th>Item Name</th><th>Description</th><th>Price</th><th>Time left</th><th>Current Winner</th><th>Bid</th><th>Max Amount</th></tr>"""

            onload = ""

            parity = "impar"
            for key,auction in self.server.behav.myAgent.auctions.items():
                # Check for current auction
                # Build time left
#                time_left = int(auction["time"])
#                days_left = int(time_left / 86400)
#                time_left = time_left - (86400*days_left)
#                hours_left = int(time_left / 3600)
#                time_left = time_left - (3600*hours_left)
#                minutes_left = int(time_left / 60)
#                time_left = time_left - (60*minutes_left)
#                seconds_left = time_left % 60

                cp = cp + """
                <tr>
                <td class="""+parity+"""><img height=130 width=150 src=""" + str(auction["image"]) + """  /></td>
                <td class="""+parity+">" + auction["name"] + """</td>
                <td class="""+parity+">" + auction["desc"] + """</td>"""

                #cp = cp + """<td class="""+parity+">" + str(auction["price"]) + """</td>"""
                cp = cp + """<td class="""+parity+"><span class="+parity+" id='price_" +key + """'></span></td>"""

                #The time
                #cp = cp + """<td class="""+parity+">" + "<span id='time_"+key+"'>" + str(days_left) + """d """ + str(hours_left) + """h """ + str(minutes_left) + """m """ + str(seconds_left) + """s</span></td>"""

                # The time with javascript
                cp = cp + """<td class="""+parity+"""><span class="""+parity+""" id='time_"""+key+"""'></span></td>"""

                # The current winner with javascript
                cp = cp + """<td class="""+parity+"""><span class="""+parity+""" id='winner_"""+key+"""'></span></td>"""

                cp = cp + """<td class="""+parity+'''><input name="'''+key+'''" type="checkbox"'''
                if auction["bidding"]: cp = cp + ''' checked="checked" '''
                if auction["time"] <= 0: cp = cp + ''' disabled="disabled" '''
                cp = cp + """/></td>"""
                cp = cp + """<td class="""+parity+'''><input name="'''+key+'''_max" type=text'''
                if auction["max"]: cp = cp + ''' value=''' + str(auction["max"])
                cp = cp + """ /></td></tr>"""

                if parity == "impar": parity = "par"
                else: parity = "impar"

            cp = cp + """<INPUT TYPE="hidden" NAME="do" VALUE="yes">"""
            cp = cp + """</table><div>"""
            cp = cp + """<INPUT TYPE="submit" VALUE="Bid for these items"></FORM>"""

            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body, onload="auction_update()") + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

        else:
            self._content = self.header() + self.body() + self.footer()
        self.wfile.write(self._content)






class Bidder(Agent.Agent):

    class OrgBehav(Behaviour.Behaviour):
        def onStart(self):
            self.members = []
            # I should build or join a coallition
            #if self.myAgent.money < 100:
            # Coalliate
            dad = DF.DfAgentDescription()
            ds = DF.ServiceDescription()
            ds.setName("ALLIANCE_"+self._item)
            #ds.addProperty({'item':self._item})
            dad.addService(ds)
            search = self.myAgent.searchService(dad)
            #print str(search)

            aname = False
            if str(search).strip():
                try:
                    for j in range(0,len(search)):
                        entry = search[j][1]
    #                    print "ENTRY:", str(entry)
    #                    print "ENTRY KEYS:", str(entry.keys())
    #                    print "ENTRY VALUES:", str(entry.values())
    #                    print "ENTRY.NAME:", str(entry.name.asDict())
                        for e in entry.services.set.values():
                            #print "SERVICE LIST:", str(e.asDict())
                            sname = str(e.asDict()['name']).strip("[']")
                            print "SERVICE NAME:", sname
                            if "ALLIANCE" in sname:
                                aname = str(entry['name']['agent-identifier']['name']).strip("[']")

                except Exception, e:
                    print "EXCEPTION: ", str(e)

            if aname:
                msg = ACLMessage.ACLMessage()
                msg.addReceiver(AID.aid(aname, addresses=["xmpp://"+aname]))
                msg.setContent("JOIN " + str(self._money))
                msg.setPerformative("request")
                msg.setOntology("spade:x:organization")
                self.myAgent.send(msg)
                self.supervisor = False
                self.myAgent.update_log("Tried to JOIN coallition " + self._item)
            else:
                # Register service in DF
                sd = DF.ServiceDescription()
                sd.setName("ALLIANCE_"+self._item)
                sd.setType("organization")
                sd.addProperty({"name":"topology","value":"coallition"})
                dad = DF.DfAgentDescription()
                dad.addService(sd)
                dad.setAID(self.myAgent.getAID())
                #print dad
                res = self.myAgent.registerService(dad)
                #print str(res)
                self.members.append(self.myAgent.getAID())
                self.supervisor = True
                self.myAgent.auctions[self._item]["original_max"] = self._money
                self.myAgent.coallitions[self._item] = True  # I'm the boss
                self.myAgent.update_log("I started a coallition to buy item " + self._item)


        def _process(self):
            msg = self._receive(True,5)
            if msg == None:
                if self.myAgent.auctions[self._item]["time"] <= 0 and self.supervisor:
                    if self.myAgent.auctions[self._item]["current_bidder"] == self.myAgent.getAID().getName():
                        # We are the winners (as a coallition)
                        # Forward the WINNER message to every member changing the winner name
                        rep = ACLMessage.ACLMessage()
                        rep.setPerformative("inform")
                        for m in self.members:
                            if m != self.myAgent.getAID():
                                rep.setContent("WINNER "+ self._item +" " + str(self.myAgent.auctions[self._item]["price"]) + " " + str(m.getName()))
                                rep.receivers = [m]
                                self.myAgent.send(rep)
                    else:
                        rep = ACLMessage.ACLMessage()
                        rep.setPerformative("inform")
                        rep.setContent("WINNER "+ self._item +" " + str(self.myAgent.auctions[self._item]["price"])+" "+str(self.myAgent.auctions[self._item]["current_bidder"]))
                        for m in self.members:
                        	if m != self.myAgent.getAID():
	                            rep.receivers = [m]
	                            self.myAgent.send(rep)
                    #Terminate behaviour
                    self.kill()

                return
            elif "MEMBERS" in msg.getContent():
                print "I have been asked for the members"
                rep = msg.createReply()
                content = ""
                for m in self.members:
                    content = content + str(m.getName()) + ","
                content = content[:-1]
                rep.setContent(content)
                rep.setOntology("spade:x:organization")
                rep.setPerformative("inform")
                #print rep
                self.myAgent.send(rep)

            elif "JOIN" in msg.getContent():
                self.myAgent.auctions[self._item]["max"] = int(self.myAgent.auctions[self._item]["max"]) + int(msg.getContent().split(" ")[1])
                entry = "Someone wants to join my organization with " + msg.getContent().split(" ")[1] + " euros"
                self.myAgent.update_log(entry)
                print entry
                rep = msg.createReply()
                if msg.getSender() not in self.members:
                    content = "AGREE"
                    self.members.append(msg.getSender())
                    print "MEMBERS: ", str(self.members)
                    entry = "I have let " + msg.getSender().getName() + " join my organization"
                    self.myAgent.update_log(entry)
                    print entry
                else:
                    content = "REFUSE"
                    entry = "I have denied " + msg.getSender().getName() + "'s request to join my organization"
                    self.myAgent.update_log(entry)
                    print entry
                rep.setContent(content)
                rep.setOntology("spade:x:organization")
                self.myAgent.send(rep)
            elif "AGREE" in msg.getContent():
                print "I am a soul member! PARAPA"
            elif "REFUSE" in msg.getContent():
                print "They didn't want me :-("


    class CheckPriceBehav(Behaviour.OneShotBehaviour):
        def __init__(self, msg):
            Behaviour.OneShotBehaviour.__init__(self)
            self.result = None
            self.finished = False
            self._msg = msg

        def _process(self):
            to = "auctioner@" + PLATFORM_HOST
            receiver = AID.aid(name=to, addresses=["xmpp://"+to])
            self._msg.addReceiver( receiver )
            self._msg.setPerformative('request')
            self._msg.setContent("ASK")
            #print "ASKING CURRENT AUCTIONS"
            self.myAgent.send(self._msg)

            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'inform':
                print "There was an error bidding. (not inform)"
                self.finished = True
                return None
            else:
                try:
                    if "::" in msg.getContent():
                        auctions_list = msg.getContent().split(";;")
                        for auc in auctions_list:
                            key,auction = auc.split("::")
                            auction = auction.split(",,")

                            if not self.myAgent.auctions.has_key(key): self.myAgent.auctions[key] = {}

                            for i in range(0,len(auction),2):
                                if auction[i]:
                                    self.myAgent.auctions[key][auction[i].strip("'")] = auction[i+1].strip("'")
                            if not self.myAgent.auctions[key].has_key("bidding"): self.myAgent.auctions[key]['bidding'] = False
                            if not self.myAgent.auctions[key].has_key("max"): self.myAgent.auctions[key]['max'] = None
                            if not self.myAgent.auctions[key].has_key("step"): self.myAgent.auctions[key]['step'] = 5
                            if not self.myAgent.auctions[key].has_key("current_bidder"): self.myAgent.auctions[key]["current_bidder"] = ""

                        #print "The current price is ", str(msg.getContent().split()[1])
                        #self.result = msg.getContent().split()[1]
                    else:
                        #print "There are no active auctions"
                        self.result = "UNKNOWN"
                except Exception, e:
                    print "The current auctions are unknown: ", str(e)
                    self.result = "UNKNOWN"

            self.finished = True


    class MainBehav(Behaviour.Behaviour):

#        def _setup(self):
#            print "Main Behav _setup"

        def _process(self):
            t = time.time()
            if (t - self.timer) > 1:  #Wait a second Mr. Postman
                #Check Prices
                self.myAgent.check_price()
                self.timer = time.time()

            to = "auctioner@" + PLATFORM_HOST
            receiver = AID.aid(name=to, addresses=["xmpp://"+to])
#            self._msg.addReceiver( receiver )
#            self._msg.setPerformative('request')
#            self._msg.setContent("BID "+str(self.amount))
#            print "SENDING A BID OF ", str(self.amount)
#            self.myAgent.send(self._msg)

            for k,auction in self.myAgent.auctions.items():
                if auction['bidding']:
                    if (self.myAgent.coallitions.has_key(k) and self.myAgent.coallitions[k] == True) or \
                    not self.myAgent.coallitions.has_key(k):
                        # I'm the supervisor of a coallition OR an independent bidder
                        # If I'm not the current higher bidder
                        if int(auction['time']) > 0:
                            if auction['current_bidder'] != self.myAgent.getAID().getName():
                                if int(auction['price']) + int(auction['step']) <= int(auction['max']) :
                                    bid = int(auction['price']) + int(auction['step'])
                                    rep = ACLMessage.ACLMessage()
                                    rep.setPerformative("request")
                                    rep.addReceiver(receiver)
                                    rep.setContent("BID "+k+" "+str(bid))
                                    self.myAgent.send(rep)
                                    self.myAgent.update_log("I have bidded for item " + k + " a quantity of " + str(bid) + " euros")
                                    #Update the price and current_bidder of the item based on my own bid.
                                    #We don't wait for auctioner confirmation. We initially suppose that our bid is the best
                                    auction['price'] = str(bid)
                                    auction['current_bidder'] = self.myAgent.getAID().getName()

            self.msg = None
            self.msg = self._receive(True,1)  #Adjust this timeout to prevent CPU hogging
            if self.msg == None:
                #self.myAgent.check_price()
                return
            elif self.msg.getPerformative() != 'inform':
                print "There was an error bidding. (not inform)"
                self.myAgent.update_log("I received an erroneous message")
                return None
            else:
                if "CURRENTBID" in self.msg.getContent():
                    cont_list = self.msg.getContent().split()
                    self.myAgent.auctions[cont_list[1]]["price"] = cont_list[2]
                    self.myAgent.auctions[cont_list[1]]["current_bidder"] = cont_list[3]
                    if cont_list[3] == self.myAgent.getAID().getName():
                        entry =  "Confirmation that I made a bid for item %s of %s"%(cont_list[1],cont_list[2])
                        print entry
                        self.myAgent.update_log(entry)
                    else:
                        entry = "Bidder %s made a bid for item %s of %s"%(cont_list[3],cont_list[1],cont_list[2])
                        print entry
                        self.myAgent.update_log(entry)

                elif "LOW" in self.msg.getContent():
                    cont_list = self.msg.getContent().split()
                    entry = "My bid for item " + cont_list[1] + " was too low :-("
                    print entry
                    self.myAgent.update_log(entry)
                    # We no longer suppose that we are the current_bidder
                    self.myAgent.auctions[cont_list[1]]["current_bidder"] = ""
                    #self.myAgent.check_price()

                elif "ALREADY" in self.msg.getContent():
                    cont_list = self.msg.getContent().split()
                    entry = "I am already the highest bidder for item " + cont_list[1]
                    print entry
                    self.myAgent.update_log(entry)
                    #self.myAgent.check_price()

                elif "LATE" in self.msg.getContent():
                    cont_list = self.msg.getContent().split()
                    entry = "My bid for item " + cont_list[1] + " arrived too late"
                    print entry
                    self.myAgent.update_log(entry)
                    self.myAgent.auctions[cont_list[1]]["bidding"] = False
                    #self.myAgent.check_price()

                elif "DOWN" in self.msg.getContent():
                    cont_list = self.msg.getContent().split()
                    entry = "The auction for item " + cont_list[1] + " is down"
                    print entry
                    self.myAgent.update_log(entry)
                    self.myAgent.auctions[cont_list[1]]["bidding"] = False
                    #self.myAgent.check_price()

                elif "WINNER" in self.msg.getContent():
                    cont_list = self.msg.getContent().split()
                    entry = "A bid has ended. The winner was " + str(cont_list[3])
                    print entry
                    self.myAgent.update_log(entry)
                    self.myAgent.auctions[cont_list[1]]["price"] = cont_list[2]
                    self.myAgent.auctions[cont_list[1]]["current_bidder"] = cont_list[3]
                    self.myAgent.auctions[cont_list[1]]["time"] = 0
                    if cont_list[3] != self.myAgent.getAID().getName():
                        if self.myAgent.coallitions.has_key(cont_list[1]) and self.myAgent.coallitions[cont_list[1]] == True:
                             self.myAgent.money = int(self.myAgent.money) + int(self.myAgent.auctions[cont_list[1]]["original_max"])
                        else:
                             self.myAgent.money = int(self.myAgent.money) + int(self.myAgent.auctions[cont_list[1]]["max"])
                    #self.myAgent.check_price()


        def done(self):
            pass

        def onStart(self):
            print "Main Behav onStart"

            # Start timer
            self.timer = time.time()

#
#            # If I'm poor, I should build or join a coallition
#            if self.myAgent.money < 10000:
#                # Coalliate
#                dad = DF.DfAgentDescription()
#                ds = DF.ServiceDescription()
#                ds.setName("ALLIANCE")
#                dad.addService(ds)
#                search = self.myAgent.searchService(dad)
#                #print str(search)



        def onEnd(self):
            pass


    class WebAdminBehav(Behaviour.Behaviour):
        #WEB_ADMIN_PORT = 8009

        def onStart(self):
            self.httpd = None
            while not self.httpd:
                try:
                    self.WEB_ADMIN_PORT = int(self.myAgent.WEB_ADMIN_PORT)
                except:
                    self.WEB_ADMIN_PORT = 8009
                try:
                    self.httpd = SocketServer.ThreadingTCPServer(('', self.WEB_ADMIN_PORT), WebAdminHandler)

                    self.httpd.behav = self
                    #thread.start_new_thread(self.httpd.serve_forever, ())
                    entry = "Bidder WebAdmin serving at port "+str(self.WEB_ADMIN_PORT)
                    print entry
                    self.myAgent.update_log(entry)
                    #self.httpd.serve_forever()
                except:
                    entry = "Bidder WebAdmin Error: could not open port "+str(self.WEB_ADMIN_PORT)
                    print entry
                    self.myAgent.update_log(entry)
                    time.sleep(5)
                    #if self.httpd: del self.httpd

        def _process(self):
            self.httpd.handle_request()

        def onEnd(self):
            del self.httpd

        def done(self):
            pass
            #print "Bidder WebAdmin Terminated"

    def _setup(self):
        self.log = ""  #Events log

        self.auctions = {}
        self.coallitions = {}  #Buying Coallitions the agent is in
        entry = "Starting main Behaviour"
        self.setDefaultBehaviour(self.MainBehav())
        print entry
        self.update_log(entry)
        entry = "Starting Web Behaviour"
        self.addBehaviour(self.WebAdminBehav())
        print entry
        self.update_log(entry)

#    def bid(self, amount):
#        msg = ACLMessage.ACLMessage()
#        template = Behaviour.ACLTemplate()
#        template.setConversationId(msg.getConversationId())
#        t = Behaviour.MessageTemplate(template)
#        b = self.BidBehav(msg, amount)
#
#        self.addBehaviour(b,t)
#        b.join()
#        return b.result

    def start_org(self, item, money):
        entry = "Starting Organizative Behaviour for item " + item + " with money " + str(money)
        print entry
        self.update_log(entry)
        template = Behaviour.ACLTemplate()
        template.setOntology("spade:x:organization")
        t = Behaviour.MessageTemplate(template)
        o = self.OrgBehav()
        o._item = item
        o._money = money
        self.addBehaviour(o, t)
        self.coallitions[item] = False
        return True

    def inCoallition(self, item):
        if item in self.coallitions.keys():
            return True
        else:
            return False

    def check_price(self):
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = self.CheckPriceBehav(msg)

        self.addBehaviour(b,t)
        b.join()
        return b.result

    def update_log(self, entry):
        self.log = str(entry) + "<br/>" + self.log



if __name__ == "__main__":
    """
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
    """
    host = PLATFORM_HOST

    agent = "bidder"+str(random.randint(0,10000))+"@"+host
    print "Agent "+agent+" registering"
    b = Bidder(agent,"secret")
    if len(sys.argv) > 1:
        b.WEB_ADMIN_PORT = sys.argv[1]
    else:
        b.WEB_ADMIN_PORT = 8009
    if len(sys.argv) > 2:
        b.money = int(sys.argv[2])
    else:
        b.money = 5000

    try:
        b.start()
    except Exception, e:
        print "EXCEPTION: ", str(e)

    while True:
        time.sleep(1)
