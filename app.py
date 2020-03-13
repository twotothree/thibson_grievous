"""Thibson34 Grievous Collection Downloader

This script downloads the Grievous Collection submissions from u/thibson34, aligns and annotates them and then
composes them in a video file.
"""

from stages import downloader, composer, annotator, aligner, resizer


def main():
    print("Downloading images from Reddit ...")
    new_downloads = downloader.main()

    if not new_downloads:
        print("No new submissions, exiting.")
        return

    print("Resizing images ...")
    resizer.main()

    print("Aligning images ...")
    aligner.main()

    print("Annotating images ...")
    annotator.main()

    print("Composing video ...")
    composer.main()

    print("Done!")


if __name__ == "__main__":
    main()
