#!/bin/sh

cd /home/pi/rpi-video-looper && git pull

# todo restart if changes
# reload settings by restarting the video_looper
#supervisorctl restart video_looper