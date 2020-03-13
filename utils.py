import os
from typing import List

DOWNLOAD_LOCATION = "data/downloaded/"
RESIZED_LOCATION = "data/resized/"
ALIGNED_LOCATION = "data/aligned/"
ANNOTATED_LOCATION = "data/annotated/"


def get_images_in_dir(path: str) -> List[str]:
    """Returns a sorted list of all filenames of PNG files in directory.

    PNG should begin with a number, followed by underscore (e.g. 10_hello.png). This number is the key for sorting.
    """

    return sorted([f for f in os.listdir(path) if f.endswith(".png")], key=lambda f: int(f.split("_")[0]))
