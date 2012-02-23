TESTS=*vtc

.PHONY: $(TESTS)

*.vtc:
	/usr/bin/varnishtest -Dvarnishd=/usr/sbin/varnishd -Dprojectdir=$(pwd) $@


