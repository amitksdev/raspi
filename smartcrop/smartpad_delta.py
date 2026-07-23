#!/usr/bin/env python3
import os, sys, glob
import numpy as np
import cv2
from pathlib import Path
from shutil import copyfile
from PIL import Image, ImageOps
import importlib
from smartpad import *

GPHOTOS_DIR = "/home/pi/MyDigiFrame01/"
FEH_DIR = "/home/pi/Pictures/Slides/feh/landscape/"

# GPHOTOS_DIR = "/Users/amitsharma/axs/hobby/raspi/images/photos/"
# FEH_DIR = '/Users/amitsharma/axs/hobby/raspi/slideshow/test/output/landscape/'

Path(FEH_DIR + "processed").mkdir(parents=True, exist_ok=True)

print("Checking for new photos...")

extensions = ("png","jpg","jpeg","HEIC","PNG","JPG","JPEG",)

def trimFileName(file):
   return os.path.splitext(os.path.basename(file))[0]

gphotos_files = []
for extension in extensions:
    print("Processing : " + extension)
    gphotos_files.extend(glob.glob(GPHOTOS_DIR + "**/*." + extension, recursive=True))
#print(gphotos_files)
gphotos_filenames = [trimFileName(file) for file in gphotos_files]
#gphotos_files = glob.glob(GPHOTOS_DIR + "**/*.jpg", recursive=True)

feh_files = []
for extension in extensions:
    feh_files.extend(glob.glob(FEH_DIR + "**/*." + extension, recursive=True))

#feh_files = glob.glob(FEH_DIR + "**/*.jpg", recursive=True)
feh_filenames = [trimFileName(file) for file in feh_files]

#print(gphotos_filenames)
#print(feh_filenames)

print("Found " + str(len(gphotos_files)) + " files in gphotos.")
print("Found " + str(len(feh_files)) + " files in feh.")

# Delete removed pics
to_delete = list(set(feh_filenames) - set(gphotos_filenames))
print("Found " + str(len(to_delete)) + " deleted photos.")
d = 0
print("Deleting removed photos...")
for dfile in to_delete:
    [os.remove(f) for f in feh_files if dfile in f]
    d = d+1
print("Removed " + str(d) + " photos.")

# Process new pics
to_process = list(set(gphotos_filenames) - set(feh_filenames))
print("Found " + str(len(to_process)) + " new photos.")
to_process_files = [f for f in gphotos_files if trimFileName(f) in to_process]
total = 0
portraits = 0
print("Processing new pics...")
for file in to_process_files:
    total = total + 1
    # Check orientation
    print("Processing: " + file)
    try:    
        img = Image.open(file)
        img.draft("RGB", (1920, 1080))
        img = ImageOps.exif_transpose(img)
        print(".", end=" ")
        width, height = img.size
        print(f"file: {file}, width: {width}, height: {height}")
        if (height > width):
            portraits = portraits + 1
            # process
            img_new = padBlur(img)
            # Save cropped image
            fileName = FEH_DIR + 'processed/' + os.path.basename(file)
            img_new.convert('RGB').save(fileName.replace('.HEIC', '.JPG'))
        else:
            copyfile(file,  FEH_DIR + "/" + os.path.basename(file))
    except Exception as e:
        print("Error processing file: " + file)
        print(e)
        pass
print("")
print("Completed delta processing. Moved a total of " + str(total) + 
            " files including " + str(portraits) + " portraits")
