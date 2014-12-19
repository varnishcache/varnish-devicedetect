
#VARNISHD=/usr/sbin/varnishd
#VARNISHTEST=/usr/bin/varnishtest
VARNISHD=/opt/varnish4/sbin/varnishd
VARNISHTEST=/opt/varnish4/bin/varnishtest

TESTS=*.vtc

all: controlset snippets $(TESTS)

.PHONY: all controlset snippets $(TESTS)

controlset: ../controlset.txt vtc-from-controlset.py
	./vtc-from-controlset.py > 99-controlset.vtc

snippets: ../INSTALL.rst vtc-from-snippets.py
	find . -name snippet-\*vtc -exec rm "{}" \;
	./vtc-from-snippets.py ../INSTALL.rst

$(TESTS): controlset snippets
	${VARNISHTEST} -Dvarnishd=${VARNISHD} -Dprojectdir=$(PWD) $@
