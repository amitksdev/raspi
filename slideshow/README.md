# Digital Photo Frame Project using Raspi

1. Aliexpress: Latumab New Kit for LP156WF1-TLA1 TV+HDMI+VGA+USB LCD LED screen Controller Driver Board
2. Salvaged LCD screen from DELL 1555
3. 

## Update boot config to uncomment gpio-ir line

```
pi@raspi-dpf-01:~ $ sudo vi /boot/config.txt

dtoverlay=gpio-ir,gpio_pin=17
```

## Install and set up ir-keytable for IR receiver

```
sudo apt-get update
sudo apt install ir-keytable

# Clear irtable:
ir-keytable -c

# Load the new keymap:
sudo ir-keytable -c -p nec -w /lib/udev/rc_keymaps/my_dpf.toml 

# Check new table present:
ir-keytable -r

#Test the new file
sudo ir-keytable -v -t -p nec
```

## Override keys settings for feh

```
Copy keys file to ~/.config/feh/
```

## Slideshow controls for Raspberry Pi

1. Added following scripts to */etc/xdg/lxsession/LXDE-pi/autostart* for startup

```
@/bin/sh /home/pi/runslideshow.sh
@/bin/sh /home/pi/slideshow/slide_control.sh
```

2. Integrated with home assistant to make REST endpoint calls for PREV/PAUSE/NEXT controls on feh

3. Add keys to ~/.config/feh/keys for remote control Return key binding to toggle_pause action

## Setup a cron job for gphotos-sync

```
*/10 * * * *  /home/pi/dpf_sync_crop.sh
```

## TODO: 

- Add AI based photo cropping
- Add Resume Power-on state after reboot



