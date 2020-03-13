from typing import Tuple, List, Optional

import cv2 as cv
import numpy as np
from PIL import Image

import utils

TEMPLATE = cv.imread("data/static/align_template.png", 0)
TEMPLATE_W, TEMPLATE_H = TEMPLATE.shape[::-1]


class ImageDto:

    filename: str
    dimensions: Tuple[int, int]
    template_location: Tuple[int, int]
    original_scale: float
    scaling_factor: Optional[float]

    def __init__(self,
                 filename: str,
                 dimensions: Tuple[int, int],
                 template_location: Tuple[int, int],
                 original_scale: float,
                 scaling_factor: Optional[float]):
        """DTO for information about each image.

        :param filename: Filename of the image
        :param dimensions: Tuple of dimensions of the image
        :param template_location: Tuple of template location within the image
        :param original_scale: Scale of the original image
        :param scaling_factor: How much to scale this image in order to normalize it with others
        """
        self.filename = filename
        self.dimensions = dimensions
        self.template_location = template_location
        self.original_scale = original_scale
        self.scaling_factor = scaling_factor


def detect_edges(image):
    """Returns edge detection image with fixed parameters.
    """
    return cv.Canny(image, 100, 300)


def intround(f: float) -> int:
    """Rounds float and converts it to int
    """
    return int(round(f))


def main():
    """Aligner stage - uses OpenCV to align the images.

    This stage locates the template image (grievous' eyes) in each image and aligns images so the template is always in
    the same position.
    """

    # generate templates of different scale to fix scaling issues
    scales = np.linspace(0.5, 1.2, num=100)
    templates = [detect_edges(cv.resize(TEMPLATE, (intround(TEMPLATE_W * scale), intround(TEMPLATE_H * scale)),
                                        interpolation=cv.INTER_AREA))
                 for scale in scales]

    image_dtos: List[ImageDto] = []

    # calculate template locations and template scaling, save them as ImageDto
    for fname in utils.get_images_in_dir(utils.RESIZED_LOCATION):

        if not fname.endswith(".png"):
            continue

        img = cv.imread(utils.RESIZED_LOCATION + fname, 0)
        # apply edge detection - it slightly improves template matching results
        img = detect_edges(img)

        # find the template scale that matches best and use the value to estimate image scale factor
        optimal_max_val = None
        optimal_location = None
        optimal_scale = None
        for scale, template in zip(scales, templates):
            res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

            if optimal_max_val is None or max_val > optimal_max_val:
                # new maximum found, save the solution
                optimal_max_val = max_val
                optimal_location = max_loc
                optimal_scale = scale

        # save data, scaling factor is unknown at this point
        image_dtos.append(ImageDto(fname, img.shape[::-1], optimal_location, optimal_scale, None))

    # maximum distances from template to all borders, used for calculation of aligned image size and alignment
    # these are calculated with respect to scaling factor
    max_left, max_right, max_top, max_bottom = 0, 0, 0, 0

    # find minimum original scale to use for rescaling calculations
    min_original_scale = min(image_dto.original_scale for image_dto in image_dtos)

    # calculate scaling factors and maximum distances from template to all borders
    for image_dto in image_dtos:

        # calculate scaling factor
        # inverse proportional to original_scale - we want to downsize larger images to fit the smallest one
        image_dto.scaling_factor = min_original_scale / image_dto.original_scale

        template_x, template_y = image_dto.template_location
        original_width, original_height = image_dto.dimensions

        # calculate max distances to borders, scaling factor must be applied here
        max_left = max(max_left, template_x * image_dto.scaling_factor)
        max_top = max(max_top, template_y * image_dto.scaling_factor)
        max_right = max(max_right, (original_width - template_x) * image_dto.scaling_factor)
        max_bottom = max(max_bottom, (original_height - template_y) * image_dto.scaling_factor)

    # convert floats to ints
    max_left = intround(max_left)
    max_top = intround(max_top)
    max_right = intround(max_right)
    max_bottom = intround(max_bottom)

    new_w, new_h = max_left + max_right, max_top + max_bottom
    print(f"New dimensions: {new_w} x {new_h}")

    # do the actual alignment and scaling based on the calculated size of the new image
    for image_dto in image_dtos:

        original = Image.open(utils.RESIZED_LOCATION + image_dto.filename)

        # apply scaling (correct for scaling factor)
        resize_dimension = tuple(intround(dim * image_dto.scaling_factor) for dim in image_dto.dimensions)
        original = original.resize(resize_dimension, Image.ANTIALIAS)

        # start with blank (white) image
        aligned = Image.new("RGB", (new_w, new_h), color=(255, 255, 255, 0))

        # calculate paste location and paste original to the image
        paste_x = max_left - intround(image_dto.template_location[0] * image_dto.scaling_factor)
        paste_y = max_top - intround(image_dto.template_location[1] * image_dto.scaling_factor)
        aligned.paste(original, box=(paste_x, paste_y))

        aligned.save(utils.ALIGNED_LOCATION + image_dto.filename)


if __name__ == "__main__":
    main()
