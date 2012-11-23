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

    path = ""

    if os.name == "posix":
            # If no hostname was previously specified, get one from the system
        if globalhostname == "":
            hostname = socket.gethostname()
        else:
            hostname = globalhostname

        #path = os.sep+"usr"+os.sep+"share"+os.sep+"spade"
    else:
        # If no hostname was previously specified, get one from the system
        if globalhostname == "":
            hostname = socket.gethostbyaddr(socket.gethostname())[0]
        else:
            hostname = globalhostname
        #path = "usr"+os.sep+"share"+os.sep+"spade"

    if hostname == "localhost":
        hostname = "127.0.0.1"
        print "Translating localhost DNS to IP (127.0.0.1)."

    acc_passwd = "".join([string.ascii_letters[int(
        random.randint(0, len(string.ascii_letters) - 1))] for a in range(8)])
    ams_passwd = "".join([string.ascii_letters[int(
        random.randint(0, len(string.ascii_letters) - 1))] for a in range(8)])
    df_passwd = "".join([string.ascii_letters[int(
        random.randint(0, len(string.ascii_letters) - 1))] for a in range(8)])

    spadexml = """
<spade>
    <platform>
        <hostname>""" + hostname + """</hostname>
        <port>5222</port>
        <adminpasswd>secret</adminpasswd>
    </platform>

    <acc>
        <hostname>acc.""" + hostname + """</hostname>
        <password>""" + acc_passwd + """</password>
        <port>5222</port>
#MTPS#
    </acc>
    <ams>
        <hostname>ams.""" + hostname + """</hostname>
        <password>""" + ams_passwd + """</password>
        <port>5222</port>
    </ams>

    <df>
        <hostname>df.""" + hostname + """</hostname>
        <password>""" + df_passwd + """</password>
        <port>5222</port>
    </df>
</spade>
    """

    # Now fill the MTPs information
    #mtp_str = "\n"
    #for file in os.listdir("spade/mtp"):
    #    try:
    #        # If its a python script
    #        if file[-3:] == ".py":
    #            fname = file[:-3]
    #            mtp_str = mtp_str + '''\t\t\t<mtp name="''' + fname + '''">\n\t\t\t\t<instance>''' + fname + '''</instance>\n'''
    #            mtp_str = mtp_str + """\t\t\t\t<protocol>""" + fname + """</protocol>\n"""
    #            mtp_str = mtp_str + """\t\t\t</mtp>\n\n"""
    #    except Exception, e:
    #        print "EXCEPTION GETTING MTPS: ", str(e)

    # Fill the data
    mtp_str = '''
        <mtp name="http">
            <instance>http</instance>
            <protocol>http</protocol>
        </mtp>'''
    spadexml = spadexml.replace("#MTPS#", mtp_str)

    file = open("spade.xml", "w+")
    file.write(spadexml)
    file.close()

    # Generating real xmppd.xml
    if os.name == 'posix':
        xmppdxml = '''
<server>
    <servernames>
        <name>''' + hostname + '''</name>
    </servernames>
    <certificate file="xmppd.pem"/>
    <plugins>
        <MUC jid="muc.''' + hostname + '''" name="SPADE MUC Component"/>
        <WQ jid="wq.''' + hostname + '''" name="SPADE Workgroup Queues"/>
    </plugins>
    <components>
        <AMS jid="ams.''' + hostname + '''" name="AMS" username="ams" password="''' + ams_passwd + '''"/>
        <DF jid="df.''' + hostname + '''" name="DF" username="df" password="''' + df_passwd + '''"/>
        <ACC jid="acc.''' + hostname + '''" name="ACC" username="acc" password="''' + acc_passwd + '''"/>
    </components>
</server>
        '''
    else:
        xmppdxml = '''
<server>
    <servernames>
        <name>''' + hostname + '''</name>
    </servernames>
    <certificate file="xmppd.pem"/>
    <plugins>
        <MUC jid="muc.''' + hostname + '''" name="SPADE MUC Component"/>
        <WQ jid="wq.''' + hostname + '''" name="SPADE Workgroup Queues"/>
    </plugins>
    <components>
        <AMS jid="ams.''' + hostname + '''" name="AMS" username="ams" password="''' + ams_passwd + '''"/>
        <DF jid="df.''' + hostname + '''" name="DF" username="df" password="''' + df_passwd + '''"/>
        <ACC jid="acc.''' + hostname + '''" name="ACC" username="acc" password="''' + acc_passwd + '''"/>
    </components>
</server>
        '''

    file = open("xmppd.xml", "w+")
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
