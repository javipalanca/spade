#! python

#import sys
#import SocketServer
from string import *

from xml.sax import ContentHandler
from xml.sax import parseString
from xml.sax import make_parser
from xml.sax.handler import *

# jabber.xml template
jabber_template = """
<jabber>

  <service id="sessions">

    <host><jabberd:cmdline flag="h">$SERVERNAME$</jabberd:cmdline></host>

    <jsm xmlns="jabber:config:jsm">

      <vCard>
        <FN>SPADE Server</FN>
        <DESC>A SPADE Server!</DESC>
        <URL>http://$SERVERNAME$</URL>
      </vCard>
      
      <register notify="yes">
        <instructions>Choose a username and password to register with this server.</instructions>
        <name/>
      </register>
     
      <welcome xml:lang='en'>
        <subject>Welcome!</subject>
        <body>Welcome to the SPADE server at $SERVERNAME$ -- we hope you enjoy this service! For information about how to use SPADE, visit http://magentix.gti-ia.dsic.upv.es</body>
      </welcome>
       <welcome xml:lang='es'>
        <subject>Bienvenido!</subject>
        <body>Bienvenido al servidor SPADE en $SERVERNAME$ -- esperamos que disfrute del servicio. Para mas informacion, consulte http://magentix.gti-ia.dsic.upv.es</body>
      </welcome>
     
      <vcard2jud/>
     
      <browse>
        
	<service jid="acc.$ACCSERVERNAME$" name="SmartPython Multi Agent Development Environment">
        </service>
        <service jid="ams.$AMSSERVERNAME$" name="SPADE ams FIPA Agent">
          <ns>jabber:iq:search</ns>
        </service>
        <service jid="df.$DFSERVERNAME$" name="SPADE df FIPA Agent">
          <ns>jabber:iq:search</ns>
        </service>

      </browse>

      <disco>
        <identity category='services' type='jabber' name='Jabber 1.4 Server'/>
        <feature var='jabber:iq:browse'/>
        <feature var='jabber:iq:agents'/>
        <feature var='jabber:iq:register'/>
        <feature var='jabber:iq:time'/>
        <feature var='jabber:iq:last'/>
        <feature var='jabber:iq:version'/>
      </disco>

      <mod_auth_crypt>
        <hash>SHA1</hash>
      </mod_auth_crypt>

      <presence>
      </presence>

    </jsm>

    <load main="jsm">
      <jsm>$LIBPATH$libjabberdsm.so</jsm>
      <mod_stat>$LIBPATH$libjabberdsm.so</mod_stat>
      <mod_echo>$LIBPATH$libjabberdsm.so</mod_echo>
      <mod_roster>$LIBPATH$libjabberdsm.so</mod_roster>
      <mod_time>$LIBPATH$libjabberdsm.so</mod_time>
      <mod_vcard>$LIBPATH$libjabberdsm.so</mod_vcard>
      <mod_last>$LIBPATH$libjabberdsm.so</mod_last>
      <mod_version>$LIBPATH$libjabberdsm.so</mod_version>
      <mod_announce>$LIBPATH$libjabberdsm.so</mod_announce>
      <mod_agents>$LIBPATH$libjabberdsm.so</mod_agents>
      <mod_browse>$LIBPATH$libjabberdsm.so</mod_browse>
      <mod_disco>$LIBPATH$libjabberdsm.so</mod_disco>
      <mod_admin>$LIBPATH$libjabberdsm.so</mod_admin>
      <mod_offline>$LIBPATH$libjabberdsm.so</mod_offline>
      <mod_presence>$LIBPATH$libjabberdsm.so</mod_presence>
      <mod_auth_digest>$LIBPATH$libjabberdsm.so</mod_auth_digest>
      <mod_auth_plain>$LIBPATH$libjabberdsm.so</mod_auth_plain>    
      <mod_log>$LIBPATH$libjabberdsm.so</mod_log>
      
      $REGISTER$
      
      <!--<mod_register>$LIBPATH$libjabberdsm.so</mod_register>-->
      
      <mod_xml>$LIBPATH$libjabberdsm.so</mod_xml>
    </load>

  </service>

  <xdb id="xdb">
    <host/>
    
    <ns/>
    
    <load>
      <xdb_file>$LIBPATH$libjabberdxdbfile.so</xdb_file>
    </load>
    <xdb_file xmlns="jabber:config:xdb_file">
      <spool><jabberd:cmdline flag='s'>$WORKPATH$</jabberd:cmdline></spool>
      <timeout>3600</timeout>
      <sizelimit>500000</sizelimit>
    </xdb_file>
  </xdb>

  <service id="c2s">
    <load>
      <pthsock_client>$LIBPATH$libjabberdpthsock.so</pthsock_client>
    </load>
    <pthcsock xmlns='jabber:config:pth-csock'>
      <authtime>120</authtime>
      <heartbeat>60</heartbeat>
      <ip port="5222"/>

    </pthcsock>
  </service>

  <log id='elogger'>
    <host/>
    <logtype/>

    <format>%d: [%t] (%h): %s</format>
    <file>$WORKPATH$error.log</file>
    <stderr/>
    
    <!--<format>[%t] (%h): %s</format>
    <syslog>local0</syslog>-->
    
  </log>

  <service id="dnsrv">
    <host/>
    <load>
      <dnsrv>$LIBPATH$libjabberddnsrv.so</dnsrv>
    </load>
    <dnsrv xmlns="jabber:config:dnsrv">

    	<resend service="_xmpp-server._tcp">s2s</resend>
    	<resend service="_jabber._tcp">s2s</resend>
    	<resend>s2s</resend>
    </dnsrv>
  </service>


  <service id="s2s">
    <load>
      <dialback>$LIBPATH$libjabberddialback.so</dialback>
    </load>
    <dialback xmlns='jabber:config:dialback'>
      <ip port="5269"/>
      <karma>
        <init>50</init>
        <max>50</max>
        <inc>4</inc>
        <dec>1</dec>
        <penalty>-5</penalty>
        <restore>50</restore>
      </karma>
    </dialback>
  </service>


 <service id="acc.$ACCSERVERNAME$">
    <accept>
      <ip/>
      <port>$ACCPORT$</port>
      <secret>$ACCPASSWORD$</secret>
    </accept>
  </service>
  <service id="ams.$AMSSERVERNAME$">
    <accept>
      <ip/>
      <port>$AMSPORT$</port>
      <secret>$AMSPASSWORD$</secret>
    </accept>
  </service>
  <service id="df.$DFSERVERNAME$">
    <accept>
      <ip/>
      <port>$DFPORT$</port>
      <secret>$DFPASSWORD$</secret>
    </accept>
  </service>




  <service id="update.jabber.org">
    <host>update.jabber.org</host>
    <null/>
  </service>

  <io>

    <rate points="5" time="25"/>

    <streamconf>
      <default type='s2s'>
        <stream-from/>
      </default>
    </streamconf>


  </io>

  <debug>
      <mask>0</mask>

  </debug>

  <pidfile>$WORKPATH$jabber.pid</pidfile>

</jabber>
"""


spade = dict()
domain = dict()
acc = dict()
ams = dict()
df = dict()
jabber = dict()

class spadeXML:
	'''Analizador de cadenas XML especificamente configurado
	para el SPADE'''
	def __init__(self):
		self.ch = spadeXMLHandler()
	
	def parseString(self, xmlstream, tag_attr, chars):
		self.ch.tag_attr = tag_attr
		parseString(xmlstream, self.ch)
		return self.ch.tag_name, self.ch.message


class spadeXMLHandler(ContentHandler):
	def __init__(self):
		self.chars = ""
		self.message = ""
		self.current_tag = ""
		pass
		
	def startElement(self, name, attrs):
		'''Llamado cuando empieza un nodo XML en el flujo'''
		self.chars = ""
		self.tag_name = name
		if name == "domain":
			self.current_tag = "domain"
			#print "Current Tag: " + name
		if name == "acc":
			self.current_tag = "acc"
			#print "Current Tag: " + name
		if name == "ams":
			self.current_tag = "ams"
			#print "Current Tag: " + name
		if name == "df":
			self.current_tag = "df"
			#print "Current Tag: " + name
		if name == "jabber":
			self.current_tag = "jabber"
			#print "Current Tag: " + name
		
		if name == "connection":
			self.tag_attr["type"] = attrs.get("type", None)
			self.tag_attr['name'] = attrs.get('name', None)
			self.tag_attr['version'] = attrs.get('version', None)
			self.tag_attr['handle'] = attrs.get('handle', None)
			self.tag_attr['options'] = attrs.get('options', None)
			self.tag_attr['port'] = attrs.get('port', None)
		elif name == "database":
			self.tag_attr['size'] = attrs.get('size', None)
		elif name == "search":
			self.tag_attr['id'] = attrs.get('id', None)
			self.tag_attr['handle'] = attrs.get('handle', None)
		elif name == "keepalive":
			self.tag_attr['id'] = attrs.get('id', None)
			self.tag_attr['handle'] = attrs.get('handle', None)
		else:
			self.chars = ""
			self.tag_name = name

	def characters(self, ch):
		'''Caracteres incluidos en un nodo'''
		self.chars = str(self.chars + ch)
		
	def endElement(self, name):
		'''Llamado al finalizar un nodo'''
		#print 'Final de: ' + name + ' con current_tag: ' + self.current_tag
		#print 'Caracteres : ' + self.chars
		if name == "hostname":
			if self.current_tag == "domain":
				domain['hostname'] = self.chars
				#print 'Acaba ' + name + ' con caracteres ' + self.chars
			elif self.current_tag == "acc":
				acc['hostname'] = self.chars
				#print 'Acaba ' + name + ' con caracteres ' + self.chars
			elif self.current_tag == "ams":
				ams['hostname'] = self.chars
			elif self.current_tag == "df":
				df['hostname'] = self.chars
		if name == "password":
			if self.current_tag == "domain":
				domain['password'] = self.chars
			elif self.current_tag == "acc":
				acc['password'] = self.chars
			elif self.current_tag == "ams":
				ams['password'] = self.chars
			elif self.current_tag == "df":
				df['password'] = self.chars
		if name == "port":
			if self.current_tag == "domain":
				domain['port'] = self.chars
			elif self.current_tag == "acc":
				acc['port'] = self.chars
			elif self.current_tag == "ams":
				ams['port'] = self.chars
			elif self.current_tag == "df":
				df['port'] = self.chars
		if name == "binpath":
			jabber['binpath'] = self.chars
		if name == "libpath":
			jabber['libpath'] = self.chars
		if name == "workpath":
			jabber['workpath'] = self.chars
		if name == "allowregister":
			jabber['allowregister'] = self.chars
		self.message = self.chars
		pass


def generateCode(fn):
	# Fill the template with the correct data
	
	global jabber_template
	
	if jabber['allowregister'] == 'yes':
		jabber_template = jabber_template.replace('$REGISTER$', '<mod_register>$LIBPATH$libjabberdsm.so</mod_register>')
	else:
		jabber_template = jabber_template.replace('$REGISTER$', '')
	jabber_template = jabber_template.replace('$SERVERNAME$', domain['hostname'])
	jabber_template = jabber_template.replace('$ACCSERVERNAME$', acc['hostname'])
	jabber_template = jabber_template.replace('$ACCPORT$', acc['port'])
	jabber_template = jabber_template.replace('$ACCPASSWORD$', acc['password'])
	jabber_template = jabber_template.replace('$AMSSERVERNAME$', ams['hostname'])
	jabber_template = jabber_template.replace('$AMSPORT$', ams['port'])
	jabber_template = jabber_template.replace('$AMSPASSWORD$', ams['password'])
	jabber_template = jabber_template.replace('$DFSERVERNAME$', df['hostname'])
	jabber_template = jabber_template.replace('$DFPORT$', df['port'])
	jabber_template = jabber_template.replace('$DFPASSWORD$', df['password'])
	jabber_template = jabber_template.replace('$WORKPATH$', jabber['workpath'])
	jabber_template = jabber_template.replace('$LIBPATH$', jabber['libpath'])

	file = open(fn, "w+")
	file.write(jabber_template)
	file.close()



if __name__ == '__main__':
    # Create the handler
    #dh = sbConnection("initial", '1.0')
    
    #parseString(datosSB, dh)

    # Create a parser
    parser = make_parser()

    # Tell the parser we are not interested in XML namespaces
    parser.setFeature(feature_namespaces, 0)

    # Create the handler
    dh = spadeXMLHandler()

    # Tell the parser to use our handler
    parser.setContentHandler(dh)

    # Parse the input
    parser.parse("spade.ini.xml")

    # Manage the results
    spade['domain'] = domain
    spade['acc'] = acc
    spade['ams'] = ams
    spade['df'] = df
    spade['jabber'] = jabber
    print spade

    generateCode('generated-jabber.xml')

