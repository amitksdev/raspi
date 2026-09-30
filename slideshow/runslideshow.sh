#!/bin/sh
set -o allexport
. /home/pi/slideshow/slideshow.conf
set +o allexport

echo "-----------------------------" >> $LOGFILE
echo "$(date)" >> $LOGFILE
echo "Starting $NAME..." >> $LOGFILE
echo "Photo time interval: $SLIDE_INTERVAL" >> $LOGFILE
echo "Photo dir: $PHOTO_DIR" >> $LOGFILE
echo "Show Date Str: $SHOW_DATE" >> $LOGFILE
echo "Reload Interval: $RELOAD_INTERVAL" >> $LOGFILE
echo "Active Playlist: $ACTIVE_PLAYLIST" >> $LOGFILE

xset -dpms
xset s off
xset s noblank

echo "Starting Python Server..." >> $LOGFILE
cd /home/pi/slideshow
python3 wifi_server.py &
python3 mqtt-client.py &
echo "Done!" >> $LOGFILE

while true; do
    echo "Starting Slideshow..." >> $LOGFILE

    feh --recursive -z -Z -D $SLIDE_INTERVAL \
        --reload 4200 \
        --filelist $ACTIVE_PLAYLIST \
        --hide-pointer \
        --auto-rotate \
        --fullscreen \
        --zoom fill \
        --font "Roboto-Medium/20" \
        --draw-tinted \
        --info "/home/pi/slideshow/get_exif.sh %F %u %l" &

    FEH_PID=$!
    echo "feh PID: $FEH_PID" >> $LOGFILE
    echo $FEH_PID > /tmp/feh.pid

    wait $FEH_PID

    EXIT_CODE=$?
    echo "Slideshow exited with code $EXIT_CODE" >> $LOGFILE

    sleep 5
done
