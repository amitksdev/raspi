#!/bin/bash

# This script will be called by feh with one argument: the image path
# We don't use that, but we could if we want image-specific logic

API_KEY="e5tJzCPkrT3gMNJD4-m4DULU3fHYQx5HLr0IC5KZ_Hw"
OCTO_URL="http://octopi.local/api/job"

# Get the job info
JOB_JSON=$(curl -s -H "X-Api-Key: $API_KEY" "$OCTO_URL")

state=$(echo "$JOB_JSON" | jq -r '.state')
FILE_NAME=$(echo "$JOB_JSON" | jq -r '.job.file.name // "No job"')
progress=$(echo "$JOB_JSON" | jq -r '.progress.completion // 0' | awk '{printf "%.1f", $1}')
ELAPSED=$(echo "$JOB_JSON" | jq -r '.progress.printTime // 0' | awk '{printf "%.0f", $1 / 60}')
REMAINING=$(echo "$JOB_JSON" | jq -r '.progress.printTimeLeft // 0' | awk '{printf "%.0f", $1 / 60}')

# Convert float to int
progress=${progress%.*}
#progress=68

generate_progress_bar() {
  local progress=$1
  local width=20
  local done=$(( progress * width / 100 ))
  local left=$(( width - done ))
  local bar=$(printf '%0.s#' $(seq 1 $done))
  bar+=$(printf '%0.s-' $(seq 1 $left))
  echo "[${bar}] ${progress}%"
}

print_line() {
  local left_text="$1"
  local right_text="$2"
  local total_width=49

  local left_width=$(( total_width - ${#left_text} - ${#right_text} ))

  # Ensure left_width isn't negative (in case inputs are too long)
  if (( left_width < 0 )); then
    left_width=1
  fi

  printf " %s%*s%s  " "$left_text" "$left_width" "" "$right_text"
}

progress_bar=$(generate_progress_bar $progress)


# === Fetch Printer Temp Info ===
OCTO_URL="http://octopi.local/api/printer"
PRINTER_JSON=$(curl -s -H "X-Api-Key: $API_KEY" "$OCTO_URL")

HOTEND_ACTUAL=$(echo "$PRINTER_JSON" | jq '.temperature.tool0.actual // 0' | awk '{printf "%.0f", $1}')
HOTEND_TARGET=$(echo "$PRINTER_JSON" | jq '.temperature.tool0.target // 0' | awk '{printf "%.0f", $1}')

BED_ACTUAL=$(echo "$PRINTER_JSON" | jq '.temperature.bed.actual // 0' | awk '{printf "%.0f", $1}')
BED_TARGET=$(echo "$PRINTER_JSON" | jq '.temperature.bed.target // 0' | awk '{printf "%.0f", $1}')

#REMAINING=9000
#HOTEND_ACTUAL=112
#HOTEND_TARGET=33224
#BED_ACTUAL=48
#BED_TARGET=25645

#if [[ "$state" == "Operational" || "$state" == "Ready" || "$state" == "Offline" ]]; then
  print_line "Progress: ${progress}%"  "Time: ${REMAINING}m left"
  printf "\n"
  print_line  "Hotend: ${HOTEND_ACTUAL}/${HOTEND_TARGET}°C" "Bed: ${BED_ACTUAL}/${BED_TARGET}°C"
#fi
