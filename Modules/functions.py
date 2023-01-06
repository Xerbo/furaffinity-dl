import http.cookiejar as cookielib
import re

import browser_cookie3
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

import Modules.config as config


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504, 104),
    session=None,
):
    """Get a session, and retry in case of an error"""
    session = session or requests.Session()
    if config.cookies is not None:  # add cookies if present
        cookies = cookielib.MozillaCookieJar(config.cookies)
        cookies.load()
        session.cookies = cookies
    session.headers.update({"User-Agent": config.user_agent})
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class DownloadComplete(Exception):
    pass


def check_filter(title):
    """Compare post title and search string, then return 'True' if match found"""

    match = re.search(
        config.search,
        title,
        re.IGNORECASE,
    )
    if match is not None and title == match.string:
        return True

    return None


def system_message_handler(s):
    """Parse and return system message text"""
    try:
        message = {
            s.find(class_="notice-message")
            .find("div")
            .find(class_="link-override")
            .text.strip()
        }
    except AttributeError:
        try:
            message = (
                s.find("section", class_="aligncenter notice-message")
                .find("div", class_="section-body alignleft")
                .find("div", class_="redirect-message")
                .text.strip()
            )
        except AttributeError:
            message = (
                s.find("section", class_="aligncenter notice-message")
                .find("div", class_="section-body alignleft")
                .text.strip()
            )
    print(f"{config.WARN_COLOR}System Message: {message}{config.END}")
    raise DownloadComplete


def login():
    """Get cookies from any browser with logged in furaffinity and save them to file"""
    session = requests.Session()
    cj = browser_cookie3.load()

    response = session.get(config.BASE_URL, cookies=cj)
    fa_cookies = cj._cookies[".furaffinity.net"]["/"]

    cookie_a = fa_cookies["a"]
    cookie_b = fa_cookies["b"]

    s = BeautifulSoup(response.text, "html.parser")
    try:
        s.find(class_="loggedin_user_avatar")
        account_username = s.find(class_="loggedin_user_avatar").attrs.get("alt")
        print(f"{config.SUCCESS_COLOR}Logged in as: {account_username}{config.END}")
        with open("cookies.txt", "w") as file:
            file.write(
                f"""# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.
.furaffinity.net	TRUE	/	TRUE	{cookie_a.expires}	a	{cookie_a.value}
.furaffinity.net	TRUE	/	TRUE	{cookie_b.expires}	b	{cookie_b.value}"""
            )
        print(
            f'{config.SUCCESS_COLOR}cookies saved successfully, now you can provide them \
by using "-c cookies.txt"{config.END}'
        )
    except AttributeError:
        print(
            f"{config.ERROR_COLOR}Error getting cookies, either you need to login into \
furaffinity in your browser, or you can export cookies.txt manually{config.END}"
        )


def next_button(page_url):
    """Parse Next button and get next page url"""
    response = requests_retry_session().get(page_url)
    s = BeautifulSoup(response.text, "html.parser")
    if config.submissions is True:
        # unlike galleries that are sequentially numbered, submissions use a different scheme.
        # the "page_num" is instead: new~[set of numbers]@(12 or 48 or 72) if sorting by new
        try:
            parse_next_button = s.find("a", class_="button standard more").attrs.get(
                "href"
            )
        except AttributeError:
            try:
                parse_next_button = s.find(
                    "a", class_="button standard more-half"
                ).attrs.get("href")
            except AttributeError as e:
                print(f"{config.WARN_COLOR}Unable to find next button{config.END}")
                raise DownloadComplete from e
        page_num = parse_next_button.split("/")[-2]
    elif config.category != "favorites":
        parse_next_button = s.find("button", class_="button standard", text="Next")
        if parse_next_button is None or parse_next_button.parent is None:
            print(f"{config.WARN_COLOR}Unable to find next button{config.END}")
            raise DownloadComplete
        page_num = parse_next_button.parent.attrs["action"].split("/")[-2]
    else:
        parse_next_button = s.find("a", class_="button standard right", text="Next")
        page_num = fav_next_button(parse_next_button)
    next_page_url = (parse_next_button.parent.attrs['action'] if 'action'
                    in parse_next_button.parent.attrs else parse_next_button.attrs['href'])
    print(
        f"Downloading page {page_num} - {config.BASE_URL}{next_page_url}"
    )
    return page_num


def fav_next_button(parse_next_button):
    # unlike galleries that are sequentially numbered, favorites use a different scheme.
    # the "page_num" is instead: [set of numbers]/next (the trailing /next is required)
    if parse_next_button is None:
        print(f"{config.WARN_COLOR}Unable to find next button{config.END}")
        raise DownloadComplete
    next_page_link = parse_next_button.attrs["href"]
    next_fav_num = re.findall(r"\d+", next_page_link)

    if len(next_fav_num) <= 0:
        print(f"{config.WARN_COLOR}Failed to parse next favorite link{config.END}")
        raise DownloadComplete

    return f"{next_fav_num[-1]}/next"
