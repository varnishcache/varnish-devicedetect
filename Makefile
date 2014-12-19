#
VARNISHD := $(shell which varnishd)
VARNISHTEST := $(shell which varnishtest)
TESTS=tests/*.vtc

check: $(TESTS)

.PHONY: check controlset snippets $(TESTS)

controlset: controlset.txt tests/vtc-from-controlset.py
	tests/vtc-from-controlset.py controlset.txt > tests/99-controlset.vtc

snippets: INSTALL.rst tests/vtc-from-snippets.py
	find tests/ -name snippet-\*vtc -exec rm "{}" \;
	cd tests && ./vtc-from-snippets.py ../INSTALL.rst

$(TESTS): controlset snippets
	${VARNISHTEST} -Dvarnishd=${VARNISHD} -Dprojectdir=$(PWD) $@
