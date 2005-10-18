#!/usr/bin/env python

import os
import sys
import time
import ConfigParser
from spade-backend import *
from getopt import getopt

VERSION = "1.9b"

def print_help():
  print
  print "Usage: %s [options]" % sys.argv[0]
  print " -h, --help         display this help text and exit"
  print " -v, --version      display the version and exit"
  print " -c, --configfile   load the configuration file (default /etc/spade/spade.ini)"
  print " -j, --jabber       load the jabber configuration file (default /etc/spade/jabber.xml)"
  raise SystemExit

def print_version():
  print "SPADE %s by Javi Palanca, Gustavo Aranda, Miguel Escriva and others" % VERSION
  print "jpalanca@dsic.upv.es - http://magentix.gti-ia.dsic.upv.es/"
  raise SystemExit

if len(sys.argv) < 2: pass 
elif sys.argv[1] in ["--help", "-h"]: print_help()
elif sys.argv[1] in ["--version", "-v"]: print_version()


# Actually start the program running.
def main():
  print "SPADE", VERSION, "<jpalanca@dsic.upv.es> - http://magentix.gti-ia.dsic.upv.es/"
  """
  if mainconfig["usepsyco"]:
    try:
      import psyco
      print "Psyco optimizing compiler found. Using psyco.full()."
      psyco.full()
    except ImportError: print "W: Psyco optimizing compiler not found."
  """
  # default settings for play_and_quit.
  if os.name == "posix":
	 configfilename = "/etc/spade/spade.ini"
	 jabber = "/etc/spade/jabber.xml"
  else:
	 configfilename = "etc\spade.ini"
	 jabber = "etc\jabber.xml"
	

  for opt, arg in getopt(sys.argv[1:],
                         "hv:c:j:", ["help", "version", "configfile=",
                                      "jabber="])[0]:
    if opt in ["-h", "--help"]: print_help()
    elif opt in ["-v", "--version"]: print_version()
    elif opt in ["-c", "--configfile"]: configfilename = arg
    elif opt in ["-j", "--jabber"]: jabber = arg


  configfile = ConfigParser.ConfigParser()
  cffile = open(configfilename,'r')
  configfile.readfp(cffile)
  cffile.close()

  jabberpath = configfile.get("Jabber","path")
  if os.path.exists(jabberpath) and os.path.exists(jabber):
	os.system(str(jabberpath + "  -c " + jabber + " &"))

  time.sleep(2)

  #if os.path.exists("/usr/bin/spade-backend.py") and os.path.exists(configfilename):
  #	os.system(str( "/usr/bin/spade-backend.py " + configfilename))
  platform = SpadeBackend(configfilename)
  platform.start()

  print "OUCH!"

  """  
  for dir in mainconfig["songdir"].split(os.pathsep):
    print "Searching for songs in", dir
    song_list.extend(util.find(dir, ['*.dance', '*.dwi', '*.sm', '*/song.*']))
  for dir in mainconfig["coursedir"].split(os.pathsep):
    print "Searching for courses in", dir
    course_list.extend(util.find(dir, ['*.crs']))

  screen = set_display_mode()
  
  pygame.display.set_caption("pydance " + VERSION)
  pygame.mouse.set_visible(False)
  try:
    if os.path.exists("/usr/share/pixmaps/pydance.png"):
      icon = pygame.image.load("/usr/share/pixmaps/pydance.png")
    else: icon = pygame.image.load(os.path.join(pydance_path, "icon.png"))
    pygame.display.set_icon(icon)
  except: pass

  music.load(os.path.join(sound_path, "menu.ogg"))
  music.play(4, 0.0)

  songs = load_files(screen, song_list, "songs", SongItem, (False,))

  # Construct the song and record dictionaries for courses. These are
  # necessary because courses identify songs by title and mix, rather
  # than filename. The recordkey dictionary is needed for player's
  # picks courses.
  song_dict = {}
  record_dict = {}
  for song in songs:
    mix = song.info["mix"].lower()
    title = song.info["title"].lower()
    if song.info["subtitle"]: title += " " + song.info["subtitle"].lower()
    if not song_dict.has_key(mix): song_dict[mix] = {}
    song_dict[mix][title] = song
    record_dict[song.info["recordkey"]] = song

  crs = load_files(screen, course_list, "courses", courses.CourseFile,
                   (song_dict, record_dict))
  crs.extend(courses.make_players(song_dict, record_dict))
  records.verify(record_dict)

  # Let the GC clean these up if it needs to.
  song_list = None
  course_list = None
  record_dict = None
  pad.empty()

  if len(songs) < 1:
    ErrorMessage(screen,
                 ("You don't have any songs or step files. Check out "
                  "http://icculus.org/pyddr/get.php#songs "
                  "and download some free ones. "
                  "If you already have some, make sure they're in ") +
                 mainconfig["songdir"])
    raise SystemExit("You don't have any songs. Check http://icculus.org/pyddr/get.php#songs .")

  menudriver.do(screen, (songs, crs, screen))

  # Clean up shit.
  music.stop()
  pygame.quit()
  mainconfig.write(os.path.join(rc_path, "pydance.cfg"))
  # FIXME -- is this option a good idea?
  if mainconfig["saveinput"]: pad.write(os.path.join(rc_path, "input.cfg"))
  records.write()
 """
if __name__ == '__main__': main()
