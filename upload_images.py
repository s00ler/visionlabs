from os import path, listdir

import requests


def upload_images(dirpath, url='host:port/images'):
    """Upload images from directory.

    Assuming that target directory contains only images.
    Otherwise may filter files by extension.

    P.S. Hope that use of requests is not forbidden by task rules =)
    """
    files = listdir(path.abspath(dirpath))
    payload = [('images', open(path.abspath(file), 'rb')) for file in files if path.splitext]
    return requests.post(url, files=payload)
