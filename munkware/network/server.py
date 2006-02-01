#!/usr/bin/env python

import BaseHTTPServer
import string
import munkware
import traceback

class mwHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        #addr = "ADDR:%s" % str(self.client_address)
        #cmd = "CMD:%s" % self.command
        #path = "PATH:%s" % self.path
        #ver = "VER:%s" % self.request_version
        #foo = "FOO:%s" % self.server.foo
        #request = "<br>\n".join([addr, cmd, path, ver, foo])
        #self.send_response(200, "OK")
        #self.end_headers()
        #self.wfile.write('<html><head><title>TEST</title></head><body>%s</body></html>' % request)
        if self.path.startswith("/queue/put_commit/"): #do a queue.put_commit()
            try:
                ndx = int(string.split(self.path, '/', 3)[3])
                self.server.queue.put_commit(ndx)
                self.send_response(200, "OK")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body>Put Committed successfully</body></html>')
            except munkware.mwQueue.BadIndex: # ndx didn't exist
                self.send_response(404, "NOT FOUND")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>404 Error</h1><br>Index was not found</body></html>')
            except: # unknown exception
                traceback.print_exc()
                self.send_response(500, "ERROR")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>500 Error</h1><br>Queue generated error</body></html>')
        elif self.path.startswith("/queue/put_rollback/"): #do a queue.put_rollback()
            try:
                ndx = int(string.split(self.path, '/', 3)[3])
                self.server.queue.put_rollback(ndx)
                self.send_response(200, "OK")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body>Put Rollback successfull</body></html>')
            except munkware.mwQueue.BadIndex: # ndx didn't exist
                self.send_response(404, "NOT FOUND")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>404 Error</h1><br>Index was not found</body></html>')
            except: # unknown exception
                traceback.print_exc()
                self.send_response(500, "ERROR")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>500 Error</h1><br>Queue generated error</body></html>')

        elif self.path == "/queue/avail": #do a queue.get()
            try:
                (ndx, item) = self.server.queue.get(0)
                self.send_response(200, "OK")
                location = "/queue/rqstd/%s" % str(ndx)
                self.send_header("Location", location)
                self.end_headers()
                self.wfile.write(str(item))
            except munkware.mwQueue.Empty: # ndx didn't exist
                self.send_response(204, "NO RESPONSE")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>204 Error</h1><br>Queue was empty</body></html>')
            except: # unknown exception
                traceback.print_exc()
                self.send_response(500, "ERROR")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>500 Error</h1><br>Queue generated error</body></html>')
        elif self.path.startswith("/queue/get_commit/"): #do a queue.get_commit()
            try:
                ndx = int(string.split(self.path, '/', 3)[3])
                self.server.queue.get_commit(ndx)
                self.send_response(200, "OK")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body>Get Committed successfully</body></html>')
            except munkware.mwQueue.BadIndex: # ndx didn't exist
                self.send_response(404, "NOT FOUND")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>404 Error</h1><br>Index was not found</body></html>')
            except: # unknown exception
                traceback.print_exc()
                self.send_response(500, "ERROR")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>500 Error</h1><br>Queue generated error</body></html>')
        elif self.path.startswith("/queue/get_rollback/"): #do a queue.get_rollback()
            try:
                ndx = int(string.split(self.path, '/', 3)[3])
                self.server.queue.get_rollback(ndx)
                self.send_response(200, "OK")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body>Get Rollback successfull</body></html>')
            except munkware.mwQueue.BadIndex: # ndx didn't exist
                self.send_response(404, "NOT FOUND")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>404 Error</h1><br>Index was not found</body></html>')
            except: # unknown exception
                traceback.print_exc()
                self.send_response(500, "ERROR")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>500 Error</h1><br>Queue generated error</body></html>')

        else:
            self.send_response(404, "NOT FOUND")
            self.end_headers()
            self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>404 Error</h1><br>The requested resource was not found</body></html>')

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        body = self.rfile.read(length)
        #addr = "ADDR:%s" % str(self.client_address)
        #cmd = "CMD:%s" % self.command
        #path = "PATH:%s" % self.path
        #ver = "VER:%s" % self.request_version
        #request = "<br>\n".join([body, addr, cmd, path, ver, foo])
        if self.path == "/queue": #do a queue.put()
            try:
                put_rc = self.server.queue.put(body, 0)
                self.send_response(201, "OK")
                location = "/queue/put/%s" % str(put_rc)
                self.send_header("Location", location)
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body>Go <a href="/queue/put_commit/%s">here</a> to commit your queue.put().</body></html>' % put_rc)
            except munkware.mwQueue.Full: # queue was full
                self.send_response(502, "FULL")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>502 Error</h1><br>Queue was full</body></html>')
            except: # unknown exception
                traceback.print_exc()
                self.send_response(500, "ERROR")
                self.end_headers()
                self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>500 Error</h1><br>Queue generated error</body></html>')
        else:
            self.send_response(404, "NOT FOUND")
            self.end_headers()
            self.wfile.write('<html><head><title>QUEUE</title></head><body><h1>404 Error</h1><br>The requested resource was not found</body></html>')


def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=mwHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.queue = munkware.mwQueue.BaseACIDQueue('q', 5)
    httpd.serve_forever()

if __name__ == "__main__":
    run()

'''
PUT
-----------------
POST /<queue>

success
201 w/ index in Location: header

failure - queue full
502 (Service temporarily overloaded) - do non-blocking put 

failure - unhandled exception
500
==================

PUT_COMMIT
-----------------
GET /<queue>/put/<index>

success
200

index error
404

failure - unhandled exception
500
==================

GET
-----------------
GET /<queue>/avail

success
200 w/ serialized objects in HTTP body and index in Location: header

failure - queue empty
204 ( No Response)

failure - unhandled exception
500
==================


GET_COMMIT
-----------------
GET /<queue>/rqstd/<index>

success
200

index error
404

failure - unhandled exception
500
==================
'''
