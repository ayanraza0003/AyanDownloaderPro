from io import BytesIO
import requests
from PIL import Image


class ThumbnailManager:

    def get_image(self, url):
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        return image