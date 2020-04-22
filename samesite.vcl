sub samesite {
        # See list here:
        # https://www.chromium.org/updates/same-site/incompatible-clients
	unset req.http.X-UA-SameSiteNone;
	set req.http.X-UA-SameSiteNone = "supported";

        # Versions of Chrome from Chrome 51 to Chrome 66 (inclusive on both ends). These Chrome versions will reject a cookie with `SameSite=None`
        if (req.http.user-agent ~ "Chrom(e|ium)" &&
        (req.http.user-agent ~ "Chrom[^ \/]+\/5[1-9][\.\d]*" ||
        req.http.user-agent ~ "Chrom[^ \/]+\/6[0-6][\.\d]*")) {
                set req.http.X-UA-SameSiteNone = "unsupported";
    }

    # Versions of UC Browser on Android prior to version 12.13.2. Older versions will reject a cookie with `SameSite=None`
    if (req.http.user-agent ~ "UCBrowser\/" && (req.http.user-agent ~ "UCBrowser\/[0-9]\.\d+\.\d+[\.\d]*" || req.http.user-agent ~ "UCBrowser\/1[0-1]\.\d+\.\d+[\.\d]*" ||
        req.http.user-agent ~ "UCBrowser\/12\.[0-9]\.\d+[\.\d]*" || req.http.user-agent ~ "UCBrowser\/12\.1[0-2]\.\d+[\.\d]*" || req.http.user-agent ~ "UCBrowser\/12\.13\.[0-1][\.\d]*")) {
        set req.http.X-UA-SameSiteNone = "unsupported";
    }

    #######################
    # hasWebKitSameSiteBug:
    #
    # all browsers on iOS 12
    if (req.http.user-agent ~ "\(iP.+; CPU .*OS 12[_\d]*.*\) AppleWebKit\/") {
        set req.http.X-UA-SameSiteNone = "unsupported";
    }
    # Safari & embedded browsers on MacOS 10.14
    if (req.http.user-agent ~ "\(Macintosh;.*Mac OS X 10_14[_\d]*.*\) AppleWebKit\/") {
        # isSafari
        # ||
        # isMacEmbeddedBrowser
        if ((req.http.user-agent ~ "Version\/.* Safari\/" && req.http.user-agent !~ "Chrom(e|ium)") ||
            (req.http.user-agent ~ "^Mozilla\/[\.\d]+ \(Macintosh;.*Mac OS X [_\d]+\) AppleWebKit\/[\.\d]+ \(KHTML, like Gecko\)$")) {
            set req.http.X-UA-SameSiteNone = "unsupported";
        }
    }
}
