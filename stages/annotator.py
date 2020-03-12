from PIL import Image, ImageDraw, ImageFont

import utils


def main():
    """Annotator stage - uses PIL to annotate images with lightsaber names.
    """

    # get width and height from an aligned image
    sample_img = Image.open(utils.ALIGNED_LOCATION + utils.get_images_in_dir(utils.ALIGNED_LOCATION)[0])
    w, h = sample_img.size
    sample_img.close()

    # calculate font size based on image height
    font = ImageFont.truetype("data/static/Audiowide-Regular.ttf", h // 20)
    # calculate top and bottom margins based on font size
    top_margin = font.size // 8
    # calculate image offset (top) and new image dimensions
    top_offset = font.size + 2 * top_margin
    new_w, new_h = w, h + top_offset

    for fname in utils.get_images_in_dir(utils.ALIGNED_LOCATION):

        number, name = fname.split("_")
        # remove extensions form lightsaber name
        name = name[:name.rindex(".")]

        # offset the image to make room for annotations
        original = Image.open(utils.ALIGNED_LOCATION + fname)
        annotated = Image.new(original.mode, (new_w, new_h), color=(255, 255, 255, 0))
        annotated.paste(original, box=(0, top_offset))

        draw = ImageDraw.Draw(annotated)
        # center the text using textsize
        text_w, text_h = draw.textsize(name, font=font)
        text_loc = ((w - text_w) / 2, top_margin)
        draw.text(text_loc, name, font=font, fill="#2d2e33")

        annotated.save(utils.ANNOTATED_LOCATION + fname)


if __name__ == "__main__":
    main()
