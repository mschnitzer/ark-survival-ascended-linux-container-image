#!/bin/bash
test -f /.kconfig && . /.kconfig
test -f /.profile && . /.profile
echo "Configure image: [$kiwi_iname]..."

groupmod -g 25000 gameserver
usermod -u 25000 gameserver

chmod 0755 /usr/bin/start_server

exit 0
