from basicTestCase import *
from amsTestCase   import *
from dfTestCase    import *
from coTestCase    import *
from p2pTestCase   import *
from rpcTestCase   import *
from aidTestCase   import *
from dadTestCase   import *
from eventbehavTestCase import *
from pubsubTestCase import *

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
