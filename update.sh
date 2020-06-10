#!/bin/sh

cd /home/pi/rpi-video-looper && git pull | grep 'Updating' &> /dev/null
if [ $? == 0 ]; then
  python3 /home/pi/rpi-video-looper/setup.py install --force
  # reload settings by restarting the video_looper
  supervisorctl restart video_looper
fi

