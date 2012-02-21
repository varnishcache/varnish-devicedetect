#
# devicedetect-dev.vcl
#
# Enable test URLs and cookie overrides

backend devicetest { 
    .host = "127.0.0.1";
    .port = "8000";
}

sub vcl_recv {
    if (req.url ~ "^/set_devicetype/") { error 701 regsub(req.url, "^/set_devicetype/", ""); }
    if (req.url ~ "^/devicetest") { set backend = devicetest; }
}

sub vcl_error { 
    if (obj.status == 701 ) {
        # obj.response == mobile-generic
        set obj.http.Set-Cookie = "X-UA-device=" + obj.response;
        set obj.http.Content-Type = "text/plain; charset=utf-8";
        synthetic {" 200 OK, Cookie set "};
	return(deliver)
    }
}
"""
