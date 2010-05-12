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


PLATFORM_HOST = "127.0.0.1"

class WebAdminHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	_body_template = "<table><tr><td class=cabecera colspan=2>#TOP#</td></tr><tr><td class=lateral>#MENU_LEFT#</td><td>#PANEL_RIGHT#</td></tr><tr><td>#BOTTOM#</td></tr></table>"

	def header(self, title="SPADE AUCTIONER"):
		#return "<html><head><script src='client.js'></script><link rel=stylesheet type='text/css' href='webadmin.css'><title>" + title + "</title></head>"
		return "<html><head><link rel=stylesheet type='text/css' href='webadmin.css'><script src='client.js'></script><title>" + title + "</title></head>"


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
			print "RAW_VARS", raw_vars
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
		self._body = self._body.replace("#TOP#", "<h1>SPADE AUCTIONER</h1>")
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

		print "_POST_REQ:", self._POST_REQ

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
		print page, vars
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

		elif page == "/getauctiondata":
			s = ""
			try:
				for key in self.server.behav.myAgent.auctions.keys():
					s = s + key + " "
					s = s + str(self.server.behav.myAgent.auctions[key]["time"]) + " "
					s = s + str(self.server.behav.myAgent.auctions[key]["price"]) + " "
					if self.server.behav.myAgent.auctions[key]["current_winner"]:
						s = s + str(self.server.behav.myAgent.auctions[key]["current_winner"]) + ";;"
					else:
						s = s + "-;;"
				print s
				self.wfile.write(s)
				return
			except Exception,e:
				print "EXCEPTION " + str(e)
				return

		# Main page
		elif page == "/":
			self.setPageTemplate()
			cp = ""

			# First check if we have to update auctions data
			if vars.has_key("do") and vars["do"] == "yes":
				for auction_key, auction in self.server.behav.myAgent.auctions.items():
					if auction_key in vars.keys() and vars[auction_key]:
						auction["countdown"] = True
					else:
						auction["countdown"] = False

			"""
			if vars.has_key('bid') and vars['bid']:
				msg = ACLMessage.ACLMessage()
				to = "auctioner@" + PLATFORM_HOST
				receiver = AID.aid(name=to, addresses=["xmpp://"+to])
				msg.addReceiver(receiver)
				msg.setContent("BID "+str(vars['bid']))
				msg.setPerformative("request")
				print "SENDING A BID: " + str(msg)
				self.server.behav.myAgent.send(msg)
			"""

			cp = cp + """Current auctions<div><FORM ACTION="/" METHOD="POST"><table>
			<tr><th>Product Image</th><th>Item Name</th><th>Description</th><th>Price</th><th>Time left</th><th>Active</th><th>Higher Bidder</th></tr>"""

			parity = "impar"
			for key,auction in self.server.behav.myAgent.auctions.items():
				# Check for current auction
				# Build time left
#				time_left = int(auction["time"])
#				days_left = int(time_left / 86400)
#				time_left = time_left - (86400*days_left)
#				hours_left = int(time_left / 3600)
#				time_left = time_left - (3600*hours_left)
#				minutes_left = int(time_left / 60)
#				time_left = time_left - (60*minutes_left)
#				seconds_left = time_left % 60

				cp = cp + """
				<tr>
				<td class="""+parity+"""><img height=150 src=""" + str(auction["image"]) + """  /></td>
				<td class="""+parity+">" + auction["name"] + """</td>
				<td class="""+parity+">" + auction["desc"] + """</td>
				<td class="""+parity+"""><span class="""+parity+""" id='price_""" +key + """'></span>""" + """</td>
				<td class="""+parity+"""><span class="""+parity+""" id='time_"""  +key + """'></span>""" + """</td>
				<td class="""+parity+'''><input name="'''+key+'''" type="checkbox"'''
				if auction["countdown"]: cp = cp + '''checked="checked"'''
				cp = cp + '''/>'''
				cp = cp + """<td class="""+parity+"""><span class="""+parity+""" id='winner_"""+key+"""'></span>""" + """</td>"""
				cp = cp + '''</tr>'''

				if parity == "impar": parity = "par"
				else: parity = "impar"

			cp = cp + """<INPUT TYPE="hidden" NAME="do" VALUE="yes">"""
			cp = cp + """</table><div>"""
			cp = cp + """<INPUT TYPE="submit" VALUE="Update"></FORM>"""

			self._body = self._body.replace("#MAINCP#", cp)
			self._body = self._body.replace("#BOTTOM#", '')
			self._content = self.header() + self.body(self._body, onload="auction_update()") + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

		else:
			self._content = self.header() + self.body() + self.footer()
		self.wfile.write(self._content)



class Auctioner(Agent.Agent):

    class MainBehav(Behaviour.Behaviour):

    	def _setup(self):
    		print "Main Behav _setup"

	def _process(self):
		msg = self._receive(True)
		#print "AUCTIONER: A new message arrived"
		if "BID" in msg.getContent():
			try:
				# Check wether the auction is up
				auction = msg.getContent().split()[1]
				bid = msg.getContent().split()[2]
				if auction in self.myAgent.auctions.keys() and self.myAgent.auctions[auction]["countdown"]:
					# Register the bidder if not already registered
					if msg.getSender() not in self.myAgent.auctions[auction]["bidders"]:
						self.myAgent.auctions[auction]["bidders"].append(msg.getSender())
				#print "BIDDERS: ", str(self.myAgent.auctions[auction]["bidders"])

				rep = msg.createReply()
				rep.setPerformative("inform")

				# Check if auction is running (active)
				if not int(self.myAgent.auctions[auction]['countdown']):
					#Auction is down
					rep.setContent("DOWN " + auction)
					self.myAgent.send(rep)
					return

				#Check time of the auction
				elif int(self.myAgent.auctions[auction]['time']) <= 0:
					# Too late, the auction has already ended
					rep.setContent("LATE " + auction)
					self.myAgent.send(rep)
					return

				# Check if the bidder is already the highest bidder
				elif self.myAgent.auctions[auction]['current_winner'] == msg.getSender().getName():
					rep.setContent("ALREADY " + auction)
					self.myAgent.send(rep)
					return

				elif int(bid) > self.myAgent.auctions[auction]['price']:
					#print "The bid is greater than the current price"
					self.myAgent.auctions[auction]['price'] = int(bid)
					print "The new price is:", str(self.myAgent.auctions[auction]['price']), "made by", str(msg.getSender().getName())
					#rep.setContent(msg.getContent())
					rep.setContent("CURRENTBID "+str(auction)+" "+str(bid)+" "+str(msg.getSender().getName()))
					self.myAgent.auctions[auction]["current_winner"] = msg.getSender().getName()
					for bidder in self.myAgent.auctions[auction]["bidders"]:
						rep.receivers = [bidder]
						self.myAgent.send(rep)
				else:
					print "The bid on product %s is too low (%s <= %s) (%s)"%(str(auction),str(bid),str(self.myAgent.auctions[auction]['price']),msg.getSender().getName())
					rep.setContent("LOW " + auction)
					self.myAgent.send(rep)
					return
			except Exception, e:
				# Error in bid
				print "Error in bid:", str(e)

		elif "ASK" in msg.getContent():
			#print "I've been asked about current auctions"
			rep = msg.createReply()
			cont = ""
			for k,auction in self.myAgent.auctions.items():
				if auction["countdown"]:
					cont = cont + str(k) + "::" # + str(auction["name"]) + " " + str(auction["desc"]) + ""

					for auc_key,auc_value in auction.items():
						if auc_key in ["name","desc","image","price","time"]: #Public fields
							cont = cont + str(auc_key) + ",,'" + str(auc_value) + "',,"
					cont = cont + ";;"

			#Clean last ";;"
			if ";;" in cont:
				cont = cont[:-2]

			rep.setContent(cont)
			rep.setPerformative("inform")
			self.myAgent.send(rep)
			#print "Sent current auctions:"#, str(rep)

	def done(self):
		pass

	def onStart(self):
		print "Main Behav onStart"
		# Register service in DF
		sd = DF.ServiceDescription()
		sd.setName("AUCTION")
		sd.setType("ORGANIZATION")
		dad = DF.DfAgentDescription()
		dad.addService(sd)
		dad.setAID(self.myAgent.getAID())
		res = self.myAgent.registerService(dad)
		print "REGISTER SERVICE:",str(res)

	def onEnd(self):
		pass


    class CountDownBehav(Behaviour.PeriodicBehaviour):

        def _onTick(self):
            # If there is an ongoing countdown
            for key, auction in self.myAgent.auctions.items():
                if auction['time'] > 0 and auction["countdown"]:
                    auction['time'] = auction['time'] - self._period
                    #Check and notify end of auction
                    if auction['time'] <= 0:
                        auction["countdown"] = False
                        msg = ACLMessage.ACLMessage()
                        msg.setPerformative("inform")
                        msg.setContent("WINNER "+str(key)+" "+str(auction["price"])+" "+str(auction["current_winner"]))
                        #msg.receivers = copy.copy(auction["bidders"])  #Djkstra forgive me
                        #if msg.getReceivers():
                        #    self.myAgent.send(msg)
                        for rec in auction["bidders"]:
                            msg.receivers = [rec]
                            self.myAgent.send(msg)



    class WebAdminBehav(Behaviour.Behaviour):
        WEB_ADMIN_PORT = 8010

        def onStart(self):
            self.httpd = None
            while not self.httpd:
                try:
                    self.httpd = SocketServer.ThreadingTCPServer(('', self.WEB_ADMIN_PORT), WebAdminHandler)

                    self.httpd.behav = self
                    #thread.start_new_thread(self.httpd.serve_forever, ())
                    print "Auctioner WebAdmin serving at port "+str(self.WEB_ADMIN_PORT)
                    #self.httpd.serve_forever()
                except:
                    print "Auctioner WebAdmin Error: could not open port "+str(self.WEB_ADMIN_PORT)
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
        self.auctions = {}
        self.auctions["WII"] = {'price':10, 'name':'Wii', 'desc':'Nintendo Wii Game Console','time':1600,'image':'http://www.sinmiedo.es/wp-content/uploads/2009/01/wii.jpg','countdown':False,'bidders':[],"current_winner":""}
        self.auctions["PS3"] = {'price':600, 'name':'PS3', 'desc':'Playstation 3 Giant Crab','time':50,'image':'http://www.hoytecnologia.com/img/noticias/foto_104367.jpg','countdown':False,'bidders':[],"current_winner":""}
        self.auctions["XBX"] = {'price':490, 'name':'Xbox', 'desc':'Microsoft Xbox 360','time':2200,'image':'http://cache.gizmodo.com/images/xbox360.jpg','countdown':False,'bidders':[],"current_winner":""}
        print "Starting main Behaviour"
        self.setDefaultBehaviour(self.MainBehav())
        print "Starting Web Behaviour"
        self.addBehaviour(self.WebAdminBehav())
        print "Starting Count Down Behaviour"
        self.addBehaviour(self.CountDownBehav(1))



if __name__ == "__main__":
    """
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
    """
    #host = "thx1138.dsic.upv.es"
    host = PLATFORM_HOST

    agent = "auctioner"+"@"+host
    print "Agent "+agent+" registering"
    b = Auctioner(agent,"secret")
    try:
    	b.start()
    except Exception, e:
	print "EXCEPTION: ", str(e)

    while True:
     	time.sleep(1)

