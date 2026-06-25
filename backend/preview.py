from yt_dlp import YoutubeDL


class PreviewManager:

    def __init__(self):
        self.ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }

    def get_info(self, url):
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            return {
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "views": info.get("view_count"),
                "formats": info.get("formats"),
            }

        except Exception as e:
            return {
                "error": str(e)
            }