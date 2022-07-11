#!/usr/bin/python3
import contextlib
import http.cookiejar as cookielib
import os
from time import sleep

import requests
from bs4 import BeautifulSoup

import Modules.config as config
from Modules.download import download
from Modules.functions import check_filter
from Modules.functions import download_complete
from Modules.functions import login
from Modules.functions import next_button
from Modules.functions import requests_retry_session
from Modules.functions import system_message_handler
from Modules.index import check_file
from Modules.index import start_indexing

# get session
session = requests.session()
session.headers.update({"User-Agent": config.user_agent})

if config.cookies is not None:  # add cookies if present
    cookies = cookielib.MozillaCookieJar(config.cookies)
    cookies.load()
    session.cookies = cookies


def main():
    # download loop
    page_num = config.start
    with contextlib.suppress(download_complete):
        while True:
            if config.stop == page_num:
                print(
                    f'{config.WARN_COLOR}Reached page "{config.stop}", \
stopping.{config.END}'
                )
                break

            page_url = f"{download_url}/{page_num}"
            response = requests_retry_session(session=session).get(page_url)
            s = BeautifulSoup(response.text, "html.parser")

            # System messages
            if s.find(class_="notice-message") is not None:
                system_message_handler(s)

            # End of gallery
            if s.find(id="no-images") is not None:
                print(f"{config.SUCCESS_COLOR}End of gallery{config.END}")
                break

            # Download all images on the page
            for img in s.findAll("figure"):
                title = img.find("figcaption").contents[0].text
                img_url = img.find("a").attrs.get("href")

                if config.submission_filter is True and check_filter(title) is True:
                    print(
                        f'{config.WARN_COLOR}"{title}" was filtered and will not be \
downloaded - {config.BASE_URL}{img_url}{config.END}'
                    )
                    continue

                if config.dont_redownload is True and check_file(img_url) is True:
                    if config.check is True:
                        print(
                            f'{config.SUCCESS_COLOR}Downloaded all recent files of \
"{username}"{config.END}'
                        )
                        raise download_complete
                    print(
                        f'{config.WARN_COLOR}Skipping "{title}" since \
it\'s already downloaded{config.END}'
                    )
                    continue

                download(img_url)
                sleep(config.interval)

            page_num = next_button(page_url)


if __name__ == "__main__":
    if config.login is True:
        login()
        exit()

    if config.index is True:
        if os.path.isfile(f"{config.output_folder}/index.idx"):
            os.remove(f"{config.output_folder}/index.idx")
        start_indexing(config.output_folder)
        print(f"{config.SUCCESS_COLOR}indexing finished{config.END}")
        exit()

    try:
        response = requests_retry_session(session=session).get(config.BASE_URL)
    except KeyboardInterrupt:
        print(f"{config.WARN_COLOR}Aborted by user{config.END}")
        exit()

    s = BeautifulSoup(response.text, "html.parser")
    if s.find(class_="loggedin_user_avatar") is not None:
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print(
            f'{config.SUCCESS_COLOR}Logged in as \
"{account_username}"{config.END}'
        )
    else:
        print(
            f"{config.WARN_COLOR}Not logged in, NSFW content \
is inaccessible{config.END}"
        )

    if config.download is not None:
        download(f"/view/{config.download}/")
        exit()

    if config.submissions is True:
        download_url = f"{config.BASE_URL}/msg/submissions"
        main()
        print(
            f"{config.SUCCESS_COLOR}Finished \
downloading submissions{config.END}"
        )
        exit()

    if config.folder is not None:
        folder = config.folder.split("/")
        download_url = (
            f"{config.BASE_URL}/gallery/{config.username}/folder/{config.folder[1]}"
        )
        main()
        print(
            f'{config.SUCCESS_COLOR}Finished \
downloading "{config.folder[1]}"{config.END}'
        )
        exit()

    if config.category not in ["gallery", "scraps", "favorites"]:
        print(
            f"{config.ERROR_COLOR}Please enter a valid category [gallery/scraps/favorites] {config.END}"
        )
        exit()

    try:
        if os.path.exists(config.username[0]):
            data = open(config.username[0]).read()
            config.username = filter(None, data.split("\n"))
    except TypeError or AttributeError:
        print(
            f"{config.ERROR_COLOR}Please enter a username \
or provide a file with usernames (1 username per line){config.END}"
        )
        exit()

    for username in config.username:
        username = username.split("#")[0].translate(
            str.maketrans(config.username_replace_chars)
        )
        if username != "":
            print(f'{config.SUCCESS_COLOR}Now downloading "{username}"{config.END}')
            download_url = f"{config.BASE_URL}/{config.category}/{username}"
            print(f"Downloading page {config.start} - {download_url}/{config.start}")
            main()
            print(
                f'{config.SUCCESS_COLOR}Finished \
downloading "{username}"{config.END}'
            )
