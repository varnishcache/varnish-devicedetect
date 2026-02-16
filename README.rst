=====================================
IMPORTANT - THIS REPOSITORY HAS MOVED
=====================================

New location: https://code.vinyl-cache.org/vinyl-cache/vinyl-cache

The main branch changes from ``master`` to ``main``.

Read this: https://vinyl-cache.org/organization/moving.html

Device detection in Varnish
===========================

Introduction
------------

The goal of this VCL set is to provide a simple & easy way of getting
device detection going in Varnish Cache. (https://www.varnish-cache.org)

Specific problems we want to solve:

1) Detect the most common and easily detected (mobile/tablet) platforms.
2) Provide example VCL for using devicedetect.vcl with your existing VCL.

These are explicit not goals for this project:

* Create a comprehensive set of capabilities per client. We don't want to spend a lot of effort on maintenance.
* Be perfect. It usually works, but if you need guarantees you should consider the commercial offerings instead.

This project is maintained and updated by the community. If you see any false
positives or missing strings, fork the git repository and send a pull request.


Requirements
------------

You need a recent Varnish release. It may function with some adjustments on
previous versions, but you are on your own.

It is worth noting that there is no compilation/linking required. This is VCL
code only.

Your backends needs to be able to do produce different content based on what
type of device this is. This can be signalled to the backend through the URL,
with an extra HTTP header or with a cookie. See the INSTALL.rst file for
examples.

Use cases
---------

The following uses are envisioned for this VCL:

* Serve different content per device type on the same URL. This has the upside of not requiring a redirect on slow mobile networks.
* Redirect mobile/tablets to a different URL. (http://example.com/article/1234.html -> http://m.example.com/article/1234.html)


Installation
------------

See the INSTALL.rst file for details.


Similar efforts
---------------

These similar efforts for User-Agent insights are known to us:

* https://deviceatlas.com/ (commercial)
* https://github.com/OpenDDRdotORG (free)
* https://www.varnish-cache.org/vmod/deviceatlas-mobile-detection (commercial VMOD for Deviceatlas by Varnish Software)
* https://github.com/TheWeatherChannel/dClass
* https://github.com/serbanghita/Mobile-Detect
* https://github.com/willemk/varnish-mobiletranslate (Generate VCL from Mobile-Detect data)


Contact
-------

This project lives on Github:

    https://github.com/varnishcache/varnish-devicedetect/

Feature requests, bug reports and such can be added to the Github issue tracker.

This code is currently maintained by Christopher Slowe <me@keysersosa.com>.
