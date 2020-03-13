import math
from typing import Tuple

import cv2 as cv
import numpy as np

import utils

FPS = 20


def distance(p1: Tuple[int, int], p2: Tuple[int, int]):
    """Calculate distance between two points.
    """
    x1, y1 = p1
    x2, y2 = p2

    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def create_circle_mask(shape: Tuple[int, int, int], center: Tuple[int, int], radius: float):
    """Create a mask containing a fading out circle.
    """
    mask = np.zeros(shape, dtype=np.float32)

    for x in range(shape[0]):
        for y in range(shape[1]):

            d = distance((x, y), center)

            if d < radius:
                mask[x, y, :] = 1 - d / radius

    return mask


def main():
    """Composer stage - uses OpenCV to compose annotated images to an mp4 video.
    """

    fnames = utils.get_images_in_dir(utils.ANNOTATED_LOCATION)

    # get frame width and height from the first frame
    frame = cv.imread(utils.ANNOTATED_LOCATION + fnames[0])
    frame_height, frame_width, channels = frame.shape

    # use mp4 codec, 1 frame per second
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter("data/grievous.mp4", fourcc, FPS, (frame_width, frame_height))

    # create masks for each frame in a second
    masks = [create_circle_mask((frame_height, frame_width, 3), (frame_width // 2, frame_height // 2), radius)
             for radius in np.linspace(50, frame_width * 3, FPS)]

    # top margin (title) should always be foreground
    top_margin = frame_height // 16
    for mask in masks:
        mask[0:top_margin, :, :] = 1

    previous_frame = None
    buffer_foreground = np.float32(frame.copy())
    buffer_background = np.float32(frame.copy())

    for i, fname in enumerate(fnames):

        print(f"Writing frame {i}")

        frame = cv.imread(utils.ANNOTATED_LOCATION + fname)
        # downsize frame
        frame = np.float32(frame)

        # if this is the last frame, repeat it five times (for a total of 5 seconds)
        repeat = 5 if i == len(fnames) - 1 else 1

        for repeat_idx in range(repeat):
            for frame_idx in range(FPS):
                if previous_frame is None or repeat_idx > 0:
                    # first image and repeats require no masking
                    out.write(frame.astype(np.uint8))
                else:
                    # apply mask - creates animation (new frame fades in radially from the center)
                    mask = masks[frame_idx]
                    cv.multiply(mask, frame, buffer_foreground)
                    cv.multiply(1 - mask, previous_frame, buffer_background)

                    # reuse buffer_background for final frame
                    cv.add(buffer_background, buffer_foreground, buffer_background)

                    out.write(buffer_background.astype(np.uint8))

        previous_frame = frame

    out.release()


if __name__ == "__main__":
    main()
