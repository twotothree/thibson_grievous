from PIL import Image

import utils

MIN_DIMENSIONS = (1280, 1024)


def main():
    """Resizer stage - this is only a dumb resize in order to speed-up further processing.

    Adjusting for scaling errors is done in the aligner stage.
    """

    for fname in utils.get_images_in_dir(utils.DOWNLOAD_LOCATION):

        img = Image.open(utils.DOWNLOAD_LOCATION + fname)
        # thumbnail respects the aspect ratio
        img.thumbnail(MIN_DIMENSIONS, Image.ANTIALIAS)

        img.save(utils.RESIZED_LOCATION + fname)


if __name__ == "__main__":
    main()
