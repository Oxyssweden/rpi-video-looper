#!/bin/sh

cd /home/pi/rpi-video-looper && git pull | grep 'Updating' &> /dev/null
if [ $? == 0 ]; then
  # reload settings by restarting the video_looper
  supervisorctl restart video_looper
fi

