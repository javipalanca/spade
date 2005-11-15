#! python
import pygtk
#pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
import pango, atk
import pickle
import sys
import types
import time
import os
from spade import *

#a.func_defaults
#a.func_code.co_varnames

if os.name == "posix":
	rmaxml = os.sep + "usr" + os.sep + "share" + os.sep + "spade" + os.sep + "rma.glade"
else:
	rmaxml = "usr/share/spade/rma.glade"

class GTKWindow:
	def __init__(self, file, windowname):
		self._file = file
		self._windowname=windowname
		self.glade = gtk.glade.XML(self._file, self._windowname)
		self.win = self.glade.get_widget(self._windowname)


class rma(Agent.Agent):						
	class RunAgentWindow(GTKWindow):
		def __init__(self, mainWin):
			rma.GTKWindow.__init__(self,rmaxml,"RunAgent")
			self.glade.signal_autoconnect(self)
			self.win.show()
			self.mainWin = mainWin
		
		def on_run_clicked(self, data):
			filepath = self.glade.get_widget("filechooser").get_filename()
			path = self.glade.get_widget("filechooser").get_current_folder()
			name = self.glade.get_widget("name").get_text()
			passwd = self.glade.get_widget("password").get_text()
			
			file = filepath[len(path)+1:-3]
			sys.path.append(path)
			for a in vars(__import__(file)).itervalues():
				try:
					if (issubclass(a,Agent.Agent)):
						agent = a(name, passwd)
						agent.start()
						self.mainWin.listagents.append(agent)
				except:
					pass
			
			#self.mainWin.on_updateagents_clicked(None)
			self.win.destroy()
		def on_cancel_clicked(self, data):
			self.win.destroy()

	class MainWindow(GTKWindow):
		def __init__(self, agent):
			rma.GTKWindow.__init__(self,rmaxml,"MainWindow")
			self.myAgent = agent
			self.listagents = []
			self.glade.signal_autoconnect(self)
			self.configure_agentslist()
			self.win.show()
			self.on_updateagents_clicked(None)
			
		def on_window_delete_event(self, widget, event, data=None):
			gtk.main_quit()
			return False
			
		def configure_agentslist(self):
			self.agentslistwidget = self.glade.get_widget("agentslist")
			self.agentsliststore = gtk.ListStore(str,str)
			
			self.agentslistwidget.set_model(self.agentsliststore)
			
			# New Column: Agent Name
			column = gtk.TreeViewColumn('Agent Name')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			self.agentslistwidget.append_column(column)
			# New Column: Agent Address
			column = gtk.TreeViewColumn('Agent Address')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 1)
			self.agentslistwidget.append_column(column)
			
			self.agentslistwidget.set_search_column(0)
			#self.agentslistwidget.set_reorderable(True)
			self.agentslistwidget.set_headers_clickable(True)
		
		def on_sendmessage_clicked(self, data):
			win = rma.ACLMessageSend(self.myAgent)
			
		def on_newagent_clicked(self,k):
			win = rma.RunAgentWindow(self)
			
		def on_removeagent_clicked(self,k):
			model,iter = self.agentslistwidget.get_selection().get_selected()
			name = model.get_value(iter,0)
			
			for a in self.listagents:
				if name == a.getAID().getName():
					a.kill()
			
			
		def on_updateagents_clicked(self,k):
			print "Update Agents!"
			aad = AMS.AmsAgentDescription()
			agents = self.myAgent.searchAgent(aad, debug=True)
			self.agentsliststore.clear()
			if (agents != None):
				for i in agents:
					aad = AMS.AmsAgentDescription(i)
					print str(aad)
					aid = aad.getAID()
					self.agentsliststore.append([aid.getName(), str(aid.getAddresses())])
			
	
	class AIDViewer(GTKWindow):
		def __init__(self, aid):
			rma.GTKWindow.__init__(self,rmaxml,"AIDViewer")
			self.glade.signal_autoconnect(self)
			self.configure_lists()
			self.read_aid(aid)
			self.win.show()

		def configure_lists(self):
			addresslistwidget = self.glade.get_widget("addresses")
			resolverslistwidget = self.glade.get_widget("resolvers")
			self.addressliststore = gtk.ListStore(str)
			self.resolversliststore = gtk.ListStore(str)
			
			addresslistwidget.set_model(self.addressliststore)
			resolverslistwidget.set_model(self.resolversliststore)
			
			# New Column
			column = gtk.TreeViewColumn('Addresses')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			addresslistwidget.append_column(column)

			column = gtk.TreeViewColumn('Resolvers')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			resolverslistwidget.append_column(column)
			
	class AIDEdit(GTKWindow):
		def __init__(self):
			rma.GTKWindow.__init__(self,rmaxml,"AIDEdit")
			self.glade.signal_autoconnect(self)
			self.configure_lists()
			self.win.show()
			self.aid = None
			self.Closed = False
		
		def getAID():
			return self.aid
		
		def on_edit_cb(self,cell, path_string, new_text, data):
			iter = data.get_iter(path_string)
			data.set_value(iter, 0, new_text)
			
		def on_addaddress_clicked(self, data):
			self.addressliststore.append(["<new>"])
		def on_addresolver_clicked(self, data):
			self.resolversliststore.append(["<new>"])
		def configure_lists(self):
			addresslistwidget = self.glade.get_widget("addresses")
			resolverslistwidget = self.glade.get_widget("resolvers")
			self.addressliststore = gtk.ListStore(str)
			self.resolversliststore = gtk.ListStore(str)
			
			addresslistwidget.set_model(self.addressliststore)
			resolverslistwidget.set_model(self.resolversliststore)
			
			# New Column
			column = gtk.TreeViewColumn('Addresses')
			cell = gtk.CellRendererText()
			cell.set_property("editable",True)
			cell.connect('edited', self.on_edit_cb, self.addressliststore)
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			addresslistwidget.append_column(column)

			column = gtk.TreeViewColumn('Resolvers')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			cell.set_property("editable",True)
			cell.connect('edited', self.on_edit_cb, self.resolversliststore)
			column.add_attribute(cell, 'text', 0)
			resolverslistwidget.append_column(column)

			
		def on_cancel_clicked(self,data):
			self.win.destroy()
		
		def on_ok_clicked(self,data):
			self.aid = AID.aid()
			self.aid.setName(self.glade.get_widget("name").get_text())
			iter = self.addressliststore.get_iter_first()
			while (iter != None):
				self.aid.addAddress(self.addressliststore.get_value(iter,0))
				iter = self.addressliststore.iter_next(iter)
			iter = self.resolversliststore.get_iter_first()
			while (iter != None):
				self.aid.addResolver(self.resolversliststore.get_value(iter,0))
				iter = self.resolversliststore.iter_next(iter)
			self.win.destroy()
		
		def on_destroy(self, data):
			self.Closed = True
	

	
	class ACLMessageViewer(GTKWindow):
		def __init__(self, msg):
			rma.GTKWindow.__init__(self,rmaxml,"ACLMessageViewer")
			self.glade.signal_autoconnect(self)
			self.configure_lists()
			self.read_message(msg)
			self.win.show()
			self._msg = msg
		def configure_lists(self):
			receiverslistwidget = self.glade.get_widget("receivers")
			self.receiversliststore = gtk.ListStore(str,str)
			receiverslistwidget.set_model(self.receiversliststore)
			# New Column
			column = gtk.TreeViewColumn('Agents')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			receiverslistwidget.append_column(column)
			reply_tolistwidget = self.glade.get_widget("reply_to")
			self.reply_toliststore = gtk.ListStore(str,str)
			reply_tolistwidget.set_model(self.reply_toliststore)
			# New Column
			column = gtk.TreeViewColumn('Agents')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			reply_tolistwidget.append_column(column)
			
			
		def read_message(self,msg):
			self.glade.get_widget("performative").set_text(str(msg.getPerformative()))
			self.glade.get_widget("sender_name").set_text(str(msg.getSender().getName()))
			for r in msg.getReceivers():
				self.receiversliststore.append([r.getName(), pickle.dumps(r)])
			for r in msg.getReplyTo():
				self.reply_toliststore.append([r.getName(), pickle.dumps(r)])
			buf = gtk.TextBuffer()
			buf.set_text(str(msg.getContent()))
			self.glade.get_widget("content").set_buffer(buf)
			self.glade.get_widget("reply_with").set_text(str(msg.getReplyWith()))
			self.glade.get_widget("reply_by").set_text(str(msg.getReplyBy()))
			self.glade.get_widget("in_reply_to").set_text(str(msg.getInReplyTo()))
			self.glade.get_widget("encoding").set_text(str(msg.getEncoding()))
			self.glade.get_widget("language").set_text(str(msg.getLanguage()))
			self.glade.get_widget("ontology").set_text(str(msg.getOntology()))
			self.glade.get_widget("protocol").set_text(str(msg.getProtocol()))
			
		def on_close_clicked(self,data):
			self.win.destroy()
			
		def on_view_sender_clicked(self,data):
			w = rma.AIDViewer(self._msg.getSender())
			
	class ACLMessageSend(GTKWindow):
		def __init__(self, agent):
			rma.GTKWindow.__init__(self,rmaxml,"ACLMessageSend")
			self.configure_lists()
			self.glade.signal_autoconnect(self)
			self.win.show()
			self.myAgent = agent
			self.Sender = None
		def configure_lists(self):
			receiverslistwidget = self.glade.get_widget("receivers")
			self.receiversliststore = gtk.ListStore(str,str)
			receiverslistwidget.set_model(self.receiversliststore)
			# New Column
			column = gtk.TreeViewColumn('Agents')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			receiverslistwidget.append_column(column)
			reply_tolistwidget = self.glade.get_widget("reply_to")
			self.reply_toliststore = gtk.ListStore(str,str)
			reply_tolistwidget.set_model(self.reply_toliststore)
			# New Column
			column = gtk.TreeViewColumn('Agents')
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', 0)
			reply_tolistwidget.append_column(column)
	
		def on_edit_sender_clicked(self,data):
			win = rma.AIDEdit()
			win.win.connect("destroy", self.setSender, win)
		def setSender(self, w, aidEdit):
			if aidEdit.aid != None:
				self.Sender = aidEdit.aid
				self.glade.get_widget("sender").set_text(aidEdit.aid.getName())
		def on_add_receiver_clicked(self,data):
			win = rma.AIDEdit()
			win.win.connect("destroy", self.addReceiver, win)
		def addReceiver(self, w, aidEdit):
			if aidEdit.aid != None:
				self.receiversliststore.append([aidEdit.aid.getName(),pickle.dumps(aidEdit.aid)])
						
			
		def on_cancel_clicked(self,data):
			self.win.destroy()		
		def on_send_clicked(self,data):
			msg = ACLMessage.ACLMessage()
			msg.setPerformative(self.glade.get_widget("performative").get_active_text())
			msg.setSender(self.Sender)
			iter = self.receiversliststore.get_iter_first()
			while (iter != None):
				k = pickle.loads(self.receiversliststore.get_value(iter,1))
				print type(k),k
				msg.addReceiver(k)
				iter = self.receiversliststore.iter_next(iter)
			buf = self.glade.get_widget("content").get_buffer()
			t=buf.get_text(*buf.get_bounds())
			msg.setContent(t)			
			#t=self.glade.get_widget("reply_to").get_text()
			#if t !="": msg.addReplyTo(t)
			t=self.glade.get_widget("reply_with").get_text()
			if t !="": msg.setReplyWith(t)
			t=self.glade.get_widget("reply_by").get_text()
			if t !="": msg.setReplyBy(t)
			t=self.glade.get_widget("in_reply_to").get_text()
			if t !="": msg.setInReplyTo(t)
			t=self.glade.get_widget("encoding").get_text()
			if t !="": msg.setEncoding(t)
			t=self.glade.get_widget("language").get_text()
			if t !="": msg.setLanguage(t)
			t=self.glade.get_widget("ontology").get_text()
			if t !="": msg.setOntology(t)
			t=self.glade.get_widget("protocol").get_text()
			if t !="": msg.setProtocol(t)
			
			print str(msg)
			self.myAgent.send(msg)
			self.win.destroy()


	class GUIBehaviour(Behaviour.PeriodicBehaviour):
		def __init__(self):
			Behaviour.PeriodicBehaviour.__init__(self, 10)
		
		def onStart(self):
			win = rma.MainWindow(self.myAgent)
			gobject.idle_add(rma.GUIBehaviour.idle,self)
			
		def process(self):
			pass
			
		def idle(self):
			#MIGUEL
			msg = self.blockingReceive(0.2)
			if (msg != None):
				win = rma.ACLMessageViewer(msg)
			return True
				
		
	def setup(self):
		self.setDefaultBehaviour(rma.GUIBehaviour())
		#self.addBehaviour(rma.TestBehaviour(5))
		#self.addBehaviour(rma.TestBehaviour(10))
	
		

	class TestBehaviour(Behaviour.TimeOutBehaviour):
		def timeOut(self):
			print "TimeOut!!"
			to = self.myAgent.getAID()
			msg = ACLMessage.ACLMessage()
			msg.addReceiver(to);
			msg.setPerformative('query-ref')
			msg.setContent("ping")
			self.myAgent.send(msg)
			

class RMALogin(GTKWindow):
	def __init__(self):
		GTKWindow.__init__(self,rmaxml,"RMALogin")
		self.glade.signal_autoconnect(self)
		self.win.show()
		
	def on_cancel_clicked(self, data):
		print "cancel"
		gtk.main_quit()
		
	def on_ok_clicked(self, data):
		self.win.hide();
		username = self.glade.get_widget("entry_username").get_text()
		password = self.glade.get_widget("entry_passwd").get_text()
		rma_instance=rma(username, password)
		rma_instance.start_and_wait()
		rma_instance.kill()
		gtk.main_quit()
		
	def on_window_delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False


if __name__ == "__main__":
	login = RMALogin()
	gtk.main()

