#!/usr/bin/env python

#import sys
#import SocketServer
import string
import random
import os
import socket

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
        
	<service jid="acc.$SERVERNAME$" name="SmartPython Multi Agent Development Environment">
        </service>
        <service jid="ams.$SERVERNAME$" name="SPADE ams FIPA Agent">
          <ns>jabber:iq:search</ns>
        </service>
        <service jid="df.$SERVERNAME$" name="SPADE df FIPA Agent">
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
      <jsm>$LIBPATH$$JSM$</jsm>
      <mod_stat>$LIBPATH$$JSM$</mod_stat>
      <mod_echo>$LIBPATH$$JSM$</mod_echo>
      <mod_roster>$LIBPATH$$JSM$</mod_roster>
      <mod_time>$LIBPATH$$JSM$</mod_time>
      <mod_vcard>$LIBPATH$$JSM$</mod_vcard>
      <mod_last>$LIBPATH$$JSM$</mod_last>
      <mod_version>$LIBPATH$$JSM$</mod_version>
      <mod_announce>$LIBPATH$$JSM$</mod_announce>
      <mod_agents>$LIBPATH$$JSM$</mod_agents>
      <mod_browse>$LIBPATH$$JSM$</mod_browse>
      <mod_disco>$LIBPATH$$JSM$</mod_disco>
      <mod_admin>$LIBPATH$$JSM$</mod_admin>
      <mod_offline>$LIBPATH$$JSM$</mod_offline>
      <mod_presence>$LIBPATH$$JSM$</mod_presence>
      <mod_auth_digest>$LIBPATH$$JSM$</mod_auth_digest>
      <mod_auth_plain>$LIBPATH$$JSM$</mod_auth_plain>    
      <mod_log>$LIBPATH$$JSM$</mod_log>
      
      $REGISTER$
      
      <mod_xml>$LIBPATH$$JSM$</mod_xml>
    </load>

  </service>

  <xdb id="xdb">
    <host/>
    
    <ns/>
    
    <load>
      <xdb_file>$LIBPATH$$XDB$</xdb_file>
    </load>
    <xdb_file xmlns="jabber:config:xdb_file">
      <spool><jabberd:cmdline flag='s'>./spool</jabberd:cmdline></spool>
      <timeout>3600</timeout>
      <sizelimit>500000</sizelimit>
    </xdb_file>
  </xdb>

  <service id="c2s">
    <load>
      <pthsock_client>$LIBPATH$$PTH$</pthsock_client>
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
    <file>$ERRORLOG$</file>
    <stderr/>
   
    
    <!--<format>[%t] (%h): %s</format>
    <syslog>local0</syslog>-->
    
  </log>

  <service id="dnsrv">
    <host/>
    <load>
      <dnsrv>$LIBPATH$$DNSRV$</dnsrv>
    </load>
    <dnsrv xmlns="jabber:config:dnsrv">

    	<resend service="_xmpp-server._tcp">s2s</resend>
    	<resend service="_jabber._tcp">s2s</resend>
    	<resend>s2s</resend>
    </dnsrv>
  </service>


  <service id="s2s">
    <load>
      <dialback>$LIBPATH$$DIALBACK$</dialback>
    </load>
    <dialback xmlns='jabber:config:dialback'>
      <ip port="5269"/>
    </dialback>
  </service>


 <service id="acc.$SERVERNAME$">
    <accept>
      <ip/>
      <port>$ACCPORT$</port>
      <secret>$ACCPASSWORD$</secret>
    </accept>
  </service>
  <service id="ams.$SERVERNAME$">
    <accept>
      <ip/>
      <port>$AMSPORT$</port>
      <secret>$AMSPASSWORD$</secret>
    </accept>
  </service>
  <service id="df.$SERVERNAME$">
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

  <pidfile>./jabber.pid</pidfile>

</jabber>
"""


def generateCode():
	# Fill the template with the correct data
	
	global jabber_template

	libpath = "./libs/"

	if os.name == "posix":
		jsm = "libjabberdsm.so"
		dialback = "libjabberddialback.so"
		xdb = "libjabberdxdbfile.so"
		pth = "libjabberdpthsock.so"
		dnsrv = "libjabberddnsrv.so"
		#workpath = os.sep + "usr"+os.sep+"share"+os.sep+"spade"+os.sep+"jabberd"+os.sep
		hostname = socket.gethostname()
		errorlog = "/dev/null"

	else:
		jsm = "jsm.dll"
		dialback = "dialback.dll"
		xdb = "xdb_file.dll"
		pth = "pthsock_client.dll"
		dnsrv = "dnsrv.dll"
		#workpath = "./jabberd/"
		hostname = socket.gethostbyaddr(socket.gethostname())[0]
		errorlog = "./error.log"

	acc_passwd = "".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(8)])
	ams_passwd = "".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(8)])
	df_passwd = "".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(8)])

	
	#if jabber['allowregister'] == 'yes':
	jabber_template = jabber_template.replace('$REGISTER$', '<mod_register>$LIBPATH$$JSM$</mod_register>')
	#else:
	#	jabber_template = jabber_template.replace('$REGISTER$', '')
	jabber_template = jabber_template.replace('$SERVERNAME$', hostname)
	#jabber_template = jabber_template.replace('$ACCSERVERNAME$', "acc."+hostname)
	jabber_template = jabber_template.replace('$ACCPORT$', "9000")
	jabber_template = jabber_template.replace('$ACCPASSWORD$', acc_passwd)
	#jabber_template = jabber_template.replace('$AMSSERVERNAME$', 'ams.'+hostname)
	jabber_template = jabber_template.replace('$AMSPORT$', '9001')
	jabber_template = jabber_template.replace('$AMSPASSWORD$', ams_passwd)
	#jabber_template = jabber_template.replace('$DFSERVERNAME$', 'df.'+hostname)
	jabber_template = jabber_template.replace('$DFPORT$', '9002')
	jabber_template = jabber_template.replace('$DFPASSWORD$', df_passwd)
	#jabber_template = jabber_template.replace('$WORKPATH$', jabber['workpath'])
	jabber_template = jabber_template.replace('$LIBPATH$', libpath)
	jabber_template = jabber_template.replace('$JSM$', jsm)
	jabber_template = jabber_template.replace('$DIALBACK$', dialback)
	jabber_template = jabber_template.replace('$XDB$', xdb)
	jabber_template = jabber_template.replace('$PTH$', pth)
	jabber_template = jabber_template.replace('$DNSRV$', dnsrv)
	jabber_template = jabber_template.replace('$ERRORLOG$', errorlog)

	file = open("usr/share/spade/jabberd/jabber.xml", "w+")
	file.write(jabber_template)
	file.close()

	spadexml = """
	<spade>

               <domain>
                       <hostname>""" + hostname + """</hostname>
                       <jabberport>5222</jabberport>
               </domain>

               <acc>
                       <hostname>acc.""" + hostname + """</hostname>
                       <password>""" + acc_passwd +"""</password>
                       <port>9000</port>
               </acc>

               <ams>
                      <hostname>ams."""+hostname+"""</hostname>
                      <password>"""+ams_passwd+"""</password>
                      <port>9001</port>
               </ams>

               <df>
                      <hostname>df."""+hostname+"""</hostname>
                      <password>"""+df_passwd+"""</password>
                      <port>9002</port>
               </df>

        </spade>
	"""

	file = open("etc/spade.xml", "w+")
	file.write(spadexml)
	file.close()

if __name__ == '__main__':
    generateCode()

