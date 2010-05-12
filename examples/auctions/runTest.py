###########################
#   Auction               #
###########################
'''
This example sets up an auction.
This auction comprises one auctioner and 10 bidders.
The bidders can make coalitions in order to win the most expensive auction.
All the interaction with the example is done via web.
'''

import random
from auctioner import *
from bidder import *

host = "127.0.0.1"

agent = "auctioner"+"@"+host
auctioner = Auctioner(agent,"secret")
auctioner.start()

print "Launched 1 auctioner on port 8010"


bidders = []

for nbidder in range(10):
    agent = "bidder"+str(nbidder)+"@"+host
    bidder = Bidder(agent,"secret")
    bidder.WEB_ADMIN_PORT = 9000+nbidder
    bidder.money = random.randint(1000,5000)
    bidders.append(bidder)
    bidder.start()
    print "Launched bidder "+str(nbidder)+ " on port "+str(bidder.WEB_ADMIN_PORT)

alive =True
while alive:
	try:
	    time.sleep(1)
	except KeyboardInterrupt:
	    alive=False
auctioner.stop()
for b in bidders:
    b.stop()
        
import sys
sys.exit(0)

