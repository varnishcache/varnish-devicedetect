#!/usr/bin/env python
#
# This is a simple web server (listening to port 5911) that takes the
# X-UA-Device header into consideration when producing content.
#
# Author: Lasse Karstensen <lkarsten@varnish-software.com>, February 2012.
#
from __future__ import print_function
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from socket import AF_INET6
from pprint import pformat
import datetime

HEAD_CONTENT="""<html><body><h1>Device Detection test backend</h1>
<p>This is a test backend/web server for device detection. It will tell you what kind of device your client is recognized as by Varnish, typically by outputting the contents of the X-UA-Device header.</p>
<p>All content is in /devicetest/, and the backend will redirect you if you access /.</p>
"""
TAIL_CONTENT="""
<p>If you are accessing this backend through Varnish, and have the override URLs activated, you can change the active URL with the following links. They are not defined on the backend and will as such give you 404 without Varnish.</p>
<ul>
<li><a href="/set_ua_device/mobile-iphone">mobile-iphone</a><br/>
<li><a href="/set_ua_device/tablet-ipad">tablet-ipad</a><br/>
<li><a href="/set_ua_device/mobile-android">mobile-android</a>
<li><a href="/set_ua_device/tablet-android">tablet-android</a><br/>
<li><a href="/set_ua_device/mobile-smartphone">mobile-smartphone</a><br/>
<li><a href="/set_ua_device/mobile-generic">mobile-generic</a><br/>
<li><a href="/set_ua_device/">unset override cookie</a><br/>
</ul>
</body></html>
"""

class requesthandler(BaseHTTPRequestHandler):
    # http://docs.python.org/library/basehttpserver.html#BaseHTTPServer.BaseHTTPRequestHandler
    def do_GET(self):
        # remove any GET-args
        if "?" in self.path:
            self.path = self.path[0:self.path.index("?")]

        if self.path == "/":
            self.send_response(302, "Moved temporarily")
            self.send_header("Location", "/devicetest/")
            self.end_headers()
            return
        elif self.path != "/devicetest/":
            self.send_error(404, "Not found")
            self.end_headers()
            self.wfile.write("Only / and /devicetest/ are valid URLs")
            return
        self.send_response(200, "OK")
        self.send_header("Expires", "Fri, 30 Oct 1998 14:19:41 GMT")
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(HEAD_CONTENT)

        if not self.headers.get("X-UA-Device"):
            self.wfile.write("<strong>Your request does not have a X-UA-Device header set.</strong>")
        else:
            _s = "<strong>Your X-UA-Device header is: %s</strong>" % self.headers.get("X-UA-Device", "")
            self.wfile.write(_s)
        self.wfile.write("<p>Complete header set:</p><pre>%s</pre>" % pformat(self.headers.items()))
        self.wfile.write("<p>This page was generated %s.</p>" % (datetime.datetime.now().isoformat()))
        self.wfile.write(TAIL_CONTENT)

if __name__ == "__main__":
    server_address = ('', 5911)
    HTTPServer.allow_reuse_address = True
    HTTPServer.address_family = AF_INET6
    httpd = HTTPServer(server_address, requesthandler)
    print("Listening on %s:%s." % server_address)
    httpd.serve_forever()
