from typing import Tuple

import cv2 as cv
import numpy as np

import utils

FPS = 20


def create_circle_mask(shape: Tuple[int, int, int], center: Tuple[int, int], radius: float):
    """Create a mask containing a fading out circle.
    """
    mask = np.zeros(shape, dtype=np.float32)

    # x = [[0, 0, ..., 0], [1, 1, ..., 1], ...] and y = [[0, 1, 2, ..., y], [0, 1, 2, ..., y], ...]
    x, y = np.mgrid[0:shape[0], 0:shape[1]]

    # calculate matrix of distances from center
    distances = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
    # extend x*y array to x*y*3 (add channels)
    channel_distances = np.repeat(distances[:, :, np.newaxis], 3, axis=2)
    # only update where condition is met
    update_mask = channel_distances < radius
    # value of the cell is proportional to its distance from center
    mask[update_mask] = (1 - channel_distances / radius)[update_mask]

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
