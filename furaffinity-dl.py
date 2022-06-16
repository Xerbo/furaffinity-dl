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

# COLORS
WHITE = "\033[1;37m"
RED = "\033[1;91m"
GREEN = "\033[1;92m"
YELLOW = "\033[1;33m"
END = "\033[0m"

# Argument parsing
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="Downloads the entire gallery/scraps/folder/favorites of a furaffinity user, or your submissions notifications",
    epilog="""
Examples:
 python3 furaffinity-dl.py koul -> will download gallery of user koul
 python3 furaffinity-dl.py koul scraps -> will download scraps of user koul
 python3 furaffinity-dl.py mylafox favorites -> will download favorites of user mylafox \n
You can also log in to FurAffinity in a web browser and load cookies to download age restricted content or submissions:
 python3 furaffinity-dl.py letodoesart -c cookies.txt -> will download gallery of user letodoesart including Mature and Adult submissions
 python3 furaffinity-dl.py --submissions -c cookies.txt -> will download your submissions notifications \n
DISCLAIMER: It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them.
""",
)
parser.add_argument("username", nargs="?", help="username of the furaffinity user")
parser.add_argument(
    "category",
    nargs="?",
    help="the category to download, gallery/scraps/favorites [default: gallery]",
    default="gallery",
)
parser.add_argument(
    "--submissions", action="store_true", help="download your submissions"
)
parser.add_argument(
    "--folder",
    nargs="+",
    help="full path of the furaffinity gallery folder. for instance 123456/Folder-Name-Here",
)
parser.add_argument(
    "--cookies", "-c", nargs="+", help="path to a NetScape cookies file"
)
parser.add_argument(
    "--user-agent",
    dest="user_agent",
    nargs="+",
    default="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    help="Your browser's useragent, may be required, depending on your luck",
)
parser.add_argument(
    "--start", "-s", default=[1], help="page number to start from", nargs="+"
)
parser.add_argument(
    "--stop",
    "-S",
    default=[0],
    nargs="+",
    help="Page number to stop on. Specify the full URL after the username: for favorites pages (1234567890/next) or for submissions pages: (new~123456789@48)",
)
parser.add_argument(
    "--dont-redownload",
    "-d",
    action="store_false",
    help="Allow to redownload files that have been downloaded already",
)
parser.add_argument(
    "--interval",
    "-i",
    type=int,
    default=[0],
    nargs="+",
    help="delay between downloading pages in seconds [default: 0]",
)
parser.add_argument(
    "--rating",
    "-r",
    action="store_false",
    help="disable rating separation",
)
parser.add_argument(
    "--filter",
    action="store_false",
    help="disable submission filter",
)
parser.add_argument(
    "--metadata",
    "-m",
    action="store_true",
    help="enable downloading of metadata",
)
parser.add_argument(
    "--download",
    help="download a specific submission /view/12345678/",
)
parser.add_argument(
    "--json-description",
    dest="json_description",
    action="store_true",
    help="download description as a JSON list",
)

args = parser.parse_args()

BASE_URL = "https://www.furaffinity.net"
username = args.username

if args.submissions is False and args.download is None:  # check if you are not downloading submissions or a specific post
    categories = {
        "gallery": "gallery",
        "scraps": "scraps",
        "favorites": "favorites",
    }
    category = categories.get(args.category)
    if args.username is None:
        print(f"{RED}<!> please enter a FA Username{END}")
        exit()
    if category is None:
        print(f"{RED}<!> please enter a valid category gallery/scraps/favorites{END}")
        exit()

    download_url = f"{BASE_URL}/{category}/{username}"
    output = f"furaffinity-dl/{category}/{username}"

# get session
session = requests.session()
session.headers.update({"User-Agent": args.user_agent[0]})

if args.cookies is not None:  # add cookies if present
    cookies = cookielib.MozillaCookieJar(args.cookies[0])
    cookies.load()
    session.cookies = cookies

# File downloading
def download_file(url, fname, desc):
    try:
        r = session.get(url, stream=True)
        if r.status_code != 200:
            print(
                f"{RED}<!> Got a HTTP {r.status_code} while downloading {fname}; ...skipping{END}"
            )
            return False

        total = int(r.headers.get("Content-Length", 0))
        with open(fname, "wb") as file, tqdm(
            desc=desc.ljust(60)[:60],
            total=total,
            miniters=100,
            unit="b",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in r.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
    except KeyboardInterrupt:
        print(f"{GREEN}<i> Finished downloading{END}")
        os.remove(fname)
        exit()

    return True


# checks if you are downloading forder or submission
if args.folder is not None:
    folder = args.folder[0].split("/")
    download_url = f"{BASE_URL}/gallery/{username}/folder/{args.folder[0]}"
    output = f"furaffinity-dl/folders/{username}/{folder[1]}"
if args.submissions is True:    
    download_url = f"{BASE_URL}/msg/submissions"

def download(path):
    response = session.get(f"{BASE_URL}{path}")
    s = BeautifulSoup(response.text, "html.parser")
    
    # System messages
    if s.find(class_="notice-message") is not None:
        try:
            message = (
                s.find(class_="notice-message")
                .find("div")
                .find(class_="link-override")
                .text.strip()
                .replace(".", ". \n")
            )
        except AttributeError:
            message = (
                s.find(class_="notice-message")
                .find("div", class_="section-body alignleft")
                .find("div", class_="redirect-message")
                .text.strip()
                .replace(".", ". \n")
            )
        print(f"{YELLOW}<i> System Message: {message}{END}")
        exit()

    image = s.find(class_="download").find("a").attrs.get("href")
    title = s.find(class_="submission-title").find("p").contents[0] + " "
    description = s.find(class_="submission-description").text.strip().replace("\r\n", "\n")
    author = s.find(class_="submission-id-sub-container")
    if args.submissions is True:   
        global output 
        output = f"furaffinity-dl/gallery/{author}"
        
    if args.json_description is True:
        description = []
    filename = image.split("/")[-1:][0]
    data = {
        "id": int(path.split("/")[-2:-1][0]),
        "filename": filename,
        "author": author
        .find("a")
        .find("strong")
        .text,
        "date": s.find(class_="popup_date").attrs.get("title"),
        "title": title,
        "description": description,
        "url": f"{BASE_URL}{path}",
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

    if args.filter is True:
        match = re.search(
            "YCH[a-z $-/:-?{-~!\"^_`\[\]]*OPEN|OPEN[a-z $-/:-?{-~!\"^_`\[\]]*YCH|YCH[a-z $-/:-?{-~!\"^_`\[\]]*CLOSE|CLOSE[a-z $-/:-?{-~!\"^_`\[\]]*YCH|YCH[a-z $-/:-?{-~!\"^_`\[\]]*ABLE|AVAIL[a-z $-/:-?{-~!\"^_`\[\]]*YCH|YCH[a-z $-/:-?{-~!\"^_`\[\]]*CLONE|CLONE[a-z $-/:-?{-~!\"^_`\[\]]*YCH|YCH[a-z $-/:-?{-~!\"^_`\[\]]*LIM|LIM[a-z $-/:-?{-~!\"^_`\[\]]*YCH|COM[a-z $-/:-?{-~!\"^_`\[\]]*OPEN|OPEN[a-z $-/:-?{-~!\"^_`\[\]]*COM|COM[a-z $-/:-?{-~!\"^_`\[\]]*CLOSE|CLOSE[a-z $-/:-?{-~!\"^_`\[\]]*COM|FIX[a-z $-/:-?{-~!\"^_`\[\]]*ICE|REM[insder]*\W|\\bREF|Sale$|auction|multislot|stream|adopt",
            title,
            re.IGNORECASE,
        )
        if match is not None and title == match.string:
            print(
                f"{YELLOW}<i> post {title} was filtered and will not be downloaded - {data.get('url')}{END}"
            )
            return True

    image_url = f"https:{image}"
    
    os.makedirs(output, exist_ok=True)
    output_path = f"{output}/{filename}"
    if args.rating is True:
        os.makedirs(f'{output}/{data.get("rating")}', exist_ok=True)
        output_path = f'{output}/{data.get("rating")}/{filename}'

    if args.dont_redownload is True and os.path.isfile(output_path):
        print(f'{YELLOW}<i> Skipping "{title}", since it\'s already downloaded{END}')
    else:
        download_file(image_url, output_path, title)

    if args.metadata is True:

        metadata = f"{output}/metadata"
        
        # Extract description as list
        if args.json_description is True:
            for desc in s.find("div", class_="submission-description").strings:
                description = desc.strip()
                data["description"].append(description)
            
        # Extact tags

        try:
            for tag in s.find(class_="tags-row").findAll(class_="tags"):
                data["tags"].append(tag.find("a").text)
        except AttributeError:
            print(f'{YELLOW}<i> post: "{title}", has no tags{END}')

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

if args.download is not None:
    output = "furaffinity-dl/downloaded/"
    download(args.download)
    print(f"{GREEN}<i> File downloaded{END}")
    exit()
        
# Main function
def main():
    # check if you are logged in
    page_end = args.stop[0]
    page_num = args.start[0]
    page_url = f"{download_url}/{page_num}"
    response = session.get(page_url)
    s = BeautifulSoup(response.text, "html.parser")
    if s.find(class_="loggedin_user_avatar") is not None:
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print(f"{GREEN}<i> Logged in as: {account_username}{END}")
    else:
        print(f"{YELLOW}<i> Not logged in, NSFW content is inaccessible{END}")

    # download loop
    while True:
        if page_end == page_num:
            print(f"{YELLOW}<i> Reached page {page_end}, stopping.{END}")
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
                    .replace(".", ". \n")
                )
            except AttributeError:
                message = (
                    s.find(class_="notice-message")
                    .find("div", class_="section-body alignleft")
                    .find("div", class_="redirect-message")
                    .text.strip()
                    .replace(".", ". \n")
                )
            print(f"{YELLOW}<i> System Message: {message}{END}")
            exit()

        # End of gallery
        if s.find(id="no-images") is not None:
            print(f"{GREEN}<i> End of gallery{END}")
            break

        # Download all images on the page
        for img in s.findAll("figure"):
            download(img.find("a").attrs.get("href"))
            sleep(args.interval[0])

        # Download submissions
        if args.submissions is True:
            try:
                next_button = s.find("a", class_="button standard more").attrs.get(
                    "href"
                )
            except AttributeError:
                try:
                    next_button = s.find(
                        "a", class_="button standard more-half"
                    ).attrs.get("href")
                except AttributeError:
                    print(f"{YELLOW}<!> Unable to find next button{END}")
                    break

            # unlike galleries that are sequentially numbered, submissions use a different scheme.
            # the "page_num" is instead: new~[set of numbers]@(12 or 48 or 72) if sorting by new

            page_num = next_button.split("/")[-2]
            page_url = f"{BASE_URL}{next_button}"

            print(f"{WHITE}<i> Downloading page {page_num} - {page_url} {END}")
        # Download everything else
        elif args.category != "favorites":
            next_button = s.find("button", class_="button standard", text="Next")
            if next_button is None or next_button.parent is None:
                print(f"{YELLOW}<!> Unable to find next button{END}")
                break

            page_num = next_button.parent.attrs["action"].split("/")[-2]

            print(f"{WHITE}<i> Downloading page {page_num} - {page_url} {END}")
        # Download favorites
        else:
            next_button = s.find("a", class_="button standard right", text="Next")
            if next_button is None:
                print(f"{YELLOW}<!> Unable to find next button{END}")
                break

            # unlike galleries that are sequentially numbered, favorites use a different scheme.
            # the "page_num" is instead: [set of numbers]/next (the trailing /next is required)

            next_page_link = next_button.attrs["href"]
            next_fav_num = re.search(r"\d+", next_page_link)

            if next_fav_num is None:
                print(f"{YELLOW}<!> Failed to parse next favorite link{END}")
                break

            page_num = next_fav_num.group(0) + "/next"

            # parse it into numbers/next

            print(f"{WHITE}<i> Downloading page {page_num} - {page_url} {END}")

    print(f"{GREEN}Finished downloading{END}")


if __name__ == "__main__":
    main()
