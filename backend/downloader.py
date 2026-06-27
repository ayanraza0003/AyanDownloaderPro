import sys
from pathlib import Path

import yt_dlp


def resource_path(relative_path):
    """
    Returns the correct path in development and in a PyInstaller build.
    """
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).resolve().parent.parent

    return str(base_path / relative_path)


class Downloader:
    def __init__(
        self,
        url,
        save_path,
        format_id,
        quality_name,
        mode,
        progress_hook=None,
    ):
        self.url = url
        self.save_path = save_path
        self.format_id = format_id
        self.quality_name = quality_name
        self.mode = mode
        self.progress_hook = progress_hook

    def download(self):

        if self.mode == "audio":
            format_string = "bestaudio"
        else:
            format_string = (
                f"{self.format_id}+140/"
                f"{self.format_id}+bestaudio/"
                "best"
            )

        ydl_opts = {
            "progress_hooks": (
                [self.progress_hook]
                if self.progress_hook
                else []
            ),
            "format": format_string,
            "outtmpl": (
                f"{self.save_path}/"
                f"%(title)s [{self.quality_name}].%(ext)s"
            ),
            "merge_output_format": "mp4",
            "ffmpeg_location": resource_path("bin"),
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])