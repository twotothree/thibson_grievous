import re
import urllib

import praw

import utils

RE_TITLE = "^Every day General Grievous adds a unique lightsaber to his collection. Day (\\d+): ([^\\.]+)\\.?$"


def process_thibson_post(post):
    # Extract day number and lightsaber name from post title
    matches = re.match(RE_TITLE, post.title)

    if matches is None:
        # post is not about Grievous collection, skip
        return False

    number, title = matches.group(1), matches.group(2)

    if any(f.split("_")[0] == number for f in utils.get_images_in_dir(utils.DOWNLOAD_LOCATION)):
        # post already downloaded, skipping
        return False

    print(f"Downloading image from day {number}: {title}")
    urllib.request.urlretrieve(post.url, utils.DOWNLOAD_LOCATION + f"{number}_{title}.png")

    return True


def main() -> bool:
    """Downloader stage - downloads submissions from Reddit.

    :return: True if new submissions are downloaded, False otherwise.
    """

    reddit = praw.Reddit("thibson_downloader", user_agent="PRAW")

    thibson34 = reddit.redditor("thibson34")

    new_downloads = False

    for post in thibson34.submissions.new():
        if process_thibson_post(post):
            new_downloads = True

    return new_downloads


if __name__ == "__main__":
    main()
