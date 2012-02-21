#!/usr/bin/python
#
# This is a simple web server that takes the X-UA-Device header into
# consideration when producing content.
#
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

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
        self.send_header("Cache-Control", "max-age=0")
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        if not self.headers.get("X-UA-Device"):
            self.wfile.write(HEAD_CONTENT)
            self.wfile.write("<strong>Your request does not not have a X-UA-Device header set.</strong>")
            self.wfile.write(TAIL_CONTENT)
        else:
            self.wfile.write(HEAD_CONTENT)
            _s = "<strong>Your X-UA-Device header is: %s</strong>" % \
                self.headers.get("X-UA-Device")
            self.wfile.write(_s)
            self.wfile.write(TAIL_CONTENT)

def main():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, requesthandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
