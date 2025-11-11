#!/bin/bash
rm -f /etc/localtime
zypper --gpg-auto-import-keys ref

groupmod -g 25000 gameserver
usermod -u 25000 gameserver

chmod 0755 /usr/bin/start_server
chmod 0755 /usr/bin/cli-asa-mods

# install ruby gems
cd /usr/share/asa-ctrl
bundle.ruby3.4

if [ "$kiwi_profiles" = "development" ]; then
  # will be mounted to ease development
  rm -r /usr/share/asa-ctrl
  gem.ruby3.4 install byebug
else
  chmod 0755 /usr/share/asa-ctrl/main.rb
fi

ln -s /usr/share/asa-ctrl/main.rb /usr/bin/asa-ctrl

# This fixes a warning with Proton. The warning confused some people, but it haven't had any effect on the ASA server.
echo "d5b7b5ed-1674-497d-ad98-7437a6543312" > /etc/machine-id
chmod 644 /etc/machine-id

exit 0
