#
# devicedetect-dev.vcl
#
# Enable test URLs and cookie overrides.
#

backend devicetest { 
    .host = "127.0.0.1";
    .port = "5911";
}

sub vcl_recv {
    # 701/702 are arbitrary chosen return codes that is only used internally in varnish.
    if (req.url ~ "^/set_ua_device/.+") { error 701 regsub(req.url, "^/set_ua_device/", ""); }
    # set expired cookie if nothing is specified
    if (req.url ~ "^/set_ua_device/") { error 702 "OK"; }
    if (req.url ~ "^/devicetest") { set req.backend = devicetest; }
}

sub vcl_error { 
    if (obj.status == 701 || obj.status == 702) {
        if (obj.status == 702) {
            set obj.status = 200;
            set obj.http.Set-Cookie = "X-UA-Device-force=expiring; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";

	} else {
	    set obj.status = 200;
	    set obj.http.Set-Cookie = "X-UA-Device-force=" + obj.response + "; Path=/;";
	}
        set obj.http.Content-Type = "text/html; charset=utf-8";
        synthetic {"<html><body><h1>OK, Cookie updated</h1><a href='/devicetest/'>/devicetest/</a></body></html>"};
        set obj.response = "OK";
        return(deliver);
    }
}
