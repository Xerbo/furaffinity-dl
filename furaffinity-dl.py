#!/usr/bin/python3
import contextlib
import http.cookiejar as cookielib
import os
from time import sleep

import requests
from bs4 import BeautifulSoup

import Modules.config as config
from Modules.functions import download_complete
from Modules.functions import download
from Modules.functions import login
from Modules.functions import next_button
from Modules.functions import system_message_handler

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
                    f'{config.WARN_COLOR}Reached page "{config.stop}", stopping.{config.END}'
                )
                break

            page_url = f"{download_url}/{page_num}"
            response = session.get(page_url)
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
                download(img.find("a").attrs.get("href"))
                sleep(config.interval)

            page_num = next_button(page_url)


if __name__ == "__main__":
    if config.login is True:
        login(config.user_agent)

    try:
        response = session.get(config.BASE_URL)
    except ConnectionError:
        print(f"{config.ERROR_COLOR}Connection failed{config.END}")
        exit()
    except KeyboardInterrupt:
        print(f"{config.WARN_COLOR}Aborted by user{config.END}")
        exit()

    s = BeautifulSoup(response.text, "html.parser")
    if s.find(class_="loggedin_user_avatar") is not None:
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print(f'{config.SUCCESS_COLOR}Logged in as "{account_username}"{config.END}')
    else:
        print(
            f"{config.WARN_COLOR}Not logged in, NSFW content is inaccessible{config.END}"
        )

    if config.download is not None:
        download(config.download)
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

    if os.path.exists(config.username[0]):
        data = open(config.username[0]).read()
        config.username = filter(None, data.split("\n"))

    for username in config.username:
        print(f'{config.SUCCESS_COLOR}Now downloading "{username}"{config.END}')
        download_url = f"{config.BASE_URL}/{config.category}/{username}"
        main()
        print(
            f'{config.SUCCESS_COLOR}Finished \
downloading "{username}"{config.END}'
        )
