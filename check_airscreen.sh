#!/bin/bash

export HOME=/home/pi
export ADB_VENDOR_KEYS=/home/pi/.android
FIRESTICK_IP="192.168.0.250"
PACKAGE_NAME="com.ionitech.airscreen"
LOG_FILE="/home/pi/airscreen.log"
timestamp=$(date +"%d-%m-%Y %H:%M")

echo "================== $timestamp - START::  AirScreen Launch ===================" >> "$LOG_FILE" 
echo "HOME=$HOME"
echo "ADB_VENDOR_KEYS=$ADB_VENDOR_KEYS"

#echo "Killing Server..." >> "$LOG_FILE" 2>&1 
#adb kill-server >> "$LOG_FILE" 2>&1 #/dev/null

echo "Starting Server..." >> "$LOG_FILE" 2>&1 
adb start-server >> "$LOG_FILE" 2>&1 #/dev/null

#echo "Listing Devices..." >> "$LOG_FILE" 2>&1 
#adb devices >> "$LOG_FILE" 2>&1 #/dev/null

# Connect to Firestick
adb connect "$FIRESTICK_IP" >> "$LOG_FILE" 2>&1 #/dev/null

# Check if AirScreen is running (fallback method for Android without pidof)
RUNNING=$(adb shell ps | grep "$PACKAGE_NAME")

if [ -z "$RUNNING" ]; then
  echo "$timestamp - AirScreen is NOT running. Launching it..." >> "$LOG_FILE"
  adb shell monkey -p $PACKAGE_NAME -c android.intent.category.LAUNCHER 1 >> "$LOG_FILE" 2>&1 
else
  echo "$timestamp - AirScreen is already running." >> "$LOG_FILE"
fi

# Clean disconnect
adb disconnect "$FIRESTICK_IP" >> "$LOG_FILE" 2>&1 #/dev/null 

echo "================== $timestamp - DONE:: AirScreen Launch ==================="   >> "$LOG_FILE"

