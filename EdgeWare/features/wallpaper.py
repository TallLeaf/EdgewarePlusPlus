import random as rand

from utils import utils
from utils.paths import Resource


def random_wait(settings):
    base = int(settings["wallpaperTimer"])
    vari = int(settings["wallpaperVariance"])
    return 1000 * (base + rand.randint(-vari, vari))


def start_wallpaper_rotation(root, settings):
    if len(settings["wallpaperDat"].keys()) > 1:
        root.after(random_wait(settings), lambda: rotate_wallpapers(root, settings))


def rotate_wallpapers(root, settings, previous="default"):
    selected_wallpaper = list(settings["wallpaperDat"].keys())[rand.randrange(0, len(settings["wallpaperDat"].keys()))]
    while selected_wallpaper == previous:
        selected_wallpaper = list(settings["wallpaperDat"].keys())[rand.randrange(0, len(settings["wallpaperDat"].keys()))]
    utils.set_wallpaper(Resource.ROOT / settings["wallpaperDat"][selected_wallpaper])

    base = int(settings["wallpaperTimer"])
    vari = int(settings["wallpaperVariance"])
    root.after(random_wait(settings), lambda: rotate_wallpapers(root, settings, selected_wallpaper))
