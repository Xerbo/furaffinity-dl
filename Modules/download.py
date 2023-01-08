import json
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm

import Modules.config as config
from Modules.functions import DownloadComplete
from Modules.functions import requests_retry_session
from Modules.functions import system_message_handler


def download(path, max_retries=5):
    if max_retries < 0:
        return False
    try:
        response = requests_retry_session().get(f"{config.BASE_URL}{path}")

        s = BeautifulSoup(response.text, "html.parser")
        
        # System messages
        if s.find(class_="notice-message") is not None:
            system_message_handler(s)
        image = s.find(class_="download").find("a").attrs.get("href")
    except AttributeError:
        print(
            f"{config.ERROR_COLOR}unsuccessful download of {config.BASE_URL}{path} remains retries {max_retries}{config.END}"
        )
        return download(path, max_retries - 1)
    except Exception as e:
        print(f"{config.ERROR_COLOR}exception when download {config.BASE_URL}{path} remains retries {max_retries}, error {e}{config.END}")
        return download(path, max_retries - 1)

    filename = sanitize_filename(image.split("/")[-1:][0])

    author = (
        s.find(class_="submission-id-sub-container")
        .find("a")
        .find("strong")
        .text.replace(".", "._")
    )

    title = sanitize_filename(
        str(s.find(class_="submission-title").find("p").contents[0])
    )
    view_id = int(path.split("/")[-2:-1][0])

    output = f"{config.output_folder}/{author}"
    rating = s.find(class_="rating-box").text.strip()

    if config.real_category:
        real_category = get_image_cateory(s)
        output = f"{config.output_folder}/{author}/{real_category}"
    else: 
        if config.category != "gallery":
            output = f"{config.output_folder}/{author}/{config.category}"
        if config.folder is not None:
            output = f"{config.output_folder}/{author}/{config.folder}"
    os.makedirs(output, exist_ok=True)

    output_path = f"{output}/{title} ({view_id}) - {filename}"
    output_path_fb = f"{output}/{title} - {filename}"
    if config.rating is True:
        os.makedirs(f"{output}/{rating}", exist_ok=True)
        output_path = f"{output}/{rating}/{title} ({view_id}) - {filename}"
        output_path_fb = f"{output}/{rating}/{title} - {filename}"

    image_url = f"https:{image}"

    if config.check_file_size and (
        os.path.isfile(output_path_fb) or os.path.isfile(output_path)
    ):
        content_length = get_content_length(image_url)
        delete_file_if_mismatch_size(output_path_fb, content_length)
        delete_file_if_mismatch_size(output_path, content_length)


    if config.dont_redownload is True and (
        os.path.isfile(output_path_fb) or os.path.isfile(output_path)
    ):
        return file_exists_fallback(author, title, view_id)

    if (
        download_file(
            image_url, f"{config.BASE_URL}{path}", output_path, f"{title} - [{rating}]"
        )
        is True
    ):
        with open(
            f"{config.output_folder}/index.idx", encoding="utf-8", mode="a+"
        ) as idx:
            idx.write(f"({view_id})\n")
    else:
        return download(path, max_retries - 1)

    if config.metadata is True:
        if config.html_description is True:
            dsc = s.find(class_="submission-description").prettify()
        else:
            dsc = s.find(class_="submission-description").text.strip().replace("\r\n", "\n")
        if config.json_description is True:
            dsc = []
        data = {
            "id": view_id,
            "filename": filename,
            "author": author,
            "date": s.find(class_="popup_date").attrs.get("title"),
            "title": title,
            "description": dsc,
            "url": f"{config.BASE_URL}{path}",
            "tags": [],
            "category": s.find(class_="info").find(class_="category-name").text,
            "type": s.find(class_="info").find(class_="type-name").text,
            "species": s.find(class_="info").findAll("div")[2].find("span").text,
            "gender": s.find(class_="info").findAll("div")[3].find("span").text,
            "views": int(s.find(class_="views").find(class_="font-large").text),
            "favorites": int(s.find(class_="favorites").find(class_="font-large").text),
            "rating": rating,
            "comments": [],
        }
        create_metadata(output, data, s, title, filename)
    if config.download is not None:
        print(
            f'{config.SUCCESS_COLOR}File saved as \
"{output_path}" {config.END}'
        )

    return True


def download_file(url, view_url, file_name, desc):
    try:
        r = requests_retry_session().get(url, stream=True)
        if r.status_code != 200:
            print(
                f'{config.ERROR_COLOR}Got a HTTP {r.status_code} while downloading \
"{file_name}" ({view_url}) ...skipping{config.END}'
            )
            return False
        total = int(r.headers.get("Content-Length", 0))
        encoding = r.headers.get('Content-Encoding', '')
        with open(file_name, "wb") as file, tqdm(
            desc=desc.ljust(40),
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
        print(f"{config.SUCCESS_COLOR}Finished downloading{config.END}")
        os.remove(file_name)
        exit()
    except Exception as e:
        os.remove(file_name)
        print(f"{config.ERROR_COLOR}Download {file_name} ({view_url}) failed, error {e}. Remove file...{config.END}")
        return False

    # if webserver doesn't compress file, we should check file size
    if len(encoding) == 0 and delete_file_if_mismatch_size(file_name, total):
        return False
    return True

def get_content_length(url):
    try:
        with requests_retry_session().get(url, stream=True) as r:
            if r.status_code != 200:
                print(
                    f'{config.ERROR_COLOR}Got a HTTP {r.status_code} while get content length \
    "{url}" ...return 0{config.END}'
                )
                return 0
            content_length = r.headers.get("Content-Length", 0)
            return int(content_length)
    except Exception:
        pass
    return 0

def delete_file_if_mismatch_size(path, target_size):
    if type(target_size) != int:
        target_size = int(target_size)
    if target_size <= 0 or not os.path.isfile(path):
        return False
    file_size = os.path.getsize(path)
    if file_size != target_size:
        print(f"{config.ERROR_COLOR}File size {file_size}b mismatch {target_size}b: delete file {path}{config.END}")
        os.remove(path)
        return True
    return False

def create_metadata(output, data, s, title, filename):
    if config.rating is True:
        os.makedirs(f'{output}/{data.get("rating")}/metadata', exist_ok=True)
        metadata = f'{output}/{data.get("rating")}/metadata/{title} - {filename}'
    else:
        os.makedirs(f"{output}/metadata", exist_ok=True)
        metadata = f"{output}/metadata/{title} - {filename}"

    # Extract description as list
    if config.json_description is True:
        for desc in s.find("div", class_="submission-description").stripped_strings:
            data["description"].append(desc)

    # Extract tags

    try:
        for tag in s.find(class_="tags-row").findAll(class_="tags"):
            data["tags"].append(tag.find("a").text)
    except AttributeError:
        print(f'{config.WARN_COLOR}"{title}" has no tags{config.END}')

    # Extract comments
    for comment in s.findAll(class_="comment_container"):
        temp_ele = comment.find(class_="comment-parent")
        parent_cid = None if temp_ele is None else int(temp_ele.attrs.get("href")[5:])
        # Comment is deleted or hidden
        if comment.find(class_="comment-link") is None:
            continue

        data["comments"].append(
            {
                "cid": int(comment.find(class_="comment-link").attrs.get("href")[5:]),
                "parent_cid": parent_cid,
                "content": comment.find(class_="comment_text").contents[0].strip(),
                "username": comment.find(class_="comment_username").text,
                "date": comment.find(class_="popup_date").attrs.get("title"),
            }
        )

    # Write a UTF-8 encoded JSON file for metadata
    with open(f"{metadata}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def file_exists_fallback(author, title, view_id):
    # do not write to index when check file size is enabled
    if not config.check_file_size:
        with open(f"{config.output_folder}/index.idx", encoding="utf-8", mode="a+") as idx:
            idx.write(f"({view_id})\n")
    if config.check is True:
        print(
            f'fallback: {config.SUCCESS_COLOR}Downloaded all recent files of \
"{author}"{config.END}'
        )
        raise DownloadComplete
    print(
        f'fallback: {config.WARN_COLOR}Skipping "{title}" since \
it\'s already downloaded{config.END}'
    )
    return True

def get_image_cateory(s):
    if s.find(class_ = 'button standard mobile-fix', string = 'Main Gallery') is not None:
        return 'gallery'
    elif s.find(class_='button standard mobile-fix', string = 'Scraps') is not None:
        return 'scraps'
    return 'unknown'