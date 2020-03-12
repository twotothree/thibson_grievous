import cv2 as cv

import utils


def main():
    """Composer stage - uses OpenCV to compose annotated images to an mp4 video.
    """

    fnames = utils.get_images_in_dir(utils.ANNOTATED_LOCATION)

    # get frame width and height from the first frame
    frame = cv.imread(utils.ANNOTATED_LOCATION + fnames[0])
    frame_height, frame_width, channels = frame.shape
    # frames are huge, downsize them to a reasonable resolution, width is fixed and height is calculated to retain
    # aspect ratio
    video_width = 1440
    video_height = int((video_width / frame_width) * frame_height)

    # use mp4 codec, 1 frame per second
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter("data/grievous.mp4", fourcc, 1.0, (video_width, video_height))

    for i, fname in enumerate(fnames):

        print(f"Writing frame {i}")

        frame = cv.imread(utils.ANNOTATED_LOCATION + fname)
        # downsize frame
        frame = cv.resize(frame, (video_width, video_height), interpolation=cv.INTER_AREA)

        # if this is the last frame, repeat it five times (for a total of 5 seconds)
        repeat = 5 if i == len(fnames) - 1 else 1

        for _ in range(repeat):
            out.write(frame)

    out.release()


if __name__ == "__main__":
    main()
