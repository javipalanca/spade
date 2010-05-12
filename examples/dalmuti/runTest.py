###########################
#   Dalmuti               #
###########################
'''
This example sets up a game of Dalmuti.
It runs a game manager and 5 players.
Note: It's in spanish!
'''

import random
from gameManager import *
import jugador

host = "127.0.0.1"

N = 5
R = 1

ag = gameManager("dalmuti@"+host, "ElGranDalmuti")
ag.start()
ag.setOptions( N, R )

players = []

for j in range(N):
    p = jugador.jugador("player"+str(j)+"@"+host, "secret")
    p.start()
    players.append(p)
    print "Added player "+ str(j)


alive =True
while alive:
	try:
	    time.sleep(1)
	except KeyboardInterrupt:
	    alive=False
ag.stop()
for b in players:
    b.stop()
        
import sys
sys.exit(0)

