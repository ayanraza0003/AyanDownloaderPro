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

            allowed = {2160, 1440, 1080, 720, 480, 360, 240, 144}

            qualities = []

            for fmt in info.get("formats", []):
                height = fmt.get("height")

                if height in allowed:
                    qualities.append(f"{height}p")

            qualities = sorted(
                set(qualities),
                key=lambda x: int(x[:-1]),
                reverse=True
            )

            return {
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "views": info.get("view_count"),
                "qualities": qualities,
            }

        except Exception as e:
            return {
                "error": str(e)
            }