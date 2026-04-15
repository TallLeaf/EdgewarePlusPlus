import os
import sys
from utils import utils
from utils.paths import Data, Defaults
from datetime import datetime, timedelta

# Checking timer
try:
    utils.show_file(Data.HID_TIME)
except:
    ''

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)
skipped = 0
temp = 0
time = 0
d = 0


try:
    with open(Data.SKIPPED_COUNTER, 'r') as f:
        skipped = int(f.readline())
        temp = f.readline()
    time = datetime.strptime(temp, '%m/%d/%y %H:%M:%S')    
    d = datetime.now() - time
    with open(Data.SKIPPED_COUNTER, 'w') as f:
        f.write(str(skipped + 1)+'\n')
        f.write(datetime.now().strftime('%m/%d/%y %H:%M:%S'))
except Exception as e:
    with open("error.txt", 'w') as f:
        f.write(str(e))

if os.path.exists(Data.HID_TIME):
    utils.hide_file(Data.HID_TIME)
    # Do nothing if timer is present
elif len(SYS_ARGS) == 0:
    # Continue if no timer
    utils.set_wallpaper(Defaults.PANIC_WALLPAPER)
    utils.panic_script()
else:
    utils.set_wallpaper(Defaults.PANIC_WALLPAPER)
    utils.restart_script()