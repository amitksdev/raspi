#!/bin/sh
cd /home/pi/slideshow/
python ./boot_lcd.py &
sudo ir-keytable -c -p nec -w /lib/udev/rc_keymaps/my_dpf.toml
cd /home/pi/slideshow/
python3 ./wifi_server.py &
