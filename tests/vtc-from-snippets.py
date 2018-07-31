#!/usr/bin/env python3
"""
Pick out the examples from the installation documentation and
build a VTC test case around it.

This is to make sure that our documented examples are always runnable.

Format from the input file:
.. foo-start
vcl code here
.. foo-end

foo is a name that describes the vcl snippet.
"""
from sys import argv, stdout
from pprint import pprint

def header(description):
    return """varnishtest "%s"
server s1 {
       rxreq
       txresp
} -start

varnish v1 -vcl+backend {
    include "${projectdir}/devicedetect.vcl";""" % description

def tailer(optional_req):
    s = """} -start

client c1 {
"""
    if req:
        s += "    # from rst\n"
        s += req
    else:
        s += """
    txreq -req GET -url /foo -hdr "User-Agent: Mozilla/5.0 (Linux; U; Android 2.2; nb-no; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1" -hdr "Host: example.com"
    rxresp
    expect resp.status == 200"""
    s += """
} -run"""
    return s

def parse(inputfile):
    section = None
    buf = []
    req = []

    for line in open(inputfile):
        if line.startswith(".. req:"):
            req.append(line[len(".. req:"):])
            continue

        if line.startswith(".. startsnippet-"):
            section = line.replace(".. startsnippet-", "")[:-1]
            continue
        if line.startswith(".. endsnippet-"):
            try:
                assert section is not None
                assert line.startswith(".. endsnippet-%s" % section)
            except AssertionError:
                print(section, line)
                print(buf)
                print(req)
                raise

            yield section, "".join(buf), "   ".join(req)
            section = None
            buf = []
            req = []

        if section:
            # No allowed to have comments/"startsnippet" inside block sections.
            if line.startswith("VCL::"):
                continue
            if "include" in line and "devicedetect.vcl" in line:
                continue
            buf += [line]

if __name__ == "__main__":
    rstfile = argv[1]
    for name, testsnippet, req in parse(rstfile):
        with open("snippet-%s.vtc" % name, "w+") as fp:
            print(header(name), file=fp)
            print(testsnippet, file=fp)
            print(tailer(req), file=fp)
