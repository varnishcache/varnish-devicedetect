=====================
Install and configure
=====================

Serve the different content on the same URL
-------------------------------------------

To serve different content based on the device type, add the following VCL::

    include "devicedetect.vcl";
    sub vcl_recv {
        # only do device detection on non-static content.
        if (!req.url ~ "^/[^?]+\.(jpeg|jpg|png|gif|ico|js|css|txt|gz|zip|lzma|bz2|tgz|tbz|html|htm)(\?.*|)$") {
            call devicedetect;
        }
    }

    sub vcl_hash {
        # add the device classification to the hash, so clients get the correct cached object
        if (req.http.X-hash-input) { hash_data(req.http.X-hash-input); }
    }

This will make a different set of cache objects based on what the client is identified as.


Different backend for mobile clients
------------------------------------

If you have a different backend that serves pages for mobile clients, or any special needs in VCL, you can use the X-UA-Device header like this::

    include "devicedetect.vcl";

    backend mobile {
        .host = "10.0.0.1";
        .port = "80";
    }

    sub vcl_recv {
        # only do device detection on non-static content.
        if (!req.url ~ "^/[^?]+\.(jpeg|jpg|png|gif|ico|js|css|txt|gz|zip|lzma|bz2|tgz|tbz|html|htm)(\?.*|)$") {
            call devicedetect;
        }

        if (req.http.X-UA-Device ~ "^mobile" || req.http.X-UA-device ~ "^tablet") {
            set req.backend = mobile;
        }
    }

Redirecting mobile clients
--------------------------

If you want to redirect mobile clients instead, you can use::

    include "devicedetect.vcl";
    sub vcl_recv {
        # only do device detection on non-static content.
        if (!req.url ~ "^/[^?]+\.(jpeg|jpg|png|gif|ico|js|css|txt|gz|zip|lzma|bz2|tgz|tbz|html|htm)(\?.*|)$") {
            call devicedetect;
        }

        if (req.http.X-UA-Device ~ "^mobile" || req.http.X-UA-device ~ "^tablet") {
            error 750 "Moved Temporarily";
        }
    }
     
    sub vcl_error {
        if (obj.status == 750) {
            set obj.http.Location = "http://m.example.com/";
            set obj.status = 302;
            return(deliver);
        }
    }

Signaling device type to the backend
------------------------------------

Except where redirection is used, the backend needs to be told what kind of 
client the content is meant to be served to.

** Example 1: 
The basic case is that Varnish add the X-UA-Device HTTP header on the 
backend requests, and the backend mentions in the response Vary header that the
content is dependant on this header. Everything works out of the box from 
Varnish's perspective.

** Example 2: Override the User-Agent string sent

If you do not have full control, but can access the User-Agent string (think the basic set of headers available by default for CGI scripts), you can change it
into the device type.

To make sure that any caches out on the Internet doesn't cache it, a Vary header
on User-Agent must be added on the way out.

VCL code::

    # override the header before it is sent to the backend
    sub vcl_miss { if (req.http.X-UA-Device) { set bereq.http.User-Agent = req.http.X-UA-Device; } }
    sub vcl_pass { if (req.http.X-UA-Device) { set bereq.http.User-Agent = req.http.X-UA-Device; } }

    # rewrite the response from the backend
    sub vcl_fetch {
        if (req.http.X-UA-Device) {
            if (beresp.http.Vary) { set beresp.http.Vary = beresp.http.Vary + ", User-Agent"; }
            else { set beresp.http.Vary = "User-Agent"; }
        }
    }

** Example 3: Add the device class as a GET query parameter

If everything else fails, you can add the device type as a GET argument. 
http://example.com/article/1234.html -> http://example.com/article/1234.html?devicetype=mobile-iphone

The same Vary trickery from Example 2 must be added here also.

VCL::

    # override the header before it is sent to the backend
    sub add_get_devicetype { 
        if (req.http.X-UA-Device && req.method == "GET") {
            unset req.http.X-get-devicetype;
            if (bereq.url !~ "\?") {
                set req.http.X-get-devicetype = "&devicetype=" + req.http.X-UA-Device;
            } else { 
                set req.http.X-get-devicetype = "?devicetype=" + req.http.X-UA-Device;
            }
            set bereq.url = bereq.url + req.http.X-get-devicetype;
        }
    }
    sub vcl_miss { call add_get_devicetype; }
    sub vcl_pass { call add_get_devicetype; }

    # rewrite the response from the backend
    sub vcl_fetch {
        if (req.http.X-UA-Device) {
            if (beresp.http.Vary) { set beresp.http.Vary = beresp.http.Vary + ", User-Agent"; }
            else { set beresp.http.Vary = "User-Agent"; }
            # if the backend returns a redirect (think missing trailing slash), we
            # will potentially show the extra address to the client. we don't want
            # that.
            # if the backend reorders the get parameters, you may need to be smarter here. (? and & ordering)
            if (beresp.status == 301 || beresp.status == 302 || beresp.status == 303) {
                set beresp.http.location = regsub(beresp.http.location, req.http.X-get-devicetype, "");
            }
        }
        unset req.http.X-get-devicetype;
    }



Testing tools
-------------

There are some tools included for testing and validating your setup.

* backend/example-backend.py 
* devicedetect-dev.vcl

If you include the -dev.vcl file, you can access /set_ua_device/ to set a
cookie that overrides the value of X-UA-Device which is sent to the backend.
(and used for cache lookups)

Example: enable devicedetection, go to /set_ua_device/mobile-iphone .
Afterwards, access your site as usual. You will now get the content as if your
browser was an iPhone. Watch out for the TTL settings.

There is an example web server in backend/ that listens on port 5911 and replies
differently depending on X-UA-Device. Run it with:

    cd backend
    ./example_backend.py

Now you can access it through:
   
    http://localhost:5911/devicetest/ , or
    http://localhost:6081/devicetest/ # Change 6081 into your Varnish listening port.

Happy devicedetecting.
