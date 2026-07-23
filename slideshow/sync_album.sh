#!/bin/bash
PATH=/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
echo "PATH=$PATH"
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
echo "Starting sync at: $current_time..." 
#sudo -u pi pipenv run gphotos-sync --secret /home/pi/.config/gphotos-sync/client_secret.json --album MyDigiFrame01 /home/pi/Pictures/Slides/gphotos/ >> /home/pi/gphotos-sync/sync_album.log 2<&1
#sudo -u pi pipenv run /home/pi/.local/share/virtualenvs/gphotos-sync-3r3jkhDp/bin/gphotos-sync --do-delete --flush-index --secret /home/pi/.config/gphotos-sync/client_secret.json --album MyDigiFrame01 /home/pi/Pictures/Slides/gphotos/
cd /home/pi
rclone sync gdrive:MyDigiFrame01 /home/pi/MyDigiFrame01 --transfers 2 --checkers 4
echo "==================== Done ======================"
