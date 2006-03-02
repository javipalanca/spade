#!/usr/bin/env python

import os, signal
import sys
import time
import thread

from getopt import getopt
from spade import spade_backend
from spade import SpadeConfigParser
from spade import colors
import xmppd

VERSION = "1.9.7"


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
  print "jpalanca@dsic.upv.es - http://magentix.gti-ia.dsic.upv.es/"
  raise SystemExit

# Actually start the program running.
def main():

  print "SPADE", VERSION, "<jpalanca@dsic.upv.es> - http://magentix.gti-ia.dsic.upv.es/"
  
  try:
  	import psyco
	print "Using Psyco optimizing compiler."
	#psyco.log(logfile='/tmp/psyco.log')
	psyco.full()
	#psyco.profile()
  except ImportError: print "W: Psyco optimizing compiler not found."
  
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
	 jabberxml = "./etc" + os.sep + "jabber.xml"
	
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

  sys.stdout.write("Launching SPADE")

  configfile = SpadeConfigParser.ConfigParser(configfilename)

  sys.stdout.write(".")

  s = xmppd.server.Server(cfgfile=jabberxml, debug = dbg)

  sys.stdout.write(".")

  thread.start_new_thread(s.run,tuple())

  try:
	sys.stdout.write(".")
  	platform = spade_backend.SpadeBackend(configfilename)
	sys.stdout.write(".")
	platform.start()
	sys.stdout.write(".")

	if gui:
		os.spawnl(os.P_NOWAIT, "spade-rma.py", "spade-rma.py")
	sys.stdout.write(".")

  except:
	print colors.color_red + " [failed]" + colors.color_none
	del platform
 	s.shutdown("Jabber server terminated...")
	
  print colors.color_green + " [done]" + colors.color_none


  while True:
	  try:
		time.sleep(1)
	  except KeyboardInterrupt:
		del platform
		s.shutdown("Jabber server terminated...")
		sys.exit(0)

  
  #del platform
  #s.shutdown("Jabber server terminated...")
  #sys.exit(0)

if __name__ == '__main__': main()

