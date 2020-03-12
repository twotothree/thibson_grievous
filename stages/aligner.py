from typing import Tuple, List

import cv2 as cv
import utils
from PIL import Image

TEMPLATE = cv.imread("data/static/align_template.png", 0)
TEMPLATE_W, TEMPLATE_H = TEMPLATE.shape[::-1]


class ImageDto:

    filename: str
    dimensions: Tuple[int, int]
    template_location: Tuple[int, int]

    def __init__(self, filename: str, dimensions: Tuple[int, int], template_location: Tuple[int, int]):
        """DTO for information about each image.

        :param filename: Filename of the image
        :param dimensions: Tuple of dimensions of the image
        :param template_location: Tuple of template location within the image
        """
        self.filename = filename
        self.dimensions = dimensions
        self.template_location = template_location


def main():
    """Aligner stage - uses OpenCV to align the images.

    This stage locates the template image (grievous' eyes) in each image and aligns images so the template is always in
    the same position.
    """

    # maximum distances from template to all borders, used for calculation of aligned image size and alignment
    max_left, max_right, max_top, max_bottom = 0, 0, 0, 0

    image_dtos: List[ImageDto] = []

    # calculate template locations and maximum distances from template to all borders
    for fname in utils.get_images_in_dir(utils.DOWNLOAD_LOCATION):

        if not fname.endswith(".png"):
            continue

        img = cv.imread(utils.DOWNLOAD_LOCATION + fname, 0)

        res = cv.matchTemplate(img, TEMPLATE, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        # max_loc is the (most probable) location of the template within the image
        x, y = max_loc
        # image size
        w, h = img.shape[::-1]
        # max distances to borders
        max_left = max(max_left, x)
        max_top = max(max_top, y)
        max_right = max(max_right, w - x)
        max_bottom = max(max_bottom, h - y)

        # debug - draw rectangle around template on the original image
        # cv.rectangle(img, max_loc, (max_loc[0] + w, max_loc[1] + h), 10, 2)

        # save data
        image_dtos.append(ImageDto(fname, (w, h), (x, y)))

    new_w, new_h = max_left + max_right, max_top + max_bottom
    print(f"New dimensions: {new_w} x {new_h}")

    # do the actual alignment based on the calculated size of the new image
    for image_dto in image_dtos:

        original = Image.open(utils.DOWNLOAD_LOCATION + image_dto.filename)
        aligned = Image.new("RGB", (new_w, new_h), color=(255, 255, 255, 0))

        # calculate paste location and paste original to the image
        paste_x, paste_y = max_left - image_dto.template_location[0], max_top - image_dto.template_location[1]
        aligned.paste(original, box=(paste_x, paste_y))

        aligned.save(utils.ALIGNED_LOCATION + image_dto.filename)


if __name__ == "__main__":
    main()
