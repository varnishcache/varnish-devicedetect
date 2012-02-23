TESTS=*vtc

all: $(TESTS)

.PHONY: all $(TESTS)

*.vtc:
	/usr/bin/varnishtest -Dvarnishd=/usr/sbin/varnishd -Dprojectdir=$(PWD) $@
