#!/usr/bin/env python

import os, signal
import sys
import time
import thread
import ConfigParser
from optparse import OptionParser

from getopt import getopt
from spade import spade_backend
from spade import SpadeConfigParser
from spade.xmppd import Server
#import spade

VERSION = "1.9.3"


def print_help():
  print
  print "Usage: %s [options]" % sys.argv[0]
  print " -h, --help         display this help text and exit"
  print " -v, --version      display the version and exit"
  print " -c, --configfile   load the configuration file (default /etc/spade/spade.xml)"
  print " -j, --jabber       load the jabber configuration file (default /usr/share/spade/jabberd/jabber.xml)"
  raise SystemExit

def print_version():
  print "SPADE %s by Javi Palanca, Gustavo Aranda, Miguel Escriva and others" % VERSION
  print "jpalanca@dsic.upv.es - http://magentix.gti-ia.dsic.upv.es/"
  raise SystemExit

# Actually start the program running.
def main():
  global gui
  print "SPADE", VERSION, "<jpalanca@dsic.upv.es> - http://magentix.gti-ia.dsic.upv.es/"
  
  try:
  	import psyco
	print "Psyco optimizing compiler found. Using psyco.full()."
	psyco.full()
  except ImportError: print "W: Psyco optimizing compiler not found."
  
  gui = False
  if len(sys.argv) < 2: pass 
  elif sys.argv[1] in ["--help", "-h"]: print_help()
  elif sys.argv[1] in ["--version", "-v"]: print_version()
  elif sys.argv[1] in ["--gui", "-g"]: gui = True

  """
  parser = OptionParser()

  parser.add_option("-c", "--config", dest="config", help="load the configuration file (default /etc/spade/spade.xml)")
  parser.add_option("-j", "--jabber", dest="jabber", help="load the jabber configuration file (default /usr/share/spade/jabberd/jabber.xml)")
  parser.add_option("-v", "--version", action="store_true", dest="version", help="display the version and exit")
  parser.add_option("-g", "--gui", action="store_true", dest="gui", help="run the SPADE RMA")

  """

  configfilename = "/etc/spade/spade.xml"
  jabberxml = "/etc/spade/xmppd.xml"

  if os.name != "posix" or not os.path.exists(jabberxml) or not os.path.exists(configfilename):
	 configfilename = "./etc" + os.sep + "spade.xml"
	 jabberxml = "./etc" + os.sep + "jabber.xml"
	

  for opt, arg in getopt(sys.argv[1:],
                         "hvgc:j:", ["help", "version", "gui", "configfile=",
                                      "jabber="])[0]:
    if opt in ["-h", "--help"]: print_help()
    elif opt in ["-v", "--version"]: print_version()
    elif opt in ["-c", "--configfile"]: configfilename = arg
    elif opt in ["-j", "--jabber"]: jabberxml = arg
    elif opt in ["-g", "--gui"]: gui = True


  configfile = SpadeConfigParser.ConfigParser(configfilename)

  #workpath = "/usr/share/spade/jabberd/" #configfile.get("jabber","workpath")
  #if not os.path.exists(workpath):
  #	workpath = "./usr/share/spade/jabberd/"

  #if os.name == "posix":
  #	  jabberpath = workpath + "jabberd"
  #	  spool = os.environ['HOME'] + "/.spade"
  #	  if not os.path.exists(spool):
  #		os.mkdir(spool)
  #else:
  #	  jabberpath = workpath + "jabberd.exe"
  #	  spool = workpath + "spool"

  #if os.path.exists(jabberpath): # and os.path.exists(jabberxml):
	#print "JABBERPATH: " + jabberpath
	#print "JABBERXML: "+ jabberxml
	####jabberpid = os.spawnl(os.P_NOWAIT, jabberpath, jabberpath, '-c', str(jabberxml), '-H', str(workpath), '-s', str(spool))
	#print "PID: " + str(jabberpid)
  #	pass

  server = spade.xmppd.Server(jabberxml)
  thread.start_new_thread(server.run,tuple())

  try:
  	#print "Esperando...."
  	#time.sleep(2)
  	#print "Lanzando..."

  	platform = spade_backend.SpadeBackend(configfilename)
	platform.start()

	if gui:
		os.spawnl(os.P_NOWAIT, "spade-rma.py", "spade-rma.py")

	while True:
		time.sleep(1)
  except KeyboardInterrupt:
    server.shutdown()
    pass
 
  del platform

  #if os.name == "posix":
  #	######os.kill(jabberpid, signal.SIGTERM)
  #	time.sleep(2)

  print "Jabber server terminated..."

if __name__ == '__main__': main()

