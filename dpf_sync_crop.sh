#!/bin/bash
LOG_FILE="/home/pi/dpf_sync_crop.log"
cd /home/pi/slideshow/
/home/pi/slideshow/sync_album.sh >> $LOG_FILE 2<&1
#cd /home/pi/smartcrop/
#/home/pi/smartcrop/smartcrop_delta.py >> $LOG_FILE 2<&1
cd /home/pi/smartcrop/
/home/pi/smartcrop/smartpad_delta.py >> $LOG_FILE 2<&1
