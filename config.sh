#!/bin/bash
test -f /.kconfig && . /.kconfig
test -f /.profile && . /.profile
echo "Configure image: [$kiwi_iname]..."

groupmod -g 25000 gameserver
usermod -u 25000 gameserver

chmod 0755 /usr/bin/start_server
chmod 0755 /usr/bin/cli-asa-mods

if [ "$kiwi_profiles" = "development" ]; then
  # will be mounted to ease development
  rm -r /usr/share/asa-ctrl
  gem.ruby3.3 install byebug
else
  chmod 0755 /usr/share/asa-ctrl/main.rb

  cd /usr/share/asa-ctrl
  bundle.ruby3.3
fi

ln -s /usr/share/asa-ctrl/main.rb /usr/bin/asa-ctrl

exit 0
