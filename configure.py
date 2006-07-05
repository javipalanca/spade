#!/usr/bin/env python

import sys
import string
import random
import os
import socket


globalhostname = ""

def generateCode():
	# Fill the template with the correct data
	
	global jabber_template
	global globalhostname

	if os.name == "posix":
			# If no hostname was previously specified, get one from the system
		if globalhostname == "":	
			hostname = socket.gethostname()
		else:
			hostname = globalhostname

		path = os.sep+"usr"+os.sep+"share"+os.sep+"spade"
	else:
		# If no hostname was previously specified, get one from the system
		if globalhostname == "":	
			hostname = socket.gethostbyaddr(socket.gethostname())[0]
		else:
			hostname = globalhostname
		path = "usr"+os.sep+"share"+os.sep+"spade"

	#acc_passwd = "".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(8)])
	ams_passwd = "".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(8)])
	df_passwd = "".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(8)])


	spadexml = """
	<spade>

               <platform>
                       <hostname>""" + hostname + """</hostname>
                       <port>5222</port>
		       <path>"""+path+"""</path>
               </platform>

               <acc>
	       #MTPS#
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

	# Now fill the MTPs information
	"""
	mtp_str = ""
	for file in os.listdir("usr/share/spade/mtp"):
		try:
			# If its a python script
			if file[-3:] == ".py":
				fname = file[:-3]
				mtp_str = mtp_str + '<mtp name = "' + fname + '"><instance>' + fname + '</instance>'
				mtp_str = mtp_str + "<protocol>" + fname + "</protocol>"
				mtp_str = mtp_str + "</mtp>\n	       "
		except:
			pass
		
	# Fill the data
	spadexml = spadexml.replace("#MTPS#", mtp_str)
	"""
	spadexml = spadexml.replace("#MTPS#", "")	

	file = open("etc/spade.xml", "w+")
	file.write(spadexml)
	file.close()

	# Generating real xmppd.xml
	if os.name == 'posix':
		xmppdxml = '''
		<server>
	        	<servernames>
	                	<name>'''+hostname+'''</name>
		        </servernames>
		        <certificate file="xmppd.pem"/>
	        	<spool path="'''+str(os.environ['HOME'])+'''/.spade/spool"/>
			<muc jid="muc.'''+hostname+'''" name="SPADE MUC Component"/>
		</server>
		'''
	else:
		xmppdxml = '''
		<server>
	        	<servernames>
	                	<name>'''+hostname+'''</name>
		        </servernames>
		        <certificate file="xmppd.pem"/>
	        	<spool path="usr/share/spade/xmppd/spool"/>
			<muc jid="muc.'''+hostname+'''" name="SPADE MUC Component"/>
		</server>
		'''

	file = open("etc/xmppd.xml", "w+")
	file.write(xmppdxml)
	file.close()



if __name__ == '__main__':
    # We look for a command line parameter
    if len(sys.argv) > 1:
	# There is a parameter
	globalhostname = sys.argv[1]
    else:
	# There is no parameter (i.e. macho-mode)
	pass
	
    generateCode()

