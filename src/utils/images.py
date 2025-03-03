import base64
import logging

import requests


def encode_image_from_url_to_data_image(url: str) -> str:
    """
    Encode an image from a URL to a data URL.

    Parameters
    ----------
    url : str
        The URL of the image.

    Returns
    -------
    str
        The data URL of the image.
    """

    logging.info("Encoding image from URL...")

    response = requests.get(url)

    base64_string = base64.b64encode(response.content).decode("utf-8")

    return f"data:image/png;base64,{base64_string}"
