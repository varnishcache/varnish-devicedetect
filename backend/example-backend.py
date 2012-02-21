#!/usr/bin/python
#
# This is a simple web server that takes the X-UA-Device header into
# consideration when producing content.
#
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from pprint import pformat
import datetime

HEAD_CONTENT="""<html><body><h1>Device Detection test backend</h1>
<p>This is a test backend/web server for device detection. It will tell you what kind of device your client is recognized as, if set. By default it will just give you the contents of the X-UA-Device header, if set.</p>
<p>All content is in /devicetest/, and the backend will redirect you if you access /.</p>
"""
TAIL_CONTENT="""
<p>If you are accessing this backend through Varnish, and have the override URLs activacted, you can change the active URL with the following links. They are not defined on the backend and will as such give you 404 without Varnish.</p>
<ul>
<li><a href="/set_ua_device/mobile-generic">mobile-generic</a>
<li><a href="/set_ua_device/mobile-iphone">mobile-iphone</a><br/>
</ul>
</body></html>
""" 

class requesthandler(BaseHTTPRequestHandler):
    # http://docs.python.org/library/basehttpserver.html#BaseHTTPServer.BaseHTTPRequestHandler
    def do_GET(self): 
        if self.path == "/":
            self.send_response(302, "Moved temporarily")
            self.send_header("Location", "/devicetest/")
            self.end_headers()
            return
        elif self.path != "/devicetest/":
            self.send_error(404, "Not found")
            self.end_headers()
            self.wfile.write("Only root-URL is defined")
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

def main():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, requesthandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
