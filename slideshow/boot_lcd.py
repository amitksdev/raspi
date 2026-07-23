# Code to keep checking if LCD Controller is turned off
# and turn it back ON
import RPi.GPIO as GPIO
from time import sleep

red_led = 23
power_sig = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# Power is default up, and pulled LOW to activate
GPIO.setup(power_sig, GPIO.OUT)

state = GPIO.input(red_led)
if state:
  print('Red Light appears to be ON ... sending POWER ON signal')
  GPIO.output(power_sig, GPIO.LOW)
  sleep(1)
  GPIO.output(power_sig, GPIO.HIGH)
else:
  print('Red Light appears to be OFF - do nothing')
  