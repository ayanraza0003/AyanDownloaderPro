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

            allowed = [2160, 1440, 1080, 720, 480, 360, 240, 144]

            qualities = {}

            formats = sorted(
                info.get("formats", []),
                key=lambda f: (
                    f.get("height") or 0,
                    f.get("tbr") or 0
                ),
                reverse=True
            )

            for height in allowed:
                for fmt in formats:
                    if fmt.get("height") != height:
                        continue

                    # Skip audio-only
                    if fmt.get("vcodec") == "none":
                        continue

                    # Prefer MP4/H264 video
                    if fmt.get("ext") != "mp4":
                        continue

                    qualities[f"{height}p"] = fmt["format_id"]
                    break

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