#
VARNISHD := $(shell which varnishd)
VARNISHTEST := $(shell which varnishtest)
TESTS=tests/*.vtc

.PHONY: check initial
all: initial check

initial: controlset.txt tests/vtc-from-controlset.py INSTALL.rst tests/vtc-from-snippets.py
	tests/vtc-from-controlset.py controlset.txt > tests/99-controlset.vtc
	find tests/ -name snippet-\*vtc -exec rm "{}" \;
	cd tests && ./vtc-from-snippets.py ../INSTALL.rst

check: $(TESTS)

$(TESTS): devicedetect.vcl initial
	${VARNISHTEST} -Dvarnishd=${VARNISHD} -Dprojectdir=$(PWD) $@

