#!/usr/bin/python
#
# Generate a varnishtest script to validate the preclassified
# U-A strings in the control set.
#
import sys

HEADER="""varnishtest "automatic test of control set"
server s1 {
       rxreq
       txresp
} -start
varnish v1 -vcl+backend {
        include "${projectdir}/../devicedetect.vcl";
        sub vcl_recv { call devicedetect; }
        sub vcl_deliver { set resp.http.X-UA-Device = req.http.X-UA-Device; }
} -start
client c1 {
"""
TAILER="""
}
client c1 -run
"""

def main():
    print HEADER
    for line in open("../controlset.txt").readlines():
        if line.startswith("#"): continue
        line = line.strip()
        if len(line) == 0: continue

        classid, uastring = line.split("\t", 1)
        #print >>sys.stderr, classid, uastring
        print "\ttxreq -hdr \"User-Agent: %s\"" % uastring
        print "\trxresp" 
        print "\texpect resp.http.X-UA-Device == \"%s\"" % classid
        print "\n" # for readability
    print TAILER


if __name__ == "__main__":
    main()
