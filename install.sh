#!/bin/sh

# Error out if anything fails.
set -e

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./install.sh"
  exit 1
fi


echo "Installing dependencies..."
echo "=========================="
apt update && apt -y install python3 python3-pip supervisor

echo "Installing video_looper program..."
echo "=================================="

# change the directoy to the script location
cd "$(dirname "$0")"

pip3 install setuptools inputs
python3 setup.py install --force

cp ./assets/video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="

cp ./assets/video_looper.conf /etc/supervisor/conf.d/
cp ./assets/vlc.conf /etc/supervisor/conf.d/

service supervisor restart

echo "Finished!"
