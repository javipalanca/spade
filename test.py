from test.basicTestCase import *
from test.amsTestCase   import *
from test.dfTestCase    import *
from test.coTestCase    import *
from test.p2pTestCase   import *
from test.rpcTestCase   import *
from test.aidTestCase   import *
from test.dadTestCase   import *
from test.eventbehavTestCase import *
from test.pubsubTestCase import *
from test.kbTestCase import *

from spade import spade_backend
from xmppd.xmppd import Server
import thread

import os
d="test"+os.sep

s = Server(cfgfile=d+"unittests_xmppd.xml", cmd_options={'enable_debug':[], 'enable_psyco':False})
thread.start_new_thread(s.run,tuple())

platform = spade_backend.SpadeBackend(d+"unittests_spade.xml")
platform.start()



try:
	import xmlrunner
	use_xmlrunner = True
except:
	use_xmlrunner = False

if use_xmlrunner:
	unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
else:
	print "XMLTestRunner not found."
	unittest.main()

platform.shutdown()
s.shutdown("Jabber server terminated...")

