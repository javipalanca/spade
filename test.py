from test.aidTestCase import *
from test.amsTestCase import *
from test.basicTestCase import *
from test.bdiTestCase import *
from test.coTestCase import *
from test.dadTestCase import *
from test.dfTestCase import *
from test.eventbehavTestCase import *
from test.factsTestCase import *
from test.httpTestCase import *
from test.jsonTestCase import *
from test.kbTestCase import *
from test.p2pTestCase import *
from test.pubsubTestCase import *
from test.rpcTestCase import *
from test.socialTestCase import *
from test.tbcbpTestCase import *
from test.templateTestCase import *
from test.xfTestCase import *

from spade import spade_backend
from xmppd.xmppd import Server
import thread
import sys
import os

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "coverage":
        use_xmlrunner= True
        del sys.argv[1]
    else:
        use_xmlrunner = False

    d = "test" + os.sep
    dbg = ['always']
    s = Server(cfgfile=d + "unittests_xmppd.xml")
    #       , cmd_options={'enable_debug':dbg, 'enable_psyco':False})

    thread.start_new_thread(s.run, tuple())

    platform = spade_backend.SpadeBackend(s, d + "unittests_spade.xml")
    platform.start()

    try:
        import xmlrunner
    except:
        print "XMLTestRunner not found."
        use_xmlrunner = False

    if use_xmlrunner:
        p = unittest.main(testRunner=xmlrunner.XMLTestRunner(
            output='test-reports'), exit=False)
    else:
        p = unittest.main(exit=False)

    platform.shutdown()
    s.shutdown("Jabber server terminated...")

    if sys.platform == 'win32':
        os._exit(len(p.result.failures))
    else:
        sys.exit(len(p.result.failures))
