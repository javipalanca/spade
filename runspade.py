#!/usr/bin/env python

import os #, signal
import sys
import time
import thread
from os.path import *

from getopt import getopt
try:
	from spade import spade_backend
#	from spade import SpadeConfigParser
	from spade import colors
	#from xmppd.filters import acc
except ImportError:
	print "Could not import spade package!!!"
	#from libspade import spade_backend
	#from libspade import SpadeConfigParser
	#from libspade import colors


# Esto hay que ponerlo algun vez ? - Gus

#os.chdir("xmppd")
#from xmppd import xmppd
#os.chdir("..")

from xmppd.xmppd import Server


VERSION = colors.color_red + "2.0.alpha" + colors.color_none


def print_help():
  print
  print "Usage: %s [options]" % sys.argv[0]
  print " -h, --help         display this help text and exit"
  print " -v, --version      display the version and exit"
  print " -d, --debug        enable the debug execution"
  print " -c, --configfile   load the configuration file (default /etc/spade/spade.xml)"
  print " -j, --jabber       load the jabber configuration file (default /usr/share/spade/jabberd/jabber.xml)"
  raise SystemExit

def print_version():
  print "SPADE %s by Javi Palanca, Gustavo Aranda, Miguel Escriva and others" % VERSION
  print "jpalanca@dsic.upv.es - http://spade.gti-ia.dsic.upv.es/"
  raise SystemExit

def launchtg(platform):
	import pkg_resources
	pkg_resources.require("TurboGears")	
	from turbogears import update_config, start_server
	import cherrypy
	cherrypy.lowercase_api = True
	"""
	if len(sys.argv) > 1:
	    update_config(configfile=sys.argv[1], 
	        modulename="swi.config")
	"""
	if exists(join(dirname(__file__), "setup.py")):
	    update_config(configfile="dev.cfg",modulename="swi.config")
	else:
	    update_config(configfile="prod.cfg",modulename="swi.config")	
	from swi.controllers import Root
	r = Root()
	r.platform = platform
	start_server(r)

# Actually start the program running.
def main():

  gui = False
  if len(sys.argv) < 2: pass
  elif sys.argv[1] in ["--help", "-h"]: print_help()
  elif sys.argv[1] in ["--version", "-v"]: print_version()
  elif sys.argv[1] in ["--gui", "-g"]: gui = True


  configfilename = "/etc/spade/spade.xml"
  jabberxml = "/etc/spade/xmppd.xml"
  dbg = []

  if os.name != "posix" or not os.path.exists(jabberxml) or not os.path.exists(configfilename):
	 configfilename = "./etc" + os.sep + "spade.xml"
	 configfilename = os.path.abspath(configfilename)
	 jabberxml = "./etc" + os.sep + "xmppd.xml"
	 jabberxml = os.path.abspath(jabberxml)

  try:
  	for opt, arg in getopt(sys.argv[1:],
                         "hvdgc:j:", ["help", "version", "debug", "gui", "configfile=",
                                      "jabber="])[0]:
    		if opt in ["-h", "--help"]: print_help()
    		elif opt in ["-v", "--version"]: print_version()
    		elif opt in ["-c", "--configfile"]: configfilename = arg
    		elif opt in ["-j", "--jabber"]: jabberxml = arg
    		elif opt in ["-g", "--gui"]: gui = True
    		elif opt in ["-d", "--debug"]: dbg = ['always']
  except:
	pass

  print "SPADE", VERSION, "<jpalanca@dsic.upv.es> - http://magentix.gti-ia.dsic.upv.es/"

  try:
  	import psyco
	print "Using Psyco optimizing compiler."
	#psyco.log(logfile='/tmp/psyco.log')
	psyco.full()
	#psyco.profile()
  except ImportError: print "W: Psyco optimizing compiler not found."

  print "Using config file " + str(configfilename)
  print "Using jabber file " + str(jabberxml)
  sys.stdout.write("Starting SPADE")
  sys.stdout.flush()

  #parser = SpadeConfigParser.ConfigParser()
  #config = parser.parse(configfilename)

  sys.stdout.write(".")
  sys.stdout.flush()

  jabberxml =  os.path.abspath(jabberxml)
  #s = xmppd.xmppd.Server(cfgfile=jabberxml, debug = dbg)
  os.chdir("xmppd")
  #s = xmppd.Server(cfgfile=jabberxml, cmd_options={'enable_debug':dbg, 'enable_psyco':True})
  s = Server(cfgfile=jabberxml, cmd_options={'enable_debug':dbg, 'enable_psyco':True})
  #s = xmppd.Server(cfgfile=jabberxml)
  os.chdir("..")
  """
  for filter in s.router_filters:
  	if isinstance(filter, acc.ACC):
		filter.loadConfig(configfilename)
  """
  sys.stdout.write(".")
  sys.stdout.flush()

  thread.start_new_thread(s.run,tuple())

  try:
	sys.stdout.write(".")
  	sys.stdout.flush()
  	platform = spade_backend.SpadeBackend(configfilename)
	sys.stdout.write(".")
  	sys.stdout.flush()
	platform.start()
	sys.stdout.write(".")
  	sys.stdout.flush()

	#if gui:
	#	os.spawnl(os.P_NOWAIT, "spade-rma.py", "spade-rma.py")
	sys.stdout.write(".")
  	sys.stdout.flush()

  	thread.start_new_thread(launchtg, tuple([platform]))

  except Exception,e:
	print str(e)
	print colors.color_red + " [failed]" + colors.color_none
	platform.shutdown()
 	s.shutdown("Jabber server terminated...")
	raise SystemExit

  print colors.color_green + " [done]" + colors.color_none


  alive=True
  while alive:
	  try:
		time.sleep(1)
		if not platform.alive:
			#The platform died (probable restart). Let's start it over
			platform.shutdown()
			print colors.color_green + "SPADE Platform restarting..." + colors.color_none
			platform.start()
			print colors.color_green + " [done]" + colors.color_none
	  except KeyboardInterrupt:
		sys.stdout.write("Exiting")
		sys.stdout.flush()
		platform.shutdown()
		sys.stdout.write(".")
		sys.stdout.flush()
		s.shutdown("SPADE Jabber server terminated...")
		sys.stdout.write(".")
		sys.stdout.flush()
		time.sleep(1)
		sys.stdout.write(".")
		sys.stdout.flush()
		print colors.color_green + " Bye." + colors.color_none
		alive=False
		#sys.exit(0)
  sys.exit(0)
  raise SystemExit

if __name__ == '__main__': main()

