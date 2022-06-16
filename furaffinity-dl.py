#!/usr/bin/python3
import argparse
import http.cookiejar as cookielib
import json
import os
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Argument parsing
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="Downloads the entire gallery/scraps/favorites of a furaffinity user, or your submissions",
    epilog="""
Examples:
 python3 furaffinity-dl.py koul koul_gallery
 python3 furaffinity-dl.py -o koulsArt gallery koul
 python3 furaffinity-dl.py -o mylasFavs --category favorites mylafox\n
You can also log in to FurAffinity in a web browser and load cookies to download Age restricted content or Submissions:
 python3 furaffinity-dl.py -c cookies.txt gallery letodoesart
 python3 furaffinity-dl.py -c cookies.txt --submissions\n
DISCLAIMER: It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them.
""",
)

# General stuff
parser.add_argument(
    "--category",
    "-ca",
    type=str,
    nargs="?",
    help="the category to download, gallery/scraps/favorites [default: gallery]",
    const=1,
    default="gallery",
)
parser.add_argument(
    "--submissions",
    "-su",
    action="store_true",
    help="download your submissions",
)
parser.add_argument(
    "username",
    type=str,
    help="username of the furaffinity user [required]",
)
parser.add_argument(
    "--folder",
    type=str,
    help="full path of the furaffinity folder. for instance 123456/Folder-Name-Here",
)
parser.add_argument(
    "--output", type=str, default="furaffinity-dl", help="output directory [default: furaffinity-dl]"
)
parser.add_argument(
    "--cookies",
    "-c",
    dest="cookies",
    type=str,
    help="path to a NetScape cookies file",
)
parser.add_argument(
    "--user-agent",
    "-u",
    dest="ua",
    type=str,
    nargs="?",
    default="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.7) Gecko/20100101 Firefox/68.7",
    help="Your browser's useragent, may be required, depending on your luck",
)
parser.add_argument(
    "--start", "-s", type=str, default=1, help="page number to start from", nargs="?"
)
parser.add_argument(
    "--stop",
    "-S",
    dest="stop",
    type=str,
    help="Page number to stop on. For favorites pages, specify the full URL after the username (1234567890/next).",
)
parser.add_argument(
    "--dont-redownload",
    "-d",
    action="store_false",
    help="Don't redownload files that have already been downloaded [default: true]",
)
parser.add_argument(
    "--interval",
    "-i",
    dest="interval",
    type=float,
    default=0,
    help="delay between downloading pages in seconds [default: 0]",
)
parser.add_argument(
    "--rating",
    "-r",
    action="store_false",
    help="enable rating separation [default: true]",
)
parser.add_argument(
    "--metadata",
    "-m",
    action="store_true",
    help="enable downloading of metadata [default: false]",
)

args = parser.parse_args()

BASE_URL = "https://www.furaffinity.net"
categories = {
    "gallery": "gallery",
    "scraps": "scraps",
    "favorites": "favorites",
}
category = categories.get(args.category)
if category is None:
    print("please enter a valid category")
    exit()
if args.username is None:
    print("please enter a FA Username")
    exit()
if args.output is None:
    print("please enter a output folder")
    exit()

username = args.username
output = f"{args.output}/{args.username}"
metadata = f"{output}/metadata"

filter = {"YCH Open", "Reminder", "YCH Closed", "Auction"}

session = requests.session()
session.headers.update({"User-Agent": args.ua})

if args.cookies is not None:
    cookies = cookielib.MozillaCookieJar(args.cookies)
    cookies.load()
    session.cookies = cookies


def download_file(url, fname, desc):
    r = session.get(url, stream=True)
    if r.status_code != 200:
        print(f"Got a HTTP {r.status_code} while downloading {fname}; ...skipping")
        return False

    total = int(r.headers.get("Content-Length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=desc.ljust(40)[:40],
        total=total,
        miniters=100,
        unit="b",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in r.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    return True


download_url = f"{BASE_URL}/{category}/{username}"
if args.folder is not None:
    download_url = f"{BASE_URL}/gallery/{username}/folder/{args.folder}"
if args.submissions is True:
    download_url = f"{BASE_URL}/msg/submissions"


def download(path):
    response = session.get(f"{BASE_URL}{path}")
    s = BeautifulSoup(response.text, "html.parser")

    # System messages
    if s.find(class_="notice-message") is not None:
        message = (
            s.find(class_="notice-message")
            .find("div")
            .find(class_="link-override")
            .text.strip()
        )
        raise Exception("System Message", message)

    image = s.find(class_="download").find("a").attrs.get("href")
    title = s.find(class_="submission-title").find("p").contents[0]
    filename = image.split("/")[-1:][0]
    data = {
        "id": int(path.split("/")[-2:-1][0]),
        "filename": filename,
        "author": s.find(class_="submission-id-sub-container")
        .find("a")
        .find("strong")
        .text,
        "date": s.find(class_="popup_date").attrs.get("title"),
        "title": title,
        "description": s.find(class_="submission-description")
        .text.strip()
        .replace("\r\n", "\n"),
        "tags": [],
        "category": s.find(class_="info").find(class_="category-name").text,
        "type": s.find(class_="info").find(class_="type-name").text,
        "species": s.find(class_="info").findAll("div")[2].find("span").text,
        "gender": s.find(class_="info").findAll("div")[3].find("span").text,
        "views": int(s.find(class_="views").find(class_="font-large").text),
        "favorites": int(s.find(class_="favorites").find(class_="font-large").text),
        "rating": s.find(class_="rating-box").text.strip(),
        "comments": [],
    }

    match = re.search(
        "reminder|auction|YCH Open|YCH Closed|Adopt|pre-order", title, re.IGNORECASE
    )
    if match is not None and title == match.string:
        print(f"post {title} was filtered and will not be downloaded")
        return True

    # Extact tags
    try:
        for tag in s.find(class_="tags-row").findAll(class_="tags"):
            data["tags"].append(tag.find("a").text)
    except AttributeError:
        print(f'post: "{title}", has no tags')

    image_url = f"https:{image}"
    os.makedirs(output, exist_ok=True)
    output_path = f"{output}/{filename}"
    if args.rating is True:
        os.makedirs(f'{output}/{data.get("rating")}', exist_ok=True)
        output_path = f'{output}/{data.get("rating")}/{filename}'
    if args.folder is not None:
        os.makedirs(f"{output}/{args.folder}", exist_ok=True)
        output_path = f"{output}/{args.folder}/{filename}"
        if args.rating is True:
            os.makedirs(f'{output}/{args.folder}/{data.get("rating")}', exist_ok=True)
            output_path = f'{output}/{args.folder}/{data.get("rating")}/{filename}'

    if args.dont_redownload is True and os.path.isfile(output_path):
        print(f'Skipping "{title}", since it\'s already downloaded')
    else:
        download_file(image_url, output_path, title)

    if args.metadata is True:
        # Extract comments
        for comment in s.findAll(class_="comment_container"):
            temp_ele = comment.find(class_="comment-parent")
            parent_cid = (
                None if temp_ele is None else int(temp_ele.attrs.get("href")[5:])
            )
            # Comment is deleted or hidden
            if comment.find(class_="comment-link") is None:
                continue

            data["comments"].append(
                {
                    "cid": int(
                        comment.find(class_="comment-link").attrs.get("href")[5:]
                    ),
                    "parent_cid": parent_cid,
                    "content": comment.find(class_="comment_text").contents[0].strip(),
                    "username": comment.find(class_="comment_username").text,
                    "date": comment.find(class_="popup_date").attrs.get("title"),
                }
            )

        # Write a UTF-8 encoded JSON file for metadata
        os.makedirs(metadata, exist_ok=True)
        with open(
            os.path.join(metadata, f"{filename}.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    return True


# Main downloading loop
def main():
    page_end = args.stop
    page_num = args.start
    page_url = f"{download_url}/{page_num}"
    response = session.get(page_url)
    s = BeautifulSoup(response.text, "html.parser")
    if s.find(class_="loggedin_user_avatar") is not None:
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print("Logged in as", account_username)
    else:
        print("Not logged in, NSFW content is inaccessible")

    while True:
        if page_end == page_num:
            print(f"Reached page {page_end}, stopping.")
            break

        page_url = f"{download_url}/{page_num}"
        response = session.get(page_url)
        s = BeautifulSoup(response.text, "html.parser")

        # System messages
        if s.find(class_="notice-message") is not None:
            try:
                message = (
                    s.find(class_="notice-message")
                    .find("div")
                    .find(class_="link-override")
                    .text.strip()
                )
            except AttributeError:
                print("You didn't provide cookies to log in")
                break
            raise Exception("System Message", message)

        # End of gallery
        if s.find(id="no-images") is not None:
            print("End of gallery")
            break

        # Download all images on the page
        for img in s.findAll("figure"):
            download(img.find("a").attrs.get("href"))
            sleep(args.interval)

        if args.submissions is True:
            next_button = s.find("a", class_="button standard more", text="Next 48")
            if next_button is None or next_button.parent is None:
                next_button = s.find(
                    "a", class_="button standard more-half", text="Next 48"
                )
                if next_button is None or next_button.parent is None:
                    print("Unable to find next button")
                    break

            next_page_link = next_button.attrs["href"]
            page_num = next_page_link.split("/")[-2]
            page_url = BASE_URL + next_page_link

            print("Downloading page", page_num, page_url)
        elif args.category != "favorites":
            next_button = s.find("button", class_="button standard", text="Next")
            if next_button is None or next_button.parent is None:
                print("Unable to find next button")
                break

            page_num = next_button.parent.attrs["action"].split("/")[-2]

            print("Downloading page", page_num, page_url)
        else:
            next_button = s.find("a", class_="button mobile-button right", text="Next")
            if next_button is None:
                print("Unable to find next button")
                break

            # unlike galleries that are sequentially numbered, favorites use a different scheme.
            # the "page_num" is instead: [set of numbers]/next (the trailing /next is required)

            next_page_link = next_button.attrs["href"]
            next_fav_num = re.search(r"\d+", next_page_link)

            if next_fav_num is None:
                print("Failed to parse next favorite link.")
                break

            page_num = next_fav_num.group(0) + "/next"

            # parse it into numbers/next

            print("Downloading page", page_num, page_url)

    print("Finished downloading")


if __name__ == "__main__":
    main()
