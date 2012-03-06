=====================
Install and configure
=====================

Serve the different content on the same URL
-------------------------------------------

To serve different content based on the device type, add the following VCL::

    include "devicedetect.vcl";

    sub vcl_recv { call devicedetect; }
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
        call devicedetect;

        if (req.http.X-UA-Device ~ "^mobile" || req.http.X-UA-device ~ "^tablet") {
            set req.backend = mobile;
        }
    }

Redirecting mobile clients
--------------------------

If you want to redirect mobile clients instead, you can use::

    include "devicedetect.vcl";
    sub vcl_recv {
        call devicedetect;

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

Example 1: Send HTTP header to backend
''''''''''''''''''''''''''''''''''''''

The basic case is that Varnish add the X-UA-Device HTTP header on the 
backend requests, and the backend mentions in the response Vary header that the
content is dependant on this header. Everything works out of the box from 
Varnish's perspective.

... 071-example1-start
Example VCL::

    include "devicedetect.vcl";
    sub vcl_recv { call devicedetect; }

    sub add_x-ua-device {
        if (req.http.X-UA-Device) { 
            set bereq.http.X-UA-Device = req.http.X-UA-Device; }
    }
    
    # This must be done in vcl_miss and vcl_pass, before any backend request is
    # actually sent. vcl_fetch runs after the request to the backend has
    # completed.
    sub vcl_miss { call add_x-ua-device; }
    sub vcl_pass { call add_x-ua-device; }
... 071-example1-end

Please remember that the backend must send a Vary header on User-Agent, or you will need to add that manually. See below for an example.


Example 2: Normalize the User-Agent string
''''''''''''''''''''''''''''''''''''''''''

Another way of signaling the device type is to override or normalize the
User-Agent header sent to the backend::

    User-Agent: Mozilla/5.0 (Linux; U; Android 2.2; nb-no; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1
    ->
    User-Agent: mobile-android

This works if you don't need the original header for anything. A possible use
for this is for CGI scripts where only a small set of predefined headers are
(by default) available for the script.

To make sure that any caches out on the Internet doesn't cache it, a Vary header
on User-Agent must be added on the way out.

... 072-example2-start
VCL::

    include "devicedetect.vcl";
    sub vcl_recv { call devicedetect; }

    # override the header before it is sent to the backend
    sub vcl_miss { if (req.http.X-UA-Device) { set bereq.http.User-Agent = req.http.X-UA-Device; } }
    sub vcl_pass { if (req.http.X-UA-Device) { set bereq.http.User-Agent = req.http.X-UA-Device; } }

    # so, this is a bit conterintuitive. The backend creates content based on the normalized User-Agent,
    # but we use Vary on X-UA-Device so Varnish will use the same cached object for all U-As that map to
    # the same X-UA-Device.

    # if the backend does not mention in Vary that it has crafted special
    # content based on the User-Agent (==X-UA-Device), add it.
    # If your backend does set Vary: User-Agent, you may have to remove that here.
    sub vcl_fetch {
        if (req.http.X-UA-Device) {
            if (!beresp.http.Vary) { # no Vary at all
                set beresp.http.Vary = "X-UA-Device"; 
            } elseif (beresp.http.Vary !~ "X-UA-Device") { # add to existing Vary
                set beresp.http.Vary = beresp.http.Vary + ", X-UA-Device"; 
            }
        }
        # comment this out if you don't want the client to know your classification
        set beresp.http.X-UA-Device = req.http.X-UA-Device;
    }

    # to keep any caches in the wild from serving wrong content to client #2 behind them, we need to
    # transform the Vary on the way out.
    sub vcl_deliver {
        if ((req.http.X-UA-Device) && (resp.http.Vary)) {
            set resp.http.Vary = regsub(resp.http.Vary, "X-UA-Device", "User-Agent");
        }
    }


... 072-example2-end

Example 3: Add the device class as a GET query parameter
''''''''''''''''''''''''''''''''''''''''''''''''''''''''

If everything else fails, you can add the device type as a GET argument. 

    http://example.com/article/1234.html --> http://example.com/article/1234.html?devicetype=mobile-iphone

The same Vary trickery from Example 2 must be added here also.

... 073-example3-start
VCL::

    include "devicedetect.vcl";
    sub vcl_recv { 
        call devicedetect; 
        if ((req.http.X-UA-Device) && (req.request == "GET")) {
            # if there are existing GET arguments;
            if (req.url ~ "\?") {
                set req.http.X-get-devicetype = "&devicetype=" + req.http.X-UA-Device;
            } else { 
                set req.http.X-get-devicetype = "?devicetype=" + req.http.X-UA-Device;
            }
            set req.url = req.url + req.http.X-get-devicetype;
            unset req.http.X-get-devicetype;
        }
    }

    # rewrite the response from the backend
    sub vcl_fetch {
        if (req.http.X-UA-Device) {
            if (beresp.http.Vary) { set beresp.http.Vary = beresp.http.Vary + ", User-Agent"; }
            else { set beresp.http.Vary = "User-Agent"; }
            # if the backend returns a redirect (think missing trailing slash), we
            # will potentially show the extra argument to the client. we don't want
            # that.
            # if the backend reorders the GET parameters, you may need to be smarter here. (? and & ordering)
            if (beresp.status == 301 || beresp.status == 302 || beresp.status == 303) {
                set beresp.http.location = regsub(beresp.http.location, "[?&]devicetype=.*$", "");
            }

            # comment this out if you don't want the client to know your classification
            set beresp.http.X-UA-Device = req.http.X-UA-Device;
        }
    }

... 073-example3-end


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
differently depending on X-UA-Device. Run it with::

    cd backend
    ./example_backend.py

Now you can access it through::
   
    http://localhost:5911/devicetest/ , or
    http://localhost:6081/devicetest/ # Change 6081 into your Varnish listening port.

Happy devicedetecting.
