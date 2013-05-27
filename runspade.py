#!/usr/bin/env python


import os
import signal
import sys
import traceback
import time
import thread
from os.path import *

from getopt import getopt
try:
    from spade import spade_backend
    from spade import colors
except ImportError, e:
    print "Could not import spade package!!! " + str(e)

from xmppd.xmppd import Server

__author__ = "Gustavo Aranda <gusarba@gmail.com> and Javier Palanca <jpalanca@gmail.com>"
__version__ = "2.2"
__copyright__ = "Copyright (C) 2006-2012"
__license__ = "LGPL"


def print_help():
    configfilename = "/etc/spade/spade.xml"
    jabberxml = "/etc/spade/xmppd.xml"
    if sys.platform[:6] == 'netbsd':
        configfilename = os.sep + "usr" + os.sep + "pkg" + configfilename
        jabberxml = os.sep + "usr" + os.sep + "pkg" + jabberxml
    print
    print "Usage: %s [options]" % sys.argv[0]
    print " -h, --help         display this help text and exit"
    print " -v, --version      display the version and exit"
    print " -d, --debug        enable the debug execution"
    print " -c, --configfile   load the configuration file (use configure.py to create one)"
    print " -j, --jabber       load the jabber configuration file (use configure.py to create one)"
    #print " -w, --web          load the web interface"
    raise SystemExit


def print_version():
    print "SPADE " + colors.color_yellow + __version__ + colors.color_none + " by Javier Palanca, Gustavo Aranda, Miguel Escriva and others"
    print "gusarba@gmail.com - http://spade2.googlecode.com"
    raise SystemExit

# Actually start the program running.


def main():
    configfilename = "/etc/spade/spade.xml"
    jabberxml = "/etc/spade/xmppd.xml"
    if sys.platform[:6] == 'netbsd':
        configfilename = os.sep + "usr" + os.sep + "pkg" + configfilename
        jabberxml = os.sep + "usr" + os.sep + "pkg" + jabberxml

    web = False
    if len(sys.argv) < 2:
        pass
    elif sys.argv[1] in ["--help", "-h"]:
        print_help()
    elif sys.argv[1] in ["--version", "-v"]:
        print_version()
    #elif sys.argv[1] in ["--web", "-w"]: web = True

    dbg = []

    if os.name != "posix" or not os.path.exists(jabberxml) or not os.path.exists(configfilename):
        configfilename = "spade.xml"
        configfilename = os.path.abspath(configfilename)
        jabberxml = "xmppd.xml"
        jabberxml = os.path.abspath(jabberxml)

    try:
        for opt, arg in getopt(sys.argv[1:],
                               "hvdwc:j:", ["help", "version", "debug", "web", "configfile=", "jabber="])[0]:
            if opt in ["-h", "--help"]:
                print_help()
            elif opt in ["-v", "--version"]:
                print_version()
            elif opt in ["-c", "--configfile"]:
                configfilename = arg
            elif opt in ["-j", "--jabber"]:
                jabberxml = arg
            #elif opt in ["-w", "--web"]: web = True
            elif opt in ["-d", "--debug"]:
                dbg = ['always']
    except:
        pass

    print "SPADE ", colors.color_yellow + __version__ + colors.color_none, " <gusarba@gmail.com> - http://spade2.googlecode.com"

    try:
        import psyco
        psyco.full()
        #psyco.profile()
    except ImportError:
        pass  # print "W: Psyco optimizing compiler not found."

    sys.stdout.write("Starting SPADE")
    sys.stdout.flush()
    sys.stdout.write(".")
    sys.stdout.flush()

    jabberxml = os.path.abspath(jabberxml)
    if not os.path.exists(jabberxml):
        print '\n There is no jabber config file (xmppd.xml)' + colors.color_red + " [failed]" + colors.color_none
        print_help()
        raise SystemExit

    if sys.platform[:6] == 'netbsd':
        pyvers = 'python' + str(numb)
        path = "/usr/pkg/lib" + os.sep + pyvers + "/site-packages/xmppd/"
        os.chdir(path)
    else:
        pass  # os.chdir("xmppd")

    s = Server(cfgfile=jabberxml, cmd_options={'enable_debug': dbg,
               'enable_psyco': False})
    sys.stdout.write(".")
    sys.stdout.flush()

    thread.start_new_thread(s.run, tuple())

    try:
        sys.stdout.write(".")
        sys.stdout.flush()
        if not os.path.exists(configfilename):
            print '\n There is no SPADE config file (spade.xml)' + colors.color_red + " [failed]" + colors.color_none
            print_help()
            raise SystemExit

	if dbg==['always']:
            platform = spade_backend.SpadeBackend(s, configfilename, debug=True)
	else:
            platform = spade_backend.SpadeBackend(s, configfilename)
        sys.stdout.write(".")
        sys.stdout.flush()
        platform.start()
        sys.stdout.write(".")
        sys.stdout.flush()
        s.DEBUG = platform.DEBUG

        sys.stdout.write(".")
        sys.stdout.flush()

    except Exception, e:
        _exception = sys.exc_info()
        if _exception[0]:
            print '\n' + ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
            print str(e)
            print colors.color_red + " [failed]" + colors.color_none
            platform.shutdown()
            s.shutdown("Jabber server terminated...")
            raise SystemExit

    print colors.color_green + " [done]" + colors.color_none
    if platform.acc.wui:
        print "\n " + colors.color_yellow + " [info] " + colors.color_none + "WebUserInterface serving at port " + str(platform.acc.wui.port) + "\n "

    alive = True
    while alive:
        try:
            time.sleep(1)
            if not platform.alive:
                #The platform died (probable restart). Let's start it over
                platform.shutdown()
                print "\n " + colors.color_green + "SPADE Platform restarting..." + colors.color_none
                platform.start()
                print colors.color_green + " [done]" + colors.color_none
        except KeyboardInterrupt:
            alive = False

    sys.stdout.write("Exiting")
    sys.stdout.flush()
    platform.shutdown()
    sys.stdout.write(".")
    sys.stdout.flush()
    s.shutdown("SPADE Jabber server terminated...")
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(1)
    del s
    sys.stdout.write(".")
    sys.stdout.flush()
    print colors.color_green + " Bye." + colors.color_none
    #raise SystemExit
    sys.exit(0)

if __name__ == '__main__':
    main()
