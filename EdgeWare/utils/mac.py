from pathlib import Path


def panic_script():
    pass


def set_borderless(root):
    pass


def set_vlc_window(media_player, window_id):
    media_player.set_nsobject(window_id)


def set_wallpaper(wallpaper_path: Path | str):
    pass


def hide_file(path: Path | str):
    pass


def show_file(path: Path | str):
    pass


def open_directory(url: str):
    pass


def does_desktop_shortcut_exist(name: str):
    pass


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> bool:
    pass


def toggle_run_at_startup(state: bool):
    pass
