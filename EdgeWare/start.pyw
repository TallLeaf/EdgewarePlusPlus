import urllib
import hashlib
import os
import subprocess
import multiprocessing
import ast
import time
import webbrowser
import zipfile
import shutil
import json
import random as rand
import threading as thread
import tkinter as tk
import logging
import sys
import requests
import pystray
import playsound as ps
from PIL import Image
from bs4 import BeautifulSoup
from dataclasses import dataclass
from tkinter import messagebox, simpledialog
from pathlib import Path
from utils import utils
from utils.paths import Data, Defaults, Process, Resource
from utils.settings import load_settings

PATH = Path(__file__).parent
os.chdir(PATH)

utils.init_logging(logging, 'ew_start', 'start')

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)
logging.info(f'args: {SYS_ARGS}')

#load settings, if first run open options, then reload options from file
settings = load_settings(logging)
if not settings['is_configed']==1:
    logging.info('running config for first setup, is_configed flag is false.')
    subprocess.run([sys.executable, Process.CONFIG])
    logging.info('reloading settings')
    settings = load_settings(logging)

AVOID_LIST = ['EdgeWare', 'AppData'] #default avoid list for fill/replace
FILE_TYPES = ['png', 'jpg', 'jpeg'] #recognized file types for replace

LIVE_FILL_THREADS = 0 #count of live threads for hard drive filling
PLAYING_AUDIO = False #audio thread flag
REPLACING_LIVE = False #replace thread flag
HAS_PROMPTS = False #can use prompts flag
MITOSIS_LIVE = False #flag for if the mitosis mode popup has been spawned

#default data for generating working default asset resource folder
DEFAULT_WEB = '{"urls":["https://duckduckgo.com/"], "args":["?q=why+are+you+gay"]}'
DEFAULT_PROMPT = '{"moods":["no moods"], "freqList":[100], "minLen":1, "maxLen":1, "no moods":["no prompts"]}'
DEFAULT_DISCORD = 'Playing with myself~'

#naming each used variable from config for ease of use later
#annoyance vars
DELAY = int(settings['delay'])
POPUP_CHANCE = int(settings['popupMod'])
AUDIO_CHANCE = int(settings['audioMod'])
PROMPT_CHANCE = int(settings['promptMod'])
VIDEO_CHANCE = int(settings['vidMod'])
WEB_CHANCE = int(settings['webMod'])
CAP_POP_CHANCE = int(settings['capPopChance'])

VIDEOS_ONLY = int(settings['onlyVid']) == 1

PANIC_DISABLED = int(settings['panicDisabled']) == 1

AUDIO_CAP = int(settings['maxAudioBool']) == 1
AUDIO_MAX = int(settings['maxAudio'])
VIDEO_CAP = int(settings['maxVideoBool']) == 1
VIDEO_MAX = int(settings['maxVideos'])
AUDIO_NUMBER = 0
VIDEO_NUMBER = 0

#mode vars
SHOW_ON_DISCORD = int(settings['showDiscord']) == 1
LOADING_FLAIR = int(settings['showLoadingFlair']) == 1
DESKTOP_ICONS = int(settings['desktopIcons']) == 1

DOWNLOAD_ENABLED = int(settings['downloadEnabled']) == 1
USE_WEB_RESOURCE = int(settings['useWebResource']) == 1

MAX_FILL_THREADS = int(settings['maxFillThreads'])

HIBERNATE_MODE = int(settings['hibernateMode']) == 1
HIBERNATE_MIN = int(settings['hibernateMin'])
HIBERNATE_MAX = int(settings['hibernateMax'])
WAKEUP_ACTIVITY = int(settings['wakeupActivity'])
HIBERNATE_TYPE = settings['hibernateType']
HIBERNATE_TRUTH = settings['hibernateType']
HIBERNATE_LENGTH = int(settings['hibernateLength'])
FIX_WALLPAPER = int(settings['fixWallpaper']) == 1

FILL_MODE = int(settings['fill']) == 1
FILL_DELAY = int(settings['fill_delay'])
REPLACE_MODE = int(settings['replace']) == 1
REPLACE_THRESHOLD = int(settings['replaceThresh'])

ROTATE_WALLPAPER = int(settings['rotateWallpaper']) == 1

MITOSIS_MODE = int(settings['mitosisMode']) == 1
LOWKEY_MODE = int(settings['lkToggle']) == 1

TIMER_MODE = int(settings['timerMode']) == 1

DRIVE_PATH = settings['drivePath']

LANCZOS_MODE = int(settings['antiOrLanczos']) == 1

PUMP_SCARE_OFFSET = int(settings['pumpScareOffset'])

VLC_MODE = int(settings['vlcMode']) == 1

SINGLE_MODE = int(settings['singleMode']) == 1

MOOD_OFF = int(settings['toggleMoodSet']) == 1

CORRUPTION_MODE = int(settings['corruptionMode']) == 1
CORRUPTION_FADE = settings['corruptionFadeType']
CORRUPTION_TRIGGER = settings['corruptionTrigger']
#adding all three as individual vars instead of checking for trigger type because of an idea: randomized corruption per-launch?
CORRUPTION_TIME = settings['corruptionTime']
CORRUPTION_POPUPS = settings['corruptionPopups']
CORRUPTION_LAUNCHES = settings['corruptionLaunches']

CORRUPTION_DEVMODE = int(settings['corruptionDevMode']) == 1
CORRUPTION_WALLCYCLE = int(settings['corruptionWallpaperCycle']) == 1
CORRUPTION_THEMECYCLE = int(settings['corruptionThemeCycle']) == 1
CORRUPTION_PURITY = int(settings['corruptionPurityMode']) == 1
CORRUPTION_FULL = int(settings['corruptionFullPerm']) == 1

PAGESTART = 0

MOOD_ID = '0'
if not MOOD_OFF:
    try:
        if os.path.isfile(Resource.INFO):
            info_dict = ''
            with open(Resource.INFO) as r:
                info_dict = json.loads(r.read())
                if 'id' in info_dict:
                    MOOD_ID = info_dict['id'] if info_dict['id'] else '0'
        if MOOD_ID == '0':
            im = str(len(os.listdir(Resource.IMAGE))) if os.path.exists(Resource.IMAGE) else '0'
            au = str(len(os.listdir(Resource.AUDIO))) if os.path.exists(Resource.AUDIO) else '0'
            vi = str(len(os.listdir(Resource.VIDEO))) if os.path.exists(Resource.VIDEO) else '0'
            wa = 'w' if os.path.isfile(Resource.WALLPAPER) else 'x'
            sp = 's' if Resource.SPLASH else 'x'
            di = 'd' if os.path.isfile(Resource.DISCORD) else 'x'
            ic = 'i' if os.path.isfile(Resource.ICON) else 'x'
            co = 'c' if os.path.isfile(Resource.CORRUPTION) else 'x'
            MOOD_ID = im + au + vi + wa + sp + di + ic + co
    except Exception as e:
        messagebox.showerror('Launch Error', 'Could not launch Edgeware due to setting mood ID issues.\n[' + str(e) + ']')
        logging.fatal(f'failed to set mood id.\n\tReason:{e}')
        os.kill(os.getpid(), 9)
    logging.info(f'mood id: {MOOD_ID}')

hiberWait = thread.Event()
wallpaperWait = thread.Event()
runningHibernate = thread.Event()
pumpScareAudio = thread.Event()

#start init portion, check resources, config, etc.
try:
    if not os.path.exists(Resource.ROOT):
        logging.warning('no resource folder found')
        pth = 'pth-default_ignore'
        #selecting first zip found in script folder
        for obj in os.listdir(PATH):
            try:
                if obj.split('.')[-1].lower() == 'zip':
                    logging.info(f'found zip file {obj}')
                    pth = os.path.join(PATH, obj)
                    break
            except:
                print(f'{obj} is not a zip file.')
        #if found zip unpack
        if not pth == 'pth-default_ignore':
           with zipfile.ZipFile(pth, 'r') as obj:
                logging.info('extracting resources from zip')
                obj.extractall(Resource.ROOT)
        else:
            #if no zip found, use default resources
            logging.warning('no zip file found, generating resource folder from default assets.')
            for obj in [Resource.ROOT, Resource.AUDIO, Resource.IMAGE, Resource.VIDEO]:
                os.mkdir(obj)
            shutil.copyfile(Defaults.WALLPAPER, Resource.WALLPAPER)
            shutil.copyfile(Defaults.IMAGE, Resource.IMAGE / 'img0.png', follow_symlinks=True)
            if not os.path.exists(Resource.DISCORD):
                with open(Resource.DISCORD, 'w') as f:
                    f.write(DEFAULT_DISCORD)
            if not os.path.exists(Resource.PROMPT):
                with open(Resource.PROMPT, 'w') as f:
                    f.write(DEFAULT_PROMPT)
            if not os.path.exists(Resource.WEB):
                with open(Resource.WEB, 'w') as f:
                    f.write(DEFAULT_WEB)
except Exception as e:
    messagebox.showerror('Launch Error', 'Could not launch Edgeware due to resource zip unpacking issues.\n[' + str(e) + ']')
    logging.fatal(f'failed to unpack resource zip or read default resources.\n\tReason:{e}')
    os.kill(os.getpid(), 9)

#writing corruption file if it doesn't exist/wiping it if the mode isn't on launch
if CORRUPTION_MODE:
    try:
        if not os.path.exists(Data.ROOT):
            os.mkdir(Data.ROOT)
            #the launches will reset when the user specifies in the config, or a new pack is loaded
            if not os.path.exists(Data.CORRUPTION_LAUNCHES):
                with open(Data.CORRUPTION_LAUNCHES, 'w') as f:
                    f.write('0')
            with open(Data.CORRUPTION_POPUPS, 'w') as f:
                f.write('0')
            with open(Data.CORRUPTION_LEVEL, 'w') as f:
                f.write('0')
    except Exception as e:
        print(f'error loading corruption. {e}')
        logging.warning(f'failed to initialize corruption properly.\n\tReason: {e}')

HAS_PROMPTS = False
WEB_JSON_FOUND = False
if os.path.exists(Resource.PROMPT):
    logging.info('found prompt.json')
    HAS_PROMPTS = True
if os.path.exists(Resource.WEB):
    logging.info('found web.json')
    WEB_JSON_FOUND = True

WEB_DICT = {}
if os.path.exists(Resource.WEB):
    with open(Resource.WEB, 'r') as webF:
        WEB_DICT = json.loads(webF.read())

try:
    AVOID_LIST = settings['avoidList'].split('>')
except Exception as e:
    logging.warning(f'failed to set avoid list\n\tReason: {e}')

#checking presence of resources
try:
    HAS_IMAGES = len(os.listdir(Resource.IMAGE)) > 0
    logging.info('image resources found')
except Exception as e:
    logging.warning(f'no image resource folder found\n\tReason: {e}')
    print('no image folder found')
    HAS_IMAGES = False

VIDEOS = []
try:
    for vid in os.listdir(Resource.VIDEO):
        VIDEOS.append(Resource.VIDEO / vid)
    logging.info('video resources found')
except Exception as e:
    logging.warning(f'no video resource folder found\n\tReason: {e}')
    print('no video folder found')

AUDIO = []
MOOD_AUDIO = []
try:
    HAS_AUDIO = os.path.exists(Resource.AUDIO)
    for aud in os.listdir(Resource.AUDIO):
        AUDIO.append(Resource.AUDIO / aud)
    logging.info('audio resources found')
except Exception as e:
    logging.warning(f'no audio resource folder found\n\tReason: {e}')
    print('no audio folder found')

CAPTIONS = os.path.exists(Resource.CAPTIONS)

HAS_WEB = WEB_JSON_FOUND and len(WEB_DICT['urls']) > 0
#end of checking resource presence

#set discord status if enabled
if SHOW_ON_DISCORD:
    try:
        subprocess.Popen([sys.executable, Process.DISCORD])
    except Exception as e:
        logging.warning(f'failed to start discord status background task\n\tReason: {e}')
        print('failed to start discord status')

#making missing desktop shortcuts
if DESKTOP_ICONS:
    if not utils.does_desktop_shortcut_exist('Edgeware'):
        if os.path.isfile(Resource.START):
            utils.make_shortcut('Edgeware', Process.START, Resource.START)
        else:
            utils.make_shortcut('Edgeware', Process.START, Defaults.ICON)
    if not utils.does_desktop_shortcut_exist('Config'):
        if os.path.isfile(Resource.CONFIG):
            utils.make_shortcut('Config', Process.CONFIG, Resource.CONFIG)
        else:
            utils.make_shortcut('Config', Process.CONFIG, Defaults.CONFIG_ICON)
    if not utils.does_desktop_shortcut_exist('Panic'):
        if os.path.isfile(Resource.PANIC):
            utils.make_shortcut('Panic', Process.PANIC, Resource.PANIC)
        else:
            utils.make_shortcut('Panic', Process.PANIC, Defaults.PANIC_ICON)

if LOADING_FLAIR and (__name__ == "__main__"):
    logging.info('started loading flair')
    if Resource.SPLASH:
        if LANCZOS_MODE:
            logging.info('using lanczos for loading flair')
            subprocess.run([sys.executable, Process.STARTUP, '-custom', '-lanczos'])
        else:
            subprocess.run([sys.executable, Process.STARTUP, '-custom'])
    else:
        if LANCZOS_MODE:
            logging.info('using lanczos for loading flair')
            subprocess.run([sys.executable, Process.STARTUP, '-lanczos'])
        else:
            subprocess.run([sys.executable, Process.STARTUP])

#set wallpaper
if not HIBERNATE_MODE:
    logging.info('set user wallpaper to default wallpaper.png')
    utils.set_wallpaper(Resource.WALLPAPER)

#selects url to be opened in new tab by web browser
def url_select(arg:int):
    logging.info(f'selected url {arg}')
    return WEB_DICT['urls'][arg] + WEB_DICT['args'][arg].split(',')[rand.randrange(len(WEB_DICT['args'][arg].split(',')))]

#class to handle window for tray icon
class TrayHandler:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Edgeware')
        self.timer_mode = settings['timerMode'] == 1

        self.option_list = [pystray.MenuItem('Edgeware Menu', print), pystray.MenuItem('Panic', self.try_panic)]
        if settings['toggleHibSkip']:
            self.option_list.append(pystray.MenuItem('Skip to Hibernate', self.hib_skip))

        if os.path.isfile(Resource.ICON):
            self.tray_icon = pystray.Icon('Edgeware',
                                        Image.open(Resource.ICON),
                                        'Edgeware',
                                        self.option_list)
        else:
            self.tray_icon = pystray.Icon('Edgeware',
                                        Image.open(Defaults.ICON),
                                        'Edgeware',
                                        self.option_list)

        self.root.withdraw()

        self.password_setup()

    def hib_skip(self):
        if HIBERNATE_MODE:
            try:
                hiberWait.set()
            except Exception as e:
                logging.critical(f'failed to skip to hibernate start. {e}')

    def password_setup(self):
        if self.timer_mode:
            try:
                utils.show_file(Data.PASS_HASH)
                with open(Data.PASS_HASH, 'r') as file:
                    self.hashedPass = file.readline()
                utils.hide_file(Data.PASS_HASH)
            except:
                #no hash found
                self.hashedPass = None

    def try_panic(self):
        logging.info('attempting tray panic')
        if not PANIC_DISABLED:
            if self.timer_mode:
                pass_ = simpledialog.askstring('Panic', 'Enter Panic Password')
                t_hash = None if pass_ is None or pass_ == '' else hashlib.sha256(pass_.encode(encoding='ascii', errors='ignore')).hexdigest()
                if t_hash == self.hashedPass:
                    #revealing hidden files
                    try:
                        utils.show_file(Data.PASS_HASH)
                        utils.show_file(Data.HID_TIME)
                        os.remove(Data.PASS_HASH)
                        os.remove(Data.HID_TIME)
                        subprocess.Popen([sys.executable, Process.PANIC])
                    except:
                        logging.critical('panic initiated due to failed pass/timer check')
                        self.tray_icon.stop()
                        subprocess.Popen([sys.executable, Process.PANIC])
            else:
                logging.warning('panic initiated from tray command')
                self.tray_icon.stop()
                subprocess.Popen([sys.executable, Process.PANIC])

    def move_to_tray(self):
        self.tray_icon.run(tray_setup)
        logging.info('tray handler thread running')

def tray_setup(icon):
    icon.visible = True

#main function, probably can do more with this but oh well i'm an idiot so
def main():
    logging.info('entered main function')
    #set up tray icon
    tray = TrayHandler()

    #if tray icon breaks again this is why
    #idk why it works 50% of the time when it works and sometimes just stops working
    thread.Thread(target=tray.move_to_tray, daemon=True).start()

    #timer handling, start if there's a time left file
    if os.path.exists(Data.HID_TIME):
        thread.Thread(target=do_timer).start()

    #max value handling creation/cleaning
    if not os.path.exists(Data.ROOT):
        os.mkdir(Data.ROOT)
    try:
        with open(Data.MAX_VIDEOS, 'w') as f:
            f.write('0')
        with open(Data.MAX_SUBLIMINALS, 'w') as f:
            f.write('0')
        with open(Data.HIBERNATE, 'w') as f:
            f.write('0')
        if not MOOD_OFF:
            with open(Data.MEDIA_IMAGES, 'w') as f:
                f.write('0')
            with open(Data.MEDIA_VIDEO, 'w') as f:
                f.write('0')
    except Exception as e:
        logging.warning(f'failed to clean or create data files\n\tReason: {e}')
        print('failed to clean or create data files')

    update_media()

    #do downloading for booru stuff
    if settings.get('downloadEnabled') == 1:
        booru_downloader:BooruDownloader = BooruDownloader(settings.get('booruName'), settings.get('tagList').split('>'))

        logging.info('start booru_method thread')
        if settings.get('downloadMode') == 'First Page':
            thread.Thread(target=lambda: booru_downloader.download(min_score=int(settings.get('booruMinScore'))), daemon=True).start()
        elif settings.get('downloadMode') == 'Random Page':
            thread.Thread(target=lambda: booru_downloader.download_random(min_score=int(settings.get('booruMinScore'))), daemon=True).start()
        else:
            thread.Thread(target=lambda: booru_downloader.download_all(min_score=int(settings.get('booruMinScore'))), daemon=True).start()

    #do downloading from web resource folder
    if USE_WEB_RESOURCE:
        logging.info('start download_web_resources thread')
        thread.Thread(target=download_web_resources).start()

    #start thread for wallpaper timer
    if ROTATE_WALLPAPER:
        logging.info('start rotate_wallpapers thread')
        thread.Thread(target=rotate_wallpapers).start()

    #run annoyance thread or do hibernate mode
    if HIBERNATE_MODE:
        logging.info('starting in hibernate mode')
        triggerThread = thread.Thread(target=checkWallpaperStatus)
        if FIX_WALLPAPER:
            triggerThread.start()
        while True:
            hiberWait.clear()
            waitTime = rand.randint(HIBERNATE_MIN, HIBERNATE_MAX)
            if HIBERNATE_TRUTH == 'Chaos':
                try:
                    global HIBERNATE_TYPE
                    HIBERNATE_TYPE = rand.choice(['Original', 'Spaced', 'Glitch', 'Ramp', 'Pump-Scare'])
                    with open(Data.CHAOS_TYPE, 'w') as f:
                        f.write(HIBERNATE_TYPE)
                    print(f'hibernate type is chaos, and has switched to {HIBERNATE_TYPE}')
                except Exception as e:
                    logging.warning(f'failed to successfully run chaos hibernate.\n\tReason: {e}')
            hiberWait.wait(float(waitTime))
            runningHibernate.clear()
            if HIBERNATE_TYPE != 'Pump-Scare':
                utils.set_wallpaper(Resource.WALLPAPER)
                wallpaperWait.clear()
            if HIBERNATE_TYPE == 'Original':
                try:
                    print(f'running original hibernate. number of popups estimated between {int(WAKEUP_ACTIVITY / 2)} and {WAKEUP_ACTIVITY}.')
                    for i in range(0, rand.randint(int(WAKEUP_ACTIVITY / 2), WAKEUP_ACTIVITY)):
                        roll_for_initiative()
                except Exception as e:
                    logging.warning(f'failed to successfully run {HIBERNATE_TYPE} hibernate.\n\tReason: {e}')
            if HIBERNATE_TYPE == 'Spaced':
                try:
                    endTime = time.monotonic() + float(HIBERNATE_LENGTH)
                    print(f'running spaced hibernate. current time is {time.monotonic()}, end time is {endTime}')
                    while time.monotonic() < endTime:
                        roll_for_initiative()
                        time.sleep(float(DELAY) / 1000.0)
                except Exception as e:
                    logging.warning(f'failed to successfully run {HIBERNATE_TYPE} hibernate.\n\tReason: {e}')
            if HIBERNATE_TYPE == 'Glitch':
                try:
                    glitchSleep = HIBERNATE_LENGTH / WAKEUP_ACTIVITY
                    totalTime = time.monotonic()
                    endTime = time.monotonic() + float(HIBERNATE_LENGTH)
                    print(f'running glitch hibernate. the end time is {endTime} with {WAKEUP_ACTIVITY} popups, total time is {HIBERNATE_LENGTH} and glitchSleep median is {glitchSleep}')
                    for i in range(0, WAKEUP_ACTIVITY):
                        if endTime <= time.monotonic():
                            break
                        rgl = rand.randint(1,4)
                        rt = rand.randint(2,4)
                        if rgl == 1 and (endTime - totalTime) > glitchSleep:
                            time.sleep(float(glitchSleep))
                            totalTime = totalTime + glitchSleep
                        if rgl == 2 and (endTime - totalTime) > (glitchSleep / rt):
                            time.sleep(float(glitchSleep / rt))
                            totalTime = totalTime + (glitchSleep / rt)
                        if rgl == 3 and (endTime - totalTime) > (glitchSleep * rt):
                            time.sleep(float(glitchSleep * rt))
                            totalTime = totalTime + (glitchSleep * rt)
                        logging.info(f'time {endTime - totalTime}, rgl {rgl}, rt {rt}')
                        roll_for_initiative()
                    if endTime > time.monotonic(): time.sleep(float(endTime - time.monotonic()))
                    roll_for_initiative()
                except Exception as e:
                    logging.warning(f'failed to successfully run {HIBERNATE_TYPE} hibernate.\n\tReason: {e}')
            if HIBERNATE_TYPE == 'Ramp':
                try:
                    print(f'hibernate type is ramp. ramping up speed for {HIBERNATE_LENGTH}, max speed is {DELAY*0.9}, and popups at max speed is {WAKEUP_ACTIVITY}')
                    endTime = time.monotonic() + float(HIBERNATE_LENGTH)
                    x = HIBERNATE_LENGTH / 4
                    accelerate = 1
                    while True:
                        if (time.monotonic() > endTime) and ((DELAY/1000) + 0.1 > rampSleep):
                            break
                        if ((endTime - time.monotonic()) / HIBERNATE_LENGTH) > 0.5:
                            accelerate = accelerate * 1.10
                        else:
                            accelerate = accelerate * 1.05
                        x = x / accelerate
                        rampSleep = (DELAY / 1000) + x
                        #logging.info(f'rampsleep {rampSleep} accelerate {accelerate}, {((endTime - time.monotonic()) / HIBERNATE_LENGTH)} time left {endTime - time.monotonic()}')
                        roll_for_initiative()
                        time.sleep(float(rampSleep))
                    for i in range(0, WAKEUP_ACTIVITY):
                        roll_for_initiative()
                        time.sleep(float(DELAY*0.9) / 1000.0)
                except Exception as e:
                    logging.warning(f'failed to successfully run {HIBERNATE_TYPE} hibernate.\n\tReason: {e}')
            if HIBERNATE_TYPE == 'Pump-Scare':
                try:
                    print(f'hibernate type is pump-scare.')
                    roll_for_initiative()
                except Exception as e:
                    logging.warning(f'failed to successfully run {HIBERNATE_TYPE} hibernate.\n\tReason: {e}')
            time.sleep(0.5)
            runningHibernate.set()

    else:
        logging.info('starting annoyance loop')
        annoyance()



def checkWallpaperStatus():
    with open(Data.HIBERNATE, 'r') as f:
        while True:
            runningHibernate.wait()
            print('hibernate processing is over, waiting for popups to close')
            while True:
                if not runningHibernate.is_set():
                    break
                if not wallpaperWait.is_set():
                        f.seek(0)
                        i = int(f.readline())
                        if i < 1:
                            wallpaperWait.set()
                            print('hibernate popups are all dead')
                            utils.set_wallpaper(Defaults.PANIC_WALLPAPER)
                            break

#just checking %chance of doing annoyance options
def do_roll(mod:float) -> bool:
    if mod >= 100:
        return True

    if mod <= 0:
        return False

    return mod > (rand.random() * 100)

#booru handling class
class BooruDownloader:
    def __init__(self, booru:str, tags:list[str]=None):

        self.extension_list:list[str] = ['jpg', 'jpeg', 'png', 'gif']

        self.exception_list:dict[str, BooruScheme] = {
            'rule34':BooruScheme('rule34',
                                 'https://www.rule34.xxx/index.php?page=post&s=list&tags=',
                                 '/thumbnails/',
                                 '/',
                                 'thumbnail_',
                                 '.',
                                 'score:',
                                 ' ',
                                 'https://us.rule34.xxx//images/{code_actual}/')
        }

        self.booru          = booru
        self.tags           = '+'.join(tags) if tags is not None else 'all'
        logging.info(f'tags={self.tags}')
        self.post_per_page  = 0
        self.page_count     = 0
        self.booru_scheme   = BooruScheme(self.booru) if self.booru not in self.exception_list.keys() else self.exception_list.get(self.booru)
        self.max_page       = int(self.get_page_count())
        self.finalNum       = 20
        self.numDownloads   = 0
    def imgs_on_end(self,min_score:int = None):
        num = 0
        self._page_url = f'{self.booru_scheme.booru_search_url.format(booru_name=self.booru)}{self.tags}&pid={(self.max_page-1)*self.post_per_page}'
        self._html = requests.get(self._page_url).text
        self._soup = BeautifulSoup(self._html, 'html.parser')
        for image in self._soup.find_all('img'):
            try:
                self._src:str     = image.get('src')
                self._code_actual = int(self.pick_value(self._src,
                                                    f'{self.booru_scheme.preview_thumb_id_start}',
                                                    f'{self.booru_scheme.preview_thumb_id_end}'))
                self._file_name   = self.pick_value(self._src,
                                                f'{self.booru_scheme.preview_thumb_name_start}',
                                                f'{self.booru_scheme.preview_thumb_name_end}')

                self._title:str = image.get('title')
                self._start     = int(self._title.index(f'{self.booru_scheme.score_start}') + len(self.booru_scheme.score_start))
                self._end       = self._title.index(f'{self.booru_scheme.score_end}', self._start)
                self._score     = int(self._title[self._start:self._end])

                if min_score is not None and self._score < min_score:
                    print(f'(score {self._score} too low) skipped {self._src}')
                    continue
            except Exception as e:
                print(f'skipped: {e}')
                continue
            for extension in self.extension_list:
                try:
                    self._file_name_full = f'{self._file_name}.{extension}'
                    self._full_url = f'{self.booru_scheme.raw_image_url.format(booru=self.booru, code_actual=self._code_actual)}{self._file_name_full}'
                    num += 1

                    break
                except:
                    continue
        return num-1
    
    def download(self, page_start:int = 0, page_end:int = -1, min_score:int = None) -> None:
        if page_end == -1:
            page_end = self.max_page
        self._page_start = max(page_start, 0)
        self._page_start = min(self._page_start, self.max_page)
        imgnum = 0
        startnum = self.imgs_on_end(min_score=int(settings.get('booruMinScore')))
        self._page_end   = min(page_end, self.max_page+1) if page_end >= self._page_start else self._page_start + 1
        
        for page_index in range(self._page_start, self._page_end):
            imgnum = startnum + ((page_index-1)*20)
            self._page_url = f'{self.booru_scheme.booru_search_url.format(booru_name=self.booru)}{self.tags}&pid={(page_end-page_index)*self.post_per_page}'
            logging.info(f'downloadpageurl={self._page_url}')
            self._html = requests.get(self._page_url).text
            self._soup = BeautifulSoup(self._html, 'html.parser')

            for image in self._soup.find_all('img'):
                try:
                    self._src:str     = image.get('src')
                    self._code_actual = int(self.pick_value(self._src,
                                                       f'{self.booru_scheme.preview_thumb_id_start}',
                                                       f'{self.booru_scheme.preview_thumb_id_end}'))
                    self._file_name   = self.pick_value(self._src,
                                                   f'{self.booru_scheme.preview_thumb_name_start}',
                                                   f'{self.booru_scheme.preview_thumb_name_end}')

                    self._title:str = image.get('title')
                    self._start     = int(self._title.index(f'{self.booru_scheme.score_start}') + len(self.booru_scheme.score_start))
                    self._end       = self._title.index(f'{self.booru_scheme.score_end}', self._start)
                    self._score     = int(self._title[self._start:self._end])

                    if min_score is not None and self._score < min_score:
                        print(f'(score {self._score} too low) skipped {self._src}')
                        continue
                except Exception as e:
                    print(f'skipped: {e}')
                    continue

                for extension in self.extension_list:
                    try:
                        self._file_name_full = f'{self._file_name}.{extension}'
                        self._full_url = f'{self.booru_scheme.raw_image_url.format(booru=self.booru, code_actual=self._code_actual)}{self._file_name_full}'
                        self.direct_download(self._full_url, imgnum)
                        imgnum -= 1
                        self.numDownloads += 1
                        break
                    except:
                        continue

    def download_random(self, min_score:int=None) -> None:
        self._selected_page = rand.randint(0, self.max_page)
        self.download(self._selected_page, min_score=min_score)

    def download_all(self, min_score:int=None) -> None:
        for page in range(PAGESTART, self.max_page):
            self.download(page, min_score=min_score)

    def direct_download(self, url:str,num:int) -> None:
        r = requests.get(url)
        if r.status_code == 404:
            raise Exception("Response 404")
        img_data = r.content
        extension = url.split('.')[-1]
        with open('resource/img/booruimage'+str(num)+'.'+extension, 'wb') as handler:
            handler.write(img_data)
        with open('resource/img/numberdownloaded.txt', 'w') as handler:
                handler.write(str(self.numDownloads))

    def get_page_count(self) -> int:
        self._href_core = self.booru_scheme.booru_search_url.format(booru_name=self.booru).split('?')[0]
        print(f'href_core={self._href_core}')
        self._home_url  = f'{self._href_core}?page=post&s=list&tags={self.tags}'
        print(self._home_url)
        self._html = requests.get(self._home_url).text
        self._soup = BeautifulSoup(self._html, 'html.parser')
        for a in self._soup.find_all('a'):
            if a.getText() == '2' and self.post_per_page == 0:
                self.post_per_page = int(a.get('href').split('=')[-1])
            if a.get('alt') == 'last page':
                self._final_link = f'{self._href_core}{a.get("href")}'
                print(f'last alt={self._final_link}')
                return (int(self._final_link[(self._final_link.index('&pid=') + len('&pid=')):]) / self.post_per_page + 1)
        return 0

    def pick_value(self, text:str, start_text:str, end_text:str) -> str:
        start_index = text.index(start_text) + len(start_text)
        end_index   = text.index(end_text, start_index)
        return text[start_index:end_index]

@dataclass
class BooruScheme:
    booru_name               : str
    booru_search_url         : str = 'https://{booru_name}.booru.org/index.php?page=post&s=list&tags='
    preview_thumb_id_start   : str = 'thumbnails//'
    preview_thumb_id_end     : str = '/'
    preview_thumb_name_start : str = 'thumbnail_'
    preview_thumb_name_end   : str = '.'
    score_start              : str = 'score:'
    score_end                : str = ' '
    raw_image_url            : str = 'https://img.booru.org/{booru}//images/{code_actual}/'

#downloads all images listed in webresource.json in resources
def download_web_resources():
    try:
        with open(Resource.WEB_RESOURCE) as op:
            js = json.loads(op.read())
            ls = js['weblist']
            for link in ls:
                BooruDownloader.direct_download(link)
    except Exception as e:
        print(e)

#does annoyance things; while running, does a check of randint against the frequency of each option
#   if pass, do thing, if fail, don't do thing. pretty simple stuff right here.
#   only exception is for fill drive and replace images:
#       fill: will only happen if fill is on AND until there are 8 threads running simultaneously
#             as threads become available they will be restarted.
#       replace: will only happen one single time in the run of the application, but checks ALL folders
def annoyance():
    global MITOSIS_LIVE
    while(True):
        roll_for_initiative()
        if not MITOSIS_LIVE and (MITOSIS_MODE) and HAS_IMAGES: #or LOWKEY_MODE) and HAS_IMAGES:
            subprocess.Popen([sys.executable, Process.POPUP]) if MOOD_OFF else subprocess.Popen([sys.executable, Process.POPUP, f'-{MOOD_ID}'])
            MITOSIS_LIVE = True
        if FILL_MODE and LIVE_FILL_THREADS < MAX_FILL_THREADS:
            thread.Thread(target=fill_drive).start()
        if REPLACE_MODE and not REPLACING_LIVE:
            thread.Thread(target=replace_images).start()
        time.sleep(float(DELAY) / 1000.0)

#independently attempt to do all active settings with probability equal to their freq value
def roll_for_initiative():
    if HIBERNATE_TYPE == 'Pump-Scare' and HIBERNATE_MODE:
        if HAS_IMAGES:
            if HAS_AUDIO:
                if AUDIO_CAP:
                    if AUDIO_NUMBER < AUDIO_MAX:
                        try:
                            thread.Thread(target=play_audio).start()
                            pumpScareAudio.wait()
                        except Exception as e:
                            messagebox.showerror('Audio Error', 'Failed to play audio.\n[' + str(e) + ']')
                            logging.critical(f'failed to play audio\n\tReason: {e}')
                else:
                    try:
                        thread.Thread(target=play_audio).start()
                        pumpScareAudio.wait()
                    except Exception as e:
                        messagebox.showerror('Audio Error', 'Failed to play audio.\n[' + str(e) + ']')
                        logging.critical(f'failed to play audio\n\tReason: {e}')
            try:
                utils.set_wallpaper(Resource.WALLPAPER)
                wallpaperWait.clear()
                subprocess.Popen([sys.executable, Process.POPUP]) if MOOD_OFF else subprocess.Popen([sys.executable, Process.POPUP, f'-{MOOD_ID}'])
            except Exception as e:
                messagebox.showerror('Popup Error', 'Failed to start popup.\n[' + str(e) + ']')
                logging.critical(f'failed to start popup.pyw\n\tReason: {e}')
    else:
        #these variables make the experience "more consistent" by stopping further popup spawns if enough spawns are reached
        currPopNum = 0
        maxPopNum = 1 if SINGLE_MODE else 999
        if do_roll(WEB_CHANCE) and HAS_WEB and currPopNum < maxPopNum:
            try:
                url = url_select(rand.randrange(len(WEB_DICT['urls']))) if HAS_WEB else None
                webbrowser.open_new(url)
                currPopNum += 1
            except Exception as e:
                messagebox.showerror('Web Error', 'Failed to open website.\n[' + str(e) + ']')
                logging.critical(f'failed to open website {url}\n\tReason: {e}')
        if do_roll(VIDEO_CHANCE) and VIDEOS and currPopNum < maxPopNum:
            global VIDEO_NUMBER
            if VIDEO_CAP:
                with open(Data.MAX_VIDEOS, 'r') as f:
                    VIDEO_NUMBER = int(f.readline())
                if VIDEO_NUMBER < VIDEO_MAX:
                    try:
                        if VLC_MODE:
                            thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, '-video', '-vlc'], shell=False)).start() if MOOD_OFF else thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, f'-{MOOD_ID}', '-video', '-vlc'], shell=False)).start()
                        else:
                            thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, '-video'], shell=False)).start() if MOOD_OFF else thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, f'-{MOOD_ID}', '-video'], shell=False)).start()
                        with open(Data.MAX_VIDEOS, 'w') as f:
                            f.write(str(VIDEO_NUMBER+1))
                        currPopNum += 1
                    except Exception as e:
                        messagebox.showerror('Popup Error', 'Failed to start popup.\n[' + str(e) + ']')
                        logging.critical(f'failed to start video popup.pyw\n\tReason: {e}')
            else:
                try:
                    if VLC_MODE:
                        thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, '-video', '-vlc'], shell=False)).start() if MOOD_OFF else thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, f'-{MOOD_ID}', '-video', '-vlc'], shell=False)).start()
                    else:
                        thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, '-video'], shell=False)).start() if MOOD_OFF else thread.Thread(target=lambda: subprocess.call([sys.executable, Process.POPUP, f'-{MOOD_ID}', '-video'], shell=False)).start()
                    currPopNum += 1
                except Exception as e:
                    messagebox.showerror('Popup Error', 'Failed to start popup.\n[' + str(e) + ']')
                    logging.critical(f'failed to start video popup.pyw\n\tReason: {e}')
        if do_roll(AUDIO_CHANCE) and AUDIO and currPopNum < maxPopNum:
            if AUDIO_CAP:
                if AUDIO_NUMBER < AUDIO_MAX:
                    try:
                        thread.Thread(target=play_audio).start()
                        currPopNum += 1
                    except Exception as e:
                        messagebox.showerror('Audio Error', 'Failed to play audio.\n[' + str(e) + ']')
                        logging.critical(f'failed to play audio\n\tReason: {e}')
            else:
                try:
                    thread.Thread(target=play_audio).start()
                    currPopNum += 1
                except Exception as e:
                    messagebox.showerror('Audio Error', 'Failed to play audio.\n[' + str(e) + ']')
                    logging.critical(f'failed to play audio\n\tReason: {e}')
        if do_roll(CAP_POP_CHANCE) and CAPTIONS and currPopNum < maxPopNum:
            try:
                subprocess.call([sys.executable, Process.SUBLABEL, f'-{MOOD_ID}']) if not MOOD_OFF else subprocess.call([sys.executable, Process.SUBLABEL])
                currPopNum += 1
            except Exception as e:
                messagebox.showerror('Caption Popup Error', 'Could not start caption popup.\n[' + str(e) + ']')
                logging.critical(f'failed to start sublabel.pyw\n\tReason: {e}')

        if do_roll(PROMPT_CHANCE) and HAS_PROMPTS and currPopNum < maxPopNum:
            try:
                subprocess.call([sys.executable, Process.PROMPT, f'-{MOOD_ID}']) if not MOOD_OFF else subprocess.call([sys.executable, Process.PROMPT])
                currPopNum += 1
            except Exception as e:
                messagebox.showerror('Prompt Error', 'Could not start prompt.\n[' + str(e) + ']')
                logging.critical(f'failed to start prompt.pyw\n\tReason: {e}')
        if (not (MITOSIS_MODE)) and do_roll(POPUP_CHANCE) and HAS_IMAGES and currPopNum < maxPopNum:
                 #or LOWKEY_MODE)) and do_roll(POPUP_CHANCE) and HAS_IMAGES and currPopNum < maxPopNum:
            try:
                subprocess.Popen([sys.executable, Process.POPUP]) if MOOD_OFF else subprocess.Popen([sys.executable, Process.POPUP, f'-{MOOD_ID}'])
                currPopNum += 1
            except Exception as e:
                messagebox.showerror('Popup Error', 'Failed to start popup.\n[' + str(e) + ']')
                logging.critical(f'failed to start popup.pyw\n\tReason: {e}')

def rotate_wallpapers():
    prv = 'default'
    base = int(settings['wallpaperTimer'])
    vari = int(settings['wallpaperVariance'])
    while len(settings['wallpaperDat'].keys()) > 1:
        time.sleep(base + rand.randint(-vari, vari))
        selectedWallpaper = list(settings['wallpaperDat'].keys())[rand.randrange(0, len(settings['wallpaperDat'].keys()))]
        while(selectedWallpaper == prv):
            selectedWallpaper = list(settings['wallpaperDat'].keys())[rand.randrange(0, len(settings['wallpaperDat'].keys()))]
        utils.set_wallpaper(Resource.ROOT / settings['wallpaperDat'][selectedWallpaper])
        prv = selectedWallpaper

def do_timer():
    utils.show_file(Data.HID_TIME)
    with open(Data.HID_TIME, 'r') as file:
        time_remaining = int(file.readline())

    while time_remaining > 0:
        print('time left: ', str(time_remaining), 'secs', sep='')
        time.sleep(1)
        time_remaining -= 1
        utils.show_file(Data.HID_TIME)
        with open(Data.HID_TIME, 'w') as file:
            file.write(str(time_remaining))
        utils.hide_file(Data.HID_TIME)

    try:
        utils.show_file(Data.PASS_HASH)
        utils.show_file(Data.HID_TIME)
        os.remove(Data.PASS_HASH)
        os.remove(Data.HID_TIME)
        subprocess.Popen([sys.executable, Process.PANIC])
    except:
        subprocess.Popen([sys.executable, Process.PANIC])

def audioHelper():
    if MOOD_OFF:
        ps.playsound(str(AUDIO[rand.randrange(len(AUDIO))]))
    else:
        ps.playsound(str(MOOD_AUDIO[rand.randrange(len(MOOD_AUDIO))]))


#if audio is not playing, selects and plays random audio file from /aud/ folder
def play_audio():
    global PLAYING_AUDIO
    global AUDIO_NUMBER
    if not AUDIO:
        return
    logging.info('starting audio playback')
    PLAYING_AUDIO = True
    AUDIO_NUMBER += 1
    try:
        if HIBERNATE_TYPE == 'Pump-Scare' and HIBERNATE_MODE:
            p = multiprocessing.Process(target=audioHelper)
            p.start()
            if PUMP_SCARE_OFFSET != 0:
                time.sleep(PUMP_SCARE_OFFSET)
            pumpScareAudio.set()
            time.sleep(2.6)
            pumpScareAudio.clear()
            p.terminate()
        else:
            if not MOOD_OFF and os.path.exists(Resource.MEDIA):
                ps.playsound(str(MOOD_AUDIO[rand.randrange(len(MOOD_AUDIO))]))
            else:
                ps.playsound(str(AUDIO[rand.randrange(len(AUDIO))]))
    except Exception as e:
        logging.warning(f'Could not play sound. {e}')
    #winsound.PlaySound(AUDIO[rand.randrange(len(AUDIO))], winsound.SND_)
    PLAYING_AUDIO = False
    AUDIO_NUMBER -= 1
    logging.info('finished audio playback')

#fills drive with copies of images from /resource/img/
#   only targets User folders; none of that annoying elsaware shit where it fills folders you'll never see
#   can only have 8 threads live at once to avoid 'memory leak'
def fill_drive():
    global LIVE_FILL_THREADS
    LIVE_FILL_THREADS += 1
    docPath = DRIVE_PATH
    images = []
    logging.info(f'starting drive fill to {docPath}')
    for img in os.listdir(Resource.IMAGE):
        if not img.split('.')[-1] == 'ini':
            images.append(img)
    for root, dirs, files in os.walk(docPath):
        #tossing out directories that should be avoided
        for obj in list(dirs):
            if obj in AVOID_LIST or obj[0] == '.':
                dirs.remove(obj)
        for i in range(rand.randint(3, 6)):
            index = rand.randint(0, len(images)-1)
            tObj = str(time.time() * rand.randint(10000, 69420)).encode(encoding='ascii',errors='ignore')
            pth = os.path.join(root, hashlib.md5(tObj).hexdigest() + '.' + str.split(images[index], '.')[len(str.split(images[index], '.')) - 1].lower())
            shutil.copyfile(Resource.IMAGE / images[index], pth)
        time.sleep(float(FILL_DELAY) / 100)
    LIVE_FILL_THREADS -= 1

#seeks out folders with a number of images above the replace threshold and replaces all images with /resource/img/ files
def replace_images():
    global REPLACING_LIVE
    REPLACING_LIVE = True
    docPath = DRIVE_PATH
    imageNames = []
    for img in os.listdir(Resource.IMAGE):
        if not img.split('.')[-1] == 'ini':
            imageNames.append(Resource.IMAGE / img)
    for root, dirs, files in os.walk(docPath):
        for obj in list(dirs):
            if obj in AVOID_LIST or obj[0] == '.':
                dirs.remove(obj)
        toReplace = []
        #ignore any folders with fewer items than the replace threshold
        if len(files) >= REPLACE_THRESHOLD:
            #if folder has enough items, check how many of them are images
            for obj in files:
                if obj.split('.')[-1] in FILE_TYPES:
                    if os.path.exists(os.path.join(root, obj)):
                        toReplace.append(os.path.join(root, obj))
            #if has enough images, finally do replacing
            if len(toReplace) >= REPLACE_THRESHOLD:
                for obj in toReplace:
                    shutil.copyfile(imageNames[rand.randrange(len(imageNames))], obj, follow_symlinks=True)
    #never turns off threadlive variable because it should only need to do this once

def update_media():
    #handle media list, doing it here instead of popup to take the load off of popups
    if os.path.exists(Resource.MEDIA) and not MOOD_OFF:
        if os.path.exists(Data.MOODS / f'{MOOD_ID}.json'):
            with open(Data.MOODS / f'{MOOD_ID}.json', 'r') as f:
                moodData = json.loads(f.read())
                #logging.info(f'moodData {moodData}')
        elif os.path.exists(Data.UNNAMED_MOODS / f'{MOOD_ID}.json'):
            with open(Data.UNNAMED_MOODS / f'{MOOD_ID}.json', 'r') as f:
                moodData = json.loads(f.read())
                #logging.info(f'moodData {moodData}')
        with open(Resource.MEDIA, 'r') as f:
            mediaData = json.loads(f.read())
            #print(f'mediaData {mediaData}')
        #if CORRUPTION_MODE:
            #for
        try:
            global MOOD_AUDIO
            MOOD_AUDIO = []
            for mood in list(mediaData):
                if mood not in moodData['media']:
                    mediaData.pop(mood)

            rawList = list(mediaData.values())
            mergedList = dict.fromkeys(mediaData.keys())
            for key in mergedList.keys():
                mergedList[key] = []
            moodVideo = dict.fromkeys(mediaData.keys())
            for key in moodVideo.keys():
                moodVideo[key] = []
            for sub in rawList:
                for i in sub:
                    if i in os.listdir(Resource.AUDIO):
                        MOOD_AUDIO.append(Resource.AUDIO / i)
                        #logging.info(f'{i}')
                    elif i in os.listdir(Resource.VIDEO):
                        for key in mediaData.keys():
                            if i in mediaData[key]:
                                moodVideo[key] += [i]
                    else:
                        for key in mediaData.keys():
                            if i in mediaData[key]:
                                mergedList[key] += [i]
            with open(Data.MEDIA_IMAGES, 'w') as f:
                f.write(json.dumps(mergedList))
            with open(Data.MEDIA_VIDEO, 'w') as f:
                f.write(json.dumps(moodVideo))
        except Exception as e:
            logging.warning(f'failed to load mediaData properly.\n\tReason: {e}')
            print('failed to load mediaData')

if __name__ == '__main__':
    main()
