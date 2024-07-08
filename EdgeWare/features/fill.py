import hashlib
import logging
import os
import random as rand
import shutil
import time

from utils.paths import Resource

FILE_TYPES = ["png", "jpg", "jpeg"]  # recognized file types for replace
LIVE_FILL_THREADS = 0  # count of live threads for hard drive filling


# fills drive with copies of images from /resource/img/
#   only targets User folders; none of that annoying elsaware shit where it fills folders you'll never see
#   can only have 8 threads live at once to avoid 'memory leak'
def fill_drive(settings):
    global LIVE_FILL_THREADS
    LIVE_FILL_THREADS += 1
    doc_path = settings.DRIVE_PATH
    images = []
    logging.info(f"starting drive fill to {doc_path}")
    for img in os.listdir(Resource.IMAGE):
        if not img.split(".")[-1] == "ini":
            images.append(img)
    for root, dirs, files in os.walk(doc_path):
        # tossing out directories that should be avoided
        for obj in list(dirs):
            if obj in settings.AVOID_LIST or obj[0] == ".":
                dirs.remove(obj)
        for i in range(rand.randint(3, 6)):
            index = rand.randint(0, len(images) - 1)
            t_obj = str(time.time() * rand.randint(10000, 69420)).encode(encoding="ascii", errors="ignore")
            pth = os.path.join(root, hashlib.md5(t_obj).hexdigest() + "." + str.split(images[index], ".")[len(str.split(images[index], ".")) - 1].lower())
            shutil.copyfile(Resource.IMAGE / images[index], pth)
        time.sleep(float(settings.FILL_DELAY) / 100)
    LIVE_FILL_THREADS -= 1


# seeks out folders with a number of images above the replace threshold and replaces all images with /resource/img/ files
def replace_images(settings):
    global REPLACING_LIVE
    REPLACING_LIVE = True
    doc_path = settings.DRIVE_PATH
    image_names = []
    for img in os.listdir(Resource.IMAGE):
        if not img.split(".")[-1] == "ini":
            image_names.append(Resource.IMAGE / img)
    for root, dirs, files in os.walk(doc_path):
        for obj in list(dirs):
            if obj in settings.AVOID_LIST or obj[0] == ".":
                dirs.remove(obj)
        to_replace = []
        # ignore any folders with fewer items than the replace threshold
        if len(files) >= settings.REPLACE_THRESHOLD:
            # if folder has enough items, check how many of them are images
            for obj in files:
                if obj.split(".")[-1] in FILE_TYPES:
                    if os.path.exists(os.path.join(root, obj)):
                        to_replace.append(os.path.join(root, obj))
            # if has enough images, finally do replacing
            if len(to_replace) >= settings.REPLACE_THRESHOLD:
                for obj in to_replace:
                    shutil.copyfile(image_names[rand.randrange(len(image_names))], obj, follow_symlinks=True)
    # never turns off threadlive variable because it should only need to do this once
