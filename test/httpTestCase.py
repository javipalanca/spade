# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest
import BaseHTTPServer

try:
    import json
except ImportError:
    import simplejson as json

import spade

host = "127.0.0.1"


class MyAgent(spade.Agent.Agent):

    def _setup(self):
        self.msg = None


class SendMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@" + host, ["http://" + host + ":2099/b"]))
        msg.setContent("HTTPtestSendMsg")

        self.myAgent.send(msg)


class RecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        self.myAgent.msg = self._receive(block=True, timeout=20)


class AnswerMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = None
        msg = self._receive(block=True, timeout=10)
        if msg is not None:
            content = msg.getContent()
            msg = msg.createReply()
            msg.setContent(content)
            self.myAgent.send(msg)


class SendAndRecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@" + host, ["http://" + host + ":2099/b"]))
        msg.setContent("HTTPtestSendAndRecvMsg")

        self.myAgent.send(msg)
        self.myAgent.msg = None
        self.myAgent.msg = self._receive(block=True, timeout=20)


class SendJSONMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@" + host, ["http://" + host + ":2099/b"]))
        msg.setContent("HTTPtestSendJSONMsg")
        msg.setAclRepresentation(spade.ACLMessage.FIPA_ACL_REP_JSON)

        self.myAgent.send(msg)


class Send2HTTPServerBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@" + host, ["http://" + host + ":2100/b"]))
        msg.setContent("HTTPtestSendJSONMsg")
        msg.setAclRepresentation(spade.ACLMessage.FIPA_ACL_REP_JSON)

        self.myAgent.send(msg)


class HTTPTestCase(unittest.TestCase):

    def setUp(self):

        self.Aaid = spade.AID.aid("a@" + host, ["xmpp://a@" + host])
        self.Baid = spade.AID.aid("b@" + host, ["xmpp://b@" + host])

        self.a = MyAgent("a@" + host, "secret")
        self.a.start()
        self.b = MyAgent("b@" + host, "secret")
        self.b.start()
        #self.b.setDebugToScreen()
        #self.a.setDebugToScreen()

    def tearDown(self):
        self.a.stop()
        self.b.stop()

    def testSendMsg(self):
        template = spade.Behaviour.ACLTemplate()
        #template.setSender(self.Aaid)
        template.setContent("HTTPtestSendMsg")
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(RecvMsgBehav(), t)
        self.a.addBehaviour(SendMsgBehav(), None)
        counter = 0
        while self.b.msg is None and counter < 20:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg, None)
        self.assertEqual(self.b.msg.getContent(), "HTTPtestSendMsg")
        self.assertEqual(self.b.msg.getSender(), self.Aaid)
        self.assertEqual(len(self.b.msg.getReceivers()), 1)
        #self.assertEqual(self.b.msg.getReceivers()[0], self.Baid) #need to add http address

    def testSendAndRecvMsg(self):
        template = spade.Behaviour.ACLTemplate()
        #template.setSender(self.Aaid)
        template.setContent("HTTPtestSendAndRecvMsg")
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(AnswerMsgBehav(), t)
        template.setSender(self.Baid)
        t = spade.Behaviour.MessageTemplate(template)
        self.a.addBehaviour(SendAndRecvMsgBehav(), t)
        counter = 0
        while self.a.msg is None and counter < 20:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.a.msg, None)
        self.assertEqual(self.a.msg.getContent(), "HTTPtestSendAndRecvMsg")

    def testSendJSONMsg(self):
        template = spade.Behaviour.ACLTemplate()
        #template.setSender(self.Aaid)
        template.setContent("HTTPtestSendJSONMsg")
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(RecvMsgBehav(), t)
        self.a.addBehaviour(SendJSONMsgBehav(), None)
        counter = 0
        while self.b.msg is None and counter < 20:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg, None)
        self.assertEqual(self.b.msg.getContent(), "HTTPtestSendJSONMsg")
        self.assertEqual(self.b.msg.getSender(), self.Aaid)
        self.assertEqual(len(self.b.msg.getReceivers()), 1)

    class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(format, *args):
            pass

        def do_POST(self):
            boundary = self.headers.getparam('boundary')
            clen = self.headers.getheader('Content-Length')
            buf1 = self.rfile.read(int(clen)).split("--" + boundary + "--")
            buf2 = buf1[0].split("--" + boundary)
            env = buf2[1]
            pay = buf2[2]
            index = env.find('\n\n')
            self.server.type_env = env[0:index].split(':')[1].split(';')[0].strip()
            self.server.env = env[index + 2:]
            # the same for payload
            index = pay.find('\n\n')
            self.server.type_pay = pay[0:index].split(':')[1].split()[0].strip()
            self.server.pay = pay[index + 2:]

            self.send_response(200)
            self.server.done = True

    def testSend2HTTPServer(self):
        template = spade.Behaviour.ACLTemplate()
        #template.setSender(self.Aaid)
        template.setContent("HTTPtestSendJSONMsg")
        t = spade.Behaviour.MessageTemplate(template)

        httpd = BaseHTTPServer.HTTPServer(("", 2100), self.Handler)
        httpd.done = False
        httpd.env = httpd.pay = None
        import thread
        thread.start_new_thread(httpd.handle_request, ())

        self.a.addBehaviour(Send2HTTPServerBehav(), None)
        counter = 0
        while httpd.done is False and counter < 20:
            time.sleep(1)
            counter += 1

        assert httpd.env is not None
        assert httpd.pay is not None
        assert httpd.type_env == "application/json"
        assert json.loads(httpd.env)["acl-representation"] == "fipa.acl.rep.json.std"
        assert httpd.type_pay == "application/json"
        assert json.loads(httpd.pay)["content"] == "HTTPtestSendJSONMsg"
        assert json.loads(httpd.pay)["performative"] == "inform"
        assert json.loads(httpd.pay)["sender"]["name"] == "a@" + host

if __name__ == "__main__":
    unittest.main()
