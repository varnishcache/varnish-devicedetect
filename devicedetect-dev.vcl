#
# devicedetect-dev.vcl
#
# Enable test URLs and cookie overrides.
#
vcl 4.0;

backend devicetest {
	.host = "127.0.0.1";
	.port = "5911";
}

sub vcl_recv {
	# 701/702 are arbitrary chosen return codes that is only used internally in varnish.
	if (req.url ~ "^/set_ua_device/.+") {
		return(synth(701, regsub(req.url, "^/set_ua_device/", ""));
	}
	# set expired cookie if nothing is specified
	if (req.url ~ "^/set_ua_device/") {
		return(synth(702, "OK"));
	}
	if (req.url ~ "^/devicetest") {
		set req.backend = devicetest;
	}
}

sub vcl_synth {
	if (resp.status == 701 || resp.status == 702) {
		if (resp.status == 702) {
			set resp.http.Set-Cookie = "X-UA-Device-force=expiring; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
			set resp.status = 200;
		} else {
			set resp.http.Set-Cookie = "X-UA-Device-force=" + resp.reason + "; Path=/;";
			set resp.status = 200;
		}
		set resp.http.Content-Type = "text/html; charset=utf-8";
		synthetic {"<html><body><h1>OK, Cookie updated</h1><a href='/devicetest/'>/devicetest/</a></body></html>"};
		set resp.http.response = "OK";
		return(deliver);
	}
}
