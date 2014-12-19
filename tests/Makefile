
#VARNISHD=/usr/sbin/varnishd
#VARNISHTEST=/usr/bin/varnishtest
VARNISHD=/opt/varnish4/sbin/varnishd
VARNISHTEST=/opt/varnish4/bin/varnishtest

TESTS=*.vtc

all: controlset $(TESTS)

.PHONY: all controlset $(TESTS)

controlset: ../controlset.txt vtc-from-controlset.py
	./vtc-from-controlset.py > 99-controlset.vtc

$(TESTS): controlset
	${VARNISHTEST} -Dvarnishd=${VARNISHD} -Dprojectdir=$(PWD) $@
