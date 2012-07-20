TESTS=*vtc

all: $(TESTS)

.PHONY: all $(TESTS)

099-controlset.vtc: ../controlset.txt
	./vtc-from-controlset.py > 099-controlset.vtc

*.vtc:
	/usr/bin/varnishtest -Dvarnishd=/usr/sbin/varnishd -Dprojectdir=$(PWD) $@
