import base64

import requests


def encode_image_from_url_to_data_image(url: str):
    response = requests.get(url)

    base64_string = base64.b64encode(response.content).decode("utf-8")

    return f"data:image/png;base64,{base64_string}"
