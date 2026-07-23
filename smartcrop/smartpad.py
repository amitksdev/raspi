
from PIL import Image, ImageDraw, ImageFilter, ImageOps

SCREEN_WIDTH=1440
SCREEN_HEIGHT=900

def padBlur(img):
    #print("Processing: " + str(img.size))
    #img_fg = ImageOps.contain(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    img.thumbnail((SCREEN_WIDTH, SCREEN_HEIGHT))
    img_bg = img.filter(ImageFilter.BoxBlur(205)).resize((SCREEN_WIDTH, SCREEN_HEIGHT))
    width = SCREEN_WIDTH/2 - int(img.size[0]/2)
    #print("width: " + str(int(width)))
    img_bg.paste(img, (int(width), 0))
    return img_bg

