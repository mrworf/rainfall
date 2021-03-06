#!/bin/sh

DEST='/opt/rainfall'

if [ "$(whoami)" != "root" ]; then
	echo >&2 "Must run as root to install"
	exit 255
fi

if [ ! -d "$DEST" ]; then
	echo "Creating $DEST"
	mkdir -p "$DEST" || exit 255
fi
echo "Installing rainfall in $DEST"
cp server.py $DEST/ || exit 255
cp -rv modules $DEST/ || exit 255
cp -rv html $DEST/ || exit 255
echo "Installing rainfall.service"
cp rainfall.service /etc/systemd/system/ || exit 255
echo "Enabling service"
systemctl enable rainfall.service || exit 255
echo "Starting service"
# Restart will also handle the case where the service is updated
systemctl restart rainfall || exit 255
echo "Done!"
echo "Please connect to this machine's address on port 7770 to configure it"
