#!/usr/bin/env python


import os #, signal
import sys
import traceback
import time
import thread
from os.path import *

from getopt import getopt
try:
	from spade import spade_backend
#	from spade import SpadeConfigParser
	from spade import colors
	#from xmppd.filters import acc
except ImportError, e:
	print "Could not import spade package!!! " + str(e)
	#from libspade import spade_backend
	#from libspade import SpadeConfigParser
	#from libspade import colors

from xmppd.xmppd import Server



__author__    = "Gustavo Aranda <garanda@dsic.upv.es> and Javier Palanca <jpalanca@dsic.upv.es>"
__version__   = "2.0-RC4"
__copyright__ = "Copyright (C) 2010"
__license__   = "GPL"


def print_help():
  print
  print "Usage: %s [options]" % sys.argv[0]
  print " -h, --help         display this help text and exit"
  print " -v, --version      display the version and exit"
  print " -d, --debug        enable the debug execution"
  print " -c, --configfile   load the configuration file (default /etc/spade/spade.xml)"
  print " -j, --jabber       load the jabber configuration file (default /usr/share/spade/jabberd/jabber.xml)"
  #print " -w, --web          load the TurboGears(tm) web interface"
  raise SystemExit

def print_version():
  print "SPADE %s by Javier Palanca, Gustavo Aranda, Miguel Escriva, Natalia Criado and others" % colors.color_yellow + __version__ + colors.color_none
  print "gusarba@gmail.com - http://spade2.googleprojects.com"
  raise SystemExit

# Actually start the program running.
def main():

  gui = False
  web = False
  if len(sys.argv) < 2: pass
  elif sys.argv[1] in ["--help", "-h"]: print_help()
  elif sys.argv[1] in ["--version", "-v"]: print_version()
  elif sys.argv[1] in ["--gui", "-g"]: gui = True
  #elif sys.argv[1] in ["--web", "-w"]: web = True


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
                         "hvdgwc:j:", ["help", "version", "debug", "gui", "web", "configfile=",
                                      "jabber="])[0]:
    		if opt in ["-h", "--help"]: print_help()
    		elif opt in ["-v", "--version"]: print_version()
    		elif opt in ["-c", "--configfile"]: configfilename = arg
    		elif opt in ["-j", "--jabber"]: jabberxml = arg
    		elif opt in ["-g", "--gui"]: gui = True
    		#elif opt in ["-w", "--web"]: web = True
    		elif opt in ["-d", "--debug"]: dbg = ['always']
  except:
	pass

  print "SPADE ", colors.color_yellow + __version__ + colors.color_none, " <gusarba@gmail.com> - http://spade2.googleprojects.com"

  try:
  	import psyco
	psyco.full()
	#print "Using Psyco optimizing compiler."
	#psyco.log(logfile='/tmp/psyco.log')
	#psyco.profile()
  except ImportError: print "W: Psyco optimizing compiler not found."

  #print "Using config file " + str(configfilename)
  #print "Using jabber file " + str(jabberxml)
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
  #s = Server(cfgfile=jabberxml, cmd_options={'enable_debug':dbg, 'enable_psyco':True})
  s = Server(cfgfile=jabberxml, cmd_options={'enable_debug':dbg, 'enable_psyco':False})
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
  	s.DEBUG = platform.DEBUG

	sys.stdout.write(".")
  	sys.stdout.flush()


  except Exception,e:
    _exception = sys.exc_info()
    if _exception[0]:
        print '\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
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

