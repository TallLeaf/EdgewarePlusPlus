import hashlib
import os
import sys
import random as rand
import tkinter as tk
import time
import json
import pathlib
import webbrowser
import threading as thread
import logging
import subprocess
from tkinter import simpledialog, Tk, Frame, Label, Button, StringVar, font
from itertools import cycle
from PIL import Image, ImageTk, ImageFilter
from screeninfo import get_monitors
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils import utils
from utils.paths import Data, Defaults, Process, Resource

#import traceback
try:
    import vlc
except:
    print('vlc failed to load.')

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)

NO_SKIP = True

class prefix_data:
    def __init__(self, name, captions = None, images = None, max = 1, chance = 100.0):
        # The name of the prefix
        self.name = name

        # Captions to use if different from the name of the prefix
        if captions:
            self.captions = captions
        else:
            self.captions = name

        # Image file prefix
        if images:
            self.images = images
        else:
            self.images = name

        # Max number of popups to display
        self.max = max

        # Chance of this prefix being used (% out of 100, and it's a float to allow < 1% chance)
        self.chance = float(chance)

prefixes = {}
#End Imported Code


def check_setting(name:str, default:bool=False) -> bool:
    default = False if default is None else default
    try:
        return int(settings.get(name)) == 1
    except:
        return default

ALLOW_SCREAM = True
SHOW_CAPTIONS = False
PANIC_DISABLED = False
EXTREME_MODE = False
WEB_OPEN = False
HAS_LIFESPAN = False
LIFESPAN = 0
WEB_PROB = 0
MITOSIS_STRENGTH = 2
SUBMISSION_TEXT = 'I Submit <3'
PANIC_KEY = ''
PANIC_REQUIRES_VALIDATION = False
HASHED_PATH = None
CAPTIONS = {}
LOWKEY_MODE = False
LOWKEY_CORNER = 0
DELAY = 0
OPACITY = 100
VIDEO_VOLUME = 0.25
FADE_OUT_TIME = 1.5
DENIAL_MODE = False
DENIAL_CHANCE = 0
SUBLIMINAL_MODE = False
SUBLIMINAL_CHANCE = 100
MAX_SUBLIMINALS = 200
LANCZOS_MODE = True
BUTTONLESS = False
HIBERNATE_MODE = False
MOOD_OFF = True
MOOD_FILENAME = True
MULTI_CLICK = False
THEME = 'Original'
MOVING_SPEED = 5
MOVING_CHANCE = 0
MOVING_STATUS = False
MOVING_RANDOM = False

with open(Data.CONFIG, 'r') as cfg:
    settings = json.loads(cfg.read())
    SHOW_CAPTIONS = check_setting('showCaptions')
    PANIC_DISABLED = check_setting('panicDisabled')
    MITOSIS_MODE = check_setting('mitosisMode')
    WEB_OPEN = check_setting('webPopup')
    WEB_PROB = int(settings['webMod'])
    PANIC_KEY = settings['panicButton']
    HAS_LIFESPAN = check_setting('timeoutPopups')
    LIFESPAN = int(settings['popupTimeout'])
    MITOSIS_STRENGTH = int(settings['mitosisStrength'])
    PANIC_REQUIRES_VALIDATION = check_setting('timerMode')
    LOWKEY_MODE = check_setting('lkToggle')
    LOWKEY_CORNER = int(settings['lkCorner'])
    DELAY = int(settings['delay'])
    OPACITY = int(settings['lkScaling'])
    VIDEO_VOLUME = float(settings['videoVolume']) / 100
    
    VIDEO_LOOP = False # For the sake of arguement, let's say it's a toggle

    VIDEO_VOLUME = min(max(0, VIDEO_VOLUME), 1)

    DENIAL_MODE = check_setting('denialMode')
    DENIAL_CHANCE = int(settings['denialChance'])
    SUBLIMINAL_MODE = check_setting('popupSubliminals')
    SUBLIMINAL_CHANCE = int(settings['subliminalsChance'])
    MAX_SUBLIMINALS = int(settings['maxSubliminals'])

    LANCZOS_MODE = check_setting('antiOrLanczos')

    BUTTONLESS = check_setting('buttonless')

    MULTI_CLICK = check_setting('multiClick')

    HIBERNATE_MODE = check_setting('hibernateMode')

    THEME = settings['themeType']

    if HIBERNATE_MODE:
        if settings['hibernateType'] == 'Chaos':
            with open(Data.CHAOS_TYPE, 'r') as ct:
                HIBERNATE_TYPE = ct.read()
        else:
            HIBERNATE_TYPE = settings['hibernateType']
    if SYS_ARGS:
        MOOD_OFF = check_setting('toggleMoodSet')

    MOOD_FILENAME = check_setting('captionFilename')

    MOVING_CHANCE = int(settings['movingChance'])
    MOVING_SPEED = int(settings['movingSpeed'])
    MOVING_RANDOM = check_setting('movingRandom')

    CORRUPTION_DEVMODE = check_setting('corruptionDevMode')

if MOVING_CHANCE >= rand.randint(1,100):
    BUTTONLESS = True
    MOVING_STATUS = True

#take out first arg and make it into the mood ID
MOOD_ID = '0'
if not MOOD_OFF:
    MOOD_ID = SYS_ARGS[0].strip('-')
    SYS_ARGS.pop(0)

if MOOD_ID != '0':
    if os.path.exists(Data.MOODS / f'{MOOD_ID}.json'):
        with open(Data.MOODS / f'{MOOD_ID}.json', 'r') as f:
            moodData = json.loads(f.read())
    elif os.path.exists(Data.UNNAMED_MOODS / f'{MOOD_ID}.json'):
        with open(Data.UNNAMED_MOODS / f'{MOOD_ID}.json', 'r') as f:
            moodData = json.loads(f.read())


#used for timer mode, checks if password is required to panic
if PANIC_REQUIRES_VALIDATION:
    try:
        utils.show_file(Data.PASS_HASH)
        with open(Data.PASS_HASH, 'r') as file:
            HASHED_PATH = file.readline()
        utils.hide_file(Data.PASS_HASH)
    except:
        #no hash found
        HASHED_PATH = None

if WEB_OPEN:
    web_dict = ''
    if os.path.exists(Resource.WEB):
        with open(Resource.WEB, 'r') as web_file:
            web_dict = json.loads(web_file.read())
            #web_mood_dict = web_dict

        #if not MOOD_OFF:
            #try:
                #for i, mood in enumerate(web_dict['moods']):
                    #if mood not in moodData['web']:
                        #web_mood_dict['urls'].pop(i)
                        #web_mood_dict['args'].pop(i)
                        #web_mood_dict['moods'].pop(i)
                #messagebox.showinfo('test', f'{web_mood_dict}, {type(web_mood_dict)}')
            #except Exception as e:
                #messagebox.showinfo('test', f'{e}')
                #print('error loading web moods, or web moods not supported in pack.')
try:
    with open(Resource.CAPTIONS, 'r') as caption_file:
        CAPTIONS = json.load(caption_file)
        try:
            SUBMISSION_TEXT = rand.choice(CAPTIONS['subtext'])
        except:
            print('will use default submission text')
        prefixes['default'] = prefix_data('default', images='', max=1, chance=100.0)

    # Everything in the 'prefix' block gets the default values
    for prefix in CAPTIONS.get('prefix', []):
        prefixes[prefix] = prefix_data(prefix)


    for prefix in CAPTIONS.get('prefix_settings', []):
        base = CAPTIONS['prefix_settings'][prefix]
        caption = base.get('caption', prefix)
        images = base.get('images', prefix)
        max_popup = base.get('max', 1)
        chance = float(base.get('chance', 100.0))

        if prefix in prefixes:
            entry = prefixes[prefix]
            entry.caption = caption
            entry.chance = chance

            if prefix != 'default':
                entry.images = images
                entry.max = max_popup
        else:
            prefixes[prefix] = prefix_data(prefix, captions=caption, images=images, max=max_popup, chance=chance)

    # Default has to have a reasonable chance of popping up
    if prefixes['default'].chance <= 10:
        prefixes['default'].chance = 10
except:
    prefixes['default'] = prefix_data('default', images='', max=1, chance=100.0)
    print('no captions.json')

#gif label class
class GifLabel(tk.Label):
    def load(self, path:str, resized_width:int, resized_height:int, delay:int=75, back_image:Image.Image=None):
        self.image = Image.open(path)
        self.configure(background='black')
        self.frames:list[ImageTk.PhotoImage] = []
        if 'duration' in self.image.info:
            self.delay = int(self.image.info['duration'])
        else:
            self.delay = delay

        if self.delay < delay:
            self.delay = delay

        try:
            for i in range(0, self.image.n_frames):
                hold_image = self.image.resize((resized_width, resized_height), Image.BOX)
                if back_image is not None:
                    hold_image, back_image = hold_image.convert('RGBA'), back_image.convert('RGBA')
                    hold_image = Image.blend(back_image, hold_image, 0.2)
                self.frames.append(ImageTk.PhotoImage(hold_image.copy()))
                self.image.seek(i)
        except Exception as e:
            print(f'{e}')
            print(f'Done register frames. ({len(self.frames)})')
        self.frames_ = cycle(self.frames)

    def next_frame(self):
        if self.frames_:
            self.config(image=next(self.frames_))
            self.after(self.delay, self.next_frame)


#video label class
class VideoLabel(tk.Label):
    def load(self, path:str, resized_width:int, resized_height:int):
        import imageio
        from moviepy.editor import AudioFileClip
        from videoprops import get_video_properties

        self.path = path
        self.configure(background='black')
        self.wid = resized_width
        self.hgt = resized_height
        self.video_properties = get_video_properties(path)
        self.audio = AudioFileClip(self.path)
        self.fps = float(self.video_properties['avg_frame_rate'].split('/')[0]) / float(self.video_properties['avg_frame_rate'].split('/')[1])
        try:
            self.audio_track = self.audio.to_soundarray()
            print(self.audio_track)
            self.audio_track = [[VIDEO_VOLUME*v[0], VIDEO_VOLUME*v[1]] for v in self.audio_track]
            self.duration = float(self.video_properties['duration'])
        except:
            self.audio_track = None
            self.duration = None
        self.video_frames = imageio.get_reader(path)
        self.delay = 1 / self.fps

    def play(self):
        from types import NoneType
        if not isinstance(self.audio_track, NoneType):
            try:
                import sounddevice
                sounddevice.play(self.audio_track, samplerate=len(self.audio_track) / self.duration, loop=True)
            except Exception as e:
                print(f'failed to play sound, reason:\n\t{e}')
        while True:
            for frame in self.video_frames.iter_data():
                self.time_offset_start = time.perf_counter()
                self.video_frame_image = ImageTk.PhotoImage(Image.fromarray(frame).resize((self.wid, self.hgt)))
                self.config(image=self.video_frame_image)
                self.image = self.video_frame_image
                self.time_offset_end = time.perf_counter()
                time.sleep(max(0, self.delay - (self.time_offset_end - self.time_offset_start)))

#moving window originally provided very generously by u/basicmo!

    def play_no_loop(self):
        from types import NoneType
        if not isinstance(self.audio_track, NoneType):
            try:
                import sounddevice
                sounddevice.play(self.audio_track, samplerate=len(self.audio_track) / self.duration, loop=True)
            except Exception as e:
                print(f'failed to play sound, reason:\n\t{e}')
        
        for frame in self.video_frames.iter_data():
            self.time_offset_start = time.perf_counter()
            self.video_frame_image = ImageTk.PhotoImage(Image.fromarray(frame).resize((self.wid, self.hgt)))
            self.config(image=self.video_frame_image)
            self.image = self.video_frame_image
            self.time_offset_end = time.perf_counter()
            time.sleep(max(0, self.delay - (self.time_offset_end - self.time_offset_start)))
        die()
mspd = rand.randint(-MOVING_SPEED,MOVING_SPEED)
while mspd == 0:
    mspd = rand.randint(-MOVING_SPEED,MOVING_SPEED)

def move_window(master, resized_height:int, resized_width:int, xlocation:int, ylocation:int):
    width = resized_width
    height = resized_height
    if MOVING_RANDOM:
        move_speedX = rand.randint(-MOVING_SPEED,MOVING_SPEED)
        move_speedY = rand.randint(-MOVING_SPEED,MOVING_SPEED)
        while (move_speedX == 0) and (move_speedY == 0):
            move_speedX = rand.randint(-MOVING_SPEED,MOVING_SPEED)
            move_speedY = rand.randint(-MOVING_SPEED,MOVING_SPEED)
    else:
        move_speedX = mspd
        move_speedY = mspd

    dx = move_speedX
    dy = move_speedY

    x, y = xlocation, ylocation  # Initial position
    while True:
        x += dx
        y += dy

        if x + width >= master.winfo_screenwidth():
            dx = -abs(move_speedX)
        elif x <= 0:
            dx = abs(move_speedX)
        if y + height >= master.winfo_screenheight():
            dy = -abs(move_speedY)
        elif y <= 0:
            dy = abs(move_speedY)

        master.geometry(f"{width}x{height}+{x}+{y}")
        master.update()
        master.after(10)

def pick_resource(basepath, vidYes:bool):
    if MOOD_ID != '0' and os.path.exists(Resource.MEDIA):
        try:
            if vidYes:
                with open(Data.MEDIA_VIDEO, 'r') as f:
                    itemsList = json.loads(f.read())
            else:
                with open(Data.MEDIA_IMAGES, 'r') as f:
                    itemsList = json.loads(f.read())
        except Exception as e:
            print(f'failed to run mood check, reason:\n\t{e}')
            itemsList = os.listdir(basepath)
    else:
        itemsList = os.listdir(basepath)
    if not itemsList:
        return "", "", 0

    while True:
        #item = rand.choice(items)
        
        #while item.split('.')[-1].lower() == 'ini':
        #    item = rand.choice(items)

        #matched = 'none'
        if MOOD_FILENAME:
            continue
        #    for prefix_name in prefixes:
        #            if item.startswith(prefixes[prefix_name].images):
        #                matched = 'partial'
        #                if do_roll(prefixes[prefix_name].chance):
        #                    matched = 'matched'
        #                    break
        #    if matched == 'none':
        #        prefix_name = 'default'

            # In the case where there was a match to a prefix, but didn't win the roll, we want to try again
        #    elif matched == 'partial':
        #        continue
        #if the mood filename setting is off, roll for a random mood based on chance
        else:
            if MOOD_ID != '0':
                while True:
                    prefix_name = rand.choice(list(prefixes))
                    if prefix_name in moodData['captions']:
                        if do_roll(prefixes[prefix_name].chance):
                            break
            else:
                while True:
                    prefix_name = rand.choice(list(prefixes))
                    if do_roll(prefixes[prefix_name].chance):
                        break
            
        prefix = prefixes[prefix_name]
        items = itemsList[prefix_name]
        item = rand.choice(items)
        while item.split('.')[-1].lower() == 'ini':
            item = rand.choice(items)
        caption = ""
        max = 1

        if SHOW_CAPTIONS and CAPTIONS and prefix.captions:
            if prefix.captions in CAPTIONS:
                caption = rand.choice(CAPTIONS[prefix.captions])
                if prefix.max > 1:
                    max = rand.randrange(2, prefix.max)

        item = os.path.join(basepath, item)
        # print(prefix.name, item, caption, max)
        return item, caption, max

root = Tk()

fore = '#000000'
back = '#f0f0f0'
mainfont = font.nametofont('TkDefaultFont')

if THEME == 'Dark':
    fore = '#f9faff'
    back = '#282c34'
if THEME == 'The One':
    fore = '#00ff41'
    back = '#282c34'
    mainfont.configure(family='Consolas', size=8)
if THEME == 'Ransom':
    fore = '#ffffff'
    back = '#841212'
    mainfont.configure(family='Arial Bold')
if THEME == 'Goth':
    fore = '#ba9aff'
    back = '#282c34'
    mainfont.configure(family='Constantia')
if THEME == 'Bimbo':
    fore = '#ff3aa3'
    back = '#ffc5cd'
    mainfont.configure(family='Constantia')

def run():
    #var things
    video_mode = False
    resource_path = Resource.IMAGE
    if len(SYS_ARGS) >= 1 and SYS_ARGS[0] == '-video':
        video_mode = True
        resource_path = Resource.VIDEO

    item, caption_text, root.click_count = pick_resource(resource_path, video_mode)

    if not video_mode:
        while True:
            try:
                image = Image.open(os.path.abspath(item))
                break
            except:
                item, caption_text, root.click_count = pick_resource(resource_path, video_mode)
    else:
        from videoprops import get_video_properties
        video_path = str(Resource.VIDEO / item)
        video_properties = get_video_properties(video_path)
        image = Image.new('RGB', (video_properties['width'], video_properties['height']))

    animated_gif = False
    # Check to see if the gif is animated or a normal gif file
    if item.split('.')[-1].lower() == 'gif':
        if image.n_frames > 1:
            animated_gif = True

        else:
            image = image.convert('RGBA')

    border_wid_const = 5
    monitor = rand.choice(get_monitors())

    #window start
    root.bind('<KeyPress>', lambda key: panic(key))
    root.configure(bg='black')
    root.frame = Frame(root)
    root.wm_attributes('-topmost', -1)
    utils.set_borderless(root)

    #many thanks to @MercyNudes for fixing my old braindead scaling method (https://twitter.com/MercyNudes)
    def resize(img:Image.Image) -> Image.Image:
        size_source = max(img.width, img.height) / min(monitor.width, monitor.height)
        size_target = rand.randint(30, 70) / 100 if (not LOWKEY_MODE or video_mode) else rand.randint(20, 50) / 100
        if video_mode == True: 
            size_target = max(size_target, 40/100)
            resize_factor = size_target / size_source
            resize_factor = resize_factor*1.45
        else:
            resize_factor = size_target / size_source
        if LANCZOS_MODE:
            return image.resize((int(image.width * resize_factor), int(image.height * resize_factor)), Image.LANCZOS)
        else:
            return image.resize((int(image.width * resize_factor), int(image.height * resize_factor)), Image.ANTIALIAS)

    resized_image = resize(image)

    do_deny = check_deny()
    if SUBLIMINAL_MODE:
        check_subliminal()

    if do_deny and not animated_gif:
        blur_modes = [ImageFilter.GaussianBlur(5), ImageFilter.GaussianBlur(10), ImageFilter.GaussianBlur(20),
                      ImageFilter.BoxBlur(5),      ImageFilter.BoxBlur(10),       ImageFilter.BoxBlur(20)]
        rand.shuffle(blur_modes)
        resized_image = resized_image.filter(blur_modes.pop())

    photoimage_image = ImageTk.PhotoImage(resized_image)
    image.close()

    #different handling for videos vs gifs vs normal images
    if video_mode:
        duration = 0
        if len(SYS_ARGS) >= 2 and SYS_ARGS[1] == '-vlc':
            #vlc mode
            label = Label(root, width=resized_image.width, height=resized_image.height)
            label.pack()
            if VIDEO_LOOP:
                startVLC(video_path, label) # if it loops, we do whatever is normal
            else:
                from videoprops import get_video_properties # placement is only for the PR
                # the only tested file types are .mov, .mp4, and webm. I haven't encountered other file types in the packs I have so...
                try:
                    duration = float(get_video_properties(video_path)['duration']) # for .mov and .mp4
                except:
                        #for webm, we get a HH:MM:SS.MS format. It seems having two significant digits will suffice for the MS, and there's a bit of conversion to do
                    try:
                        time_str = get_video_properties(video_path)['tags']['DURATION']
                        time_str = time_str[0:10] #  HH:MM:SS.MS
                        temp = time.strptime(time_str, "%H:%M:%S.%f")
                        duration = temp.hour * 3600 + temp.minute * 60 + temp.second + temp.microsecond / 1e6
                    except:
                        print(get_video_properties(video_path)) # show the JSON
                        #the file is a .wmv, or some other cryptic type, maybe this should be an exposed fallback amount
                        duration = 30 # from what I've seen most clips are less or more, making this the frustrating center
                startVLC_no_loop(video_path, label, duration)
        else:
            #video mode
            root.attributes('-topmost',True)
            label = VideoLabel(root)
            label.load(path = video_path, resized_width = resized_image.width, resized_height = resized_image.height)
            label.pack()
            if VIDEO_LOOP:
                thread.Thread(target=lambda: label.play(), daemon=True).start()
            else:
                thread.Thread(target=lambda: label.play_no_loop(), daemon=True).start()
        duration = duration+5
    elif animated_gif:
        #gif mode
        label = GifLabel(root)
        label.load(path=os.path.abspath(f'{item}'), resized_width = resized_image.width, resized_height = resized_image.height)
        label.pack()
    else:
        #standard image mode
        if not SUBLIMINAL_MODE:
            label = Label(root, image=photoimage_image, bg='black')
            label.pack()
        else:
            with open(Data.MAX_SUBLIMINALS, 'r+') as f:
                i = int(f.readline())
                label = GifLabel(root)
                subliminal_path = Defaults.SPIRAL

                if os.path.exists(Resource.SUBLIMINALS):
                    subliminal_options = [file for file in os.listdir(Resource.SUBLIMINALS) if str(file).lower().endswith('.gif')]
                    if len(subliminal_options) > 0:
                        subliminal_path = Resource.SUBLIMINALS / str(rand.choice(subliminal_options))

                label.load(subliminal_path, photoimage_image.width(), photoimage_image.height(), back_image=resized_image)
                label.pack()
                label.next_frame()

                f.seek(0)
                f.write(str(i+1))
                f.truncate()

        if do_deny:
            deny_options = CAPTIONS.get('denial')
            if deny_options is None or len(CAPTIONS['denial']) == 0:
                deny_text = 'Not for you~'
            else:
                deny_text = rand.choice(CAPTIONS['denial'])
            denyLabel = Label(label, text=deny_text, wraplength=resized_image.width - border_wid_const)
            denyLabel.place(x=int(resized_image.width / 2) - int(denyLabel.winfo_reqwidth() / 2),
                            y=int(resized_image.height / 2) - int(denyLabel.winfo_reqheight() / 2))

    locX = rand.randint(monitor.x, monitor.x + monitor.width - (resized_image.width))
    locY = rand.randint(monitor.y, max(monitor.y + monitor.height - (resized_image.height), 0))

    if LOWKEY_MODE:
        global LOWKEY_CORNER
        if LOWKEY_CORNER == 4:
            LOWKEY_CORNER = rand.randrange(0, 3)
        if LOWKEY_CORNER == 0:
            locX = monitor.width - (resized_image.width)
            locY = monitor.y
        elif LOWKEY_CORNER == 1:
            locX = monitor.x
            locY = monitor.y
        elif LOWKEY_CORNER == 2:
            locX = monitor.x
            locY = monitor.height - (resized_image.height)
        elif LOWKEY_CORNER == 3:
            locX = monitor.x + monitor.width - (resized_image.width)
            locY = monitor.y + monitor.height - (resized_image.height)
    else:
        if locX + resized_image.width > monitor.width:
            locX = monitor.width - (resized_image.width)
        if locX < monitor.x:
            locX = monitor.x
        if locY + resized_image.height > monitor.height:
            locY = monitor.height - (resized_image.height)
        if locY < monitor.y:
            locY = monitor.y

    root.geometry(f'{resized_image.width + border_wid_const - 1}x{resized_image.height + border_wid_const - 1}+{locX}+{locY}')

    if animated_gif:
        label.next_frame()

    if HAS_LIFESPAN or LOWKEY_MODE and not (HIBERNATE_TYPE == 'Pump-Scare' and HIBERNATE_MODE):
        thread.Thread(target=lambda: live_life(root, duration if video_mode else (LIFESPAN )), daemon=True).start()
    #if not LOWKEY_MODE else DELAY / 1000)), daemon=True).start()
    if not MULTI_CLICK:
        root.click_count = 1

    root.caption_text = caption_text

    if caption_text:
        root.caption_string = StringVar()
        root.caption_string.set(root.caption_text)
        captionLabel = Label(root, textvariable=root.caption_string, wraplength=resized_image.width - border_wid_const, bg=back, fg=fore)
        captionLabel.place(x=5, y=5)

    if CORRUPTION_DEVMODE:
        devmodeLabel1 = Label(root, text='clev=', wraplength=resized_image.width - border_wid_const, bg=back, fg=fore)
        devmodeLabel2 = Label(root, text='poplev=', wraplength=resized_image.width - border_wid_const, bg=back, fg=fore)
        devmodeLabel3 = Label(root, text=f'filen={pathlib.Path(item).name}', wraplength=resized_image.width - border_wid_const, bg=back, fg=fore)
        devmodeLabel1.place(x= 5, y= int(resized_image.height/2))
        devmodeLabel2.place(x= 5, y= int(resized_image.height/2) + devmodeLabel2.winfo_reqheight() + 2)
        devmodeLabel3.place(x= 5, y= int(resized_image.height/2) + devmodeLabel3.winfo_reqheight() + devmodeLabel2.winfo_reqheight() + 4)


    if BUTTONLESS:
        label.bind("<ButtonRelease-1>", buttonless_click)
    elif video_mode and NO_SKIP:
        pass
    else:
        root.button_string = StringVar()
        root.button_text = SUBMISSION_TEXT
        root.button_string.set(root.button_text)
        submit_button = Button(root, textvariable=root.button_string, command=click, bg=back, fg=fore, activebackground=back, activeforeground=fore)
        submit_button.place(x=resized_image.width - 25 - submit_button.winfo_reqwidth(), y=resized_image.height - 5 - submit_button.winfo_reqheight())

    if HIBERNATE_MODE and check_setting('fixWallpaper'):
        with open(Data.HIBERNATE, 'r+') as f:
            i = int(f.readline())
            f.seek(0)
            f.write(str(i+1))
            f.truncate()
    if video_mode:
        alpha = OPACITY
        if alpha >= 100:
            alpha = 100
        elif alpha >= 60:
            root.attributes('-alpha', min(alpha+20,100) / 100)
        else:
            alpha = rand.randint(80,100)
            root.attributes('-alpha', alpha / 100)
    else:
        root.attributes('-alpha', OPACITY / 100)

    if MOVING_STATUS:
        move_window(root,resized_image.height,resized_image.width,locX,locY)

    root.mainloop()

def startVLC(vid, label):
    #word of advice: if you go messing around with python-vlc there's almost no documentation for it
    #this is a hack that will repeat the video 999,999 times, because I tried to find something less terrible for hours but couldn't
    instance = vlc.Instance('--input-repeat=999999')
    media_player = instance.media_player_new()
    media_player.set_hwnd(label.winfo_id())
    media_player.video_set_mouse_input(False)
    media_player.video_set_key_input(False)
    media_player.audio_set_volume(int(VIDEO_VOLUME*100))

    media = instance.media_new(vid)
    media_player.set_media(media)
    media_player.play()
def startVLC_no_loop(vid, label, duration):
    import threading

    instance = vlc.Instance('--input-repeat=1') # if there's delay, the video will loop once. This should only be necessary in really bad cases
    media_player = instance.media_player_new()
    media_player.set_hwnd(label.winfo_id())
    media_player.video_set_mouse_input(False)
    media_player.video_set_key_input(False)
    media_player.audio_set_volume(int(VIDEO_VOLUME*100))

    media = instance.media_new(vid)
    media_player.set_media(media)
    media_player.play()
    t = threading.Timer(duration, die) #kill after duration
    t.start()
    stay_on_top();

def stay_on_top():
    root.lift()
    root.after(200, stay_on_top)

def check_deny() -> bool:
    return DENIAL_MODE and rand.randint(1, 100) <= DENIAL_CHANCE

def check_subliminal():
    global SUBLIMINAL_MODE
    with open(Data.MAX_SUBLIMINALS, 'r') as f:
        if int(f.readline()) >= MAX_SUBLIMINALS:
            SUBLIMINAL_MODE = False
        elif rand.randint(1, 100) > SUBLIMINAL_CHANCE:
            SUBLIMINAL_MODE = False

def live_life(parent:tk, length:int):
    while root.click_count > 0:
        time.sleep(length)
        click(allow_die=False)
    for i in range(100-OPACITY, 100):
        parent.attributes('-alpha', 1-i/100)
        time.sleep(FADE_OUT_TIME / 100)
    #if LOWKEY_MODE:
        #subprocess.Popen([sys.executable, Process.POPUP])
    if HIBERNATE_MODE and check_setting('fixWallpaper'):
        with open(Data.HIBERNATE, 'r+') as f:
            i = int(f.readline())
            if i > 0:
                f.seek(0)
                f.write(str(i-1))
                f.truncate()
    if len(SYS_ARGS) >= 1 and SYS_ARGS[0] == '-video':
        with open(Data.MAX_VIDEOS, 'r+') as f:
            i = int(f.readline())
            if i > 0:
                f.seek(0)
                f.write(str(i-1))
                f.truncate()
    if SUBLIMINAL_MODE:
        with open(Data.MAX_SUBLIMINALS, 'r+') as f:
            i = int(f.readline())
            if i > 0:
                f.seek(0)
                f.write(str(i-1))
                f.truncate()
    os.kill(os.getpid(), 9)

def do_roll(mod:float) -> bool:
    if mod >= 100:
        return True

    if mod <= 0:
        return False

    return mod > (rand.random() * 100)

def select_url(arg:str):
    #if MOOD_OFF:
    return web_dict['urls'][arg] + web_dict['args'][arg].split(',')[rand.randrange(len(web_dict['args'][arg].split(',')))]
    #else:
        #return web_mood_dict['urls'][arg] + web_mood_dict['args'][arg].split(',')[rand.randrange(len(web_mood_dict['args'][arg].split(',')))]

def buttonless_click(event):
    click()

def click(allow_die = True):
    # global click_count, caption_string, button_string

    root.click_count -= 1

    if root.click_count > 0:
        if BUTTONLESS:
            if root.caption_text:
                root.caption_string.set(root.caption_text + ' (' + str(root.click_count) + ')')

        else:
            root.button_string.set(root.button_text + ' (' + str(root.click_count) + ')')

            # Bring to front
            root.deiconify()

    else:
        if allow_die:
            die()

        else:
            if BUTTONLESS:
                if root.caption_text:
                    root.caption_string.set(root.caption_text)

            else:
                root.button_string.set(root.button_text)

def die():
    if WEB_OPEN and web_dict and do_roll((100-WEB_PROB) / 2) and not LOWKEY_MODE:
        urlPath = select_url(rand.randrange(len(web_dict['urls'])))
        webbrowser.open_new(urlPath)
    if MITOSIS_MODE:# or LOWKEY_MODE:
        for i in (range(0, MITOSIS_STRENGTH)): #if not LOWKEY_MODE else [1]):
            subprocess.Popen([sys.executable, Process.POPUP])
    if HIBERNATE_MODE and check_setting('fixWallpaper'):
        with open(Data.HIBERNATE, 'r+') as f:
            i = int(f.readline())
            if i > 0:
                f.seek(0)
                f.write(str(i-1))
                f.truncate()
    if len(SYS_ARGS) >= 1 and SYS_ARGS[0] == '-video':
        with open(Data.MAX_VIDEOS, 'r+') as f:
            i = int(f.readline())
            if i > 0:
                f.seek(0)
                f.write(str(i-1))
                f.truncate()
    if SUBLIMINAL_MODE:
        with open(Data.MAX_SUBLIMINALS, 'r+') as f:
            i = int(f.readline())
            if i > 0:
                f.seek(0)
                f.write(str(i-1))
                f.truncate()
    os.kill(os.getpid(), 9)

#def select_caption(filename:str) -> str:
#    for obj in CAPTIONS['prefix']:
#        if MOOD_FILENAME:
#            if MOOD_ID != '0':
#                if filename.startswith(obj) and obj in moodData['captions']:
#                    ls = CAPTIONS[obj]
#                    ls.extend(CAPTIONS['default'])
#                    return ls[rand.randrange(0, len(CAPTIONS[obj]))]
#            else:
#                if filename.startswith(obj):
#                    ls = CAPTIONS[obj]
#                    ls.extend(CAPTIONS['default'])
#                    return ls[rand.randrange(0, len(CAPTIONS[obj]))]
#        else:
#            if MOOD_ID != '0':
#                if obj in moodData['captions']:
#                    ls = CAPTIONS[obj]
#                    ls.extend(CAPTIONS['default'])
#                    return ls[rand.randrange(0, len(CAPTIONS[obj]))]
#    return CAPTIONS['default'][rand.randrange(0, len(CAPTIONS['default']))] if (len(CAPTIONS['default']) > 0) else None

def panic(key):
    key_condition = (key.keysym == PANIC_KEY or key.keycode == PANIC_KEY)
    if PANIC_REQUIRES_VALIDATION and key_condition:
        try:
            pass_ = simpledialog.askstring('Panic', 'Enter Panic Password')
            print('ASKING FOR PASS')
            t_hash = None if pass_ == None or pass_ == '' else hashlib.sha256(pass_.encode(encoding='ascii', errors='ignore')).hexdigest()
        except:
            #if some issue occurs with the hash or time files just emergency panic
            subprocess.Popen([sys.executable, Process.PANIC])
        print(t_hash)
        print(HASHED_PATH)
        if t_hash == HASHED_PATH:
            #revealing hidden files
            try:
                utils.show_file(Data.PASS_HASH)
                utils.show_file(Data.HID_TIME)
                os.remove(Data.PASS_HASH)
                os.remove(Data.HID_TIME)
                subprocess.Popen([sys.executable, Process.PANIC])
            except:
                #if some issue occurs with the hash or time files just emergency panic
                subprocess.Popen([sys.executable, Process.PANIC])
    else:
        if not PANIC_DISABLED and key_condition:
            subprocess.Popen([sys.executable, Process.PANIC])

def pumpScare():
    if HIBERNATE_MODE and HIBERNATE_TYPE == 'Pump-Scare':
        time.sleep(2.5)
        die()

if __name__ == '__main__':
    try:
        thread.Thread(target=pumpScare).start()
        run()
    except Exception as e:
        utils.init_logging(logging, 'popup')
        logging.fatal(f'failed to start popup\n{e}')
        #traceback.print_exc() 
