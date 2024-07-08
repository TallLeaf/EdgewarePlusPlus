import threading as thread
import time
from tkinter import RAISED, Frame, Label, Toplevel

from PIL import Image, ImageTk
from utils.paths import Defaults, Resource


def animate(top, callback):
    alpha = 0.0
    step = 0.01
    for i in range(int(1 / step)):
        top.attributes("-alpha", alpha)
        alpha += step
        time.sleep(step)
    time.sleep(2)
    for i in range(int(1 / (2 * step))):
        top.attributes("-alpha", alpha)
        alpha -= 2 * step
        time.sleep(step / 4)

    top.destroy()
    callback()


def make_startup_flair(settings, callback):
    top = Toplevel()
    top.configure(bg="black")
    top.frame = Frame(top, borderwidth=2, relief=RAISED)
    top.wm_attributes("-topmost", 1)
    top.overrideredirect(True)

    scalar = 0.6
    image_ = Image.open(Resource.SPLASH if Resource.SPLASH else Defaults.SPLASH)
    image = ImageTk.PhotoImage(
        image_.resize((int(image_.width * scalar), int(image_.height * scalar)), resample=(Image.LANCZOS if settings.LANCZOS_MODE else Image.ANTIALIAS))
    )

    top.geometry(
        "{}x{}+{}+{}".format(
            image.width(), image.height(), int((top.winfo_screenwidth() - image.width()) / 2), int((top.winfo_screenheight() - image.height()) / 2)
        )
    )
    label = Label(top, image=image)
    label.image = image  # We need to keep a reference to the image, otherwise it will fail to display
    label.pack()
    top.attributes("-alpha", 0)

    thread.Thread(target=lambda: animate(top, callback)).start()
