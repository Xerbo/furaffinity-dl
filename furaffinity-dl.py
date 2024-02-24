#!/usr/bin/python3
import argparse
from tqdm import tqdm
from argparse import RawTextHelpFormatter
import json
from bs4 import BeautifulSoup
import requests
import http.cookiejar as cookielib
import re
import os
from time import sleep

'''
Please refer to LICENSE for licensing conditions.
'''

# Argument parsing
parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description='Downloads the entire gallery/scraps/favorites of a furaffinity user', epilog='''
Examples:
 python3 furaffinity-dl.py gallery koul
 python3 furaffinity-dl.py -o koulsArt gallery koul
 python3 furaffinity-dl.py -o mylasFavs favorites mylafox\n
You can also log in to FurAffinity in a web browser and load cookies to download restricted content:
 python3 furaffinity-dl.py -c cookies.txt gallery letodoesart\n
DISCLAIMER: It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them.
''')
parser.add_argument('category', metavar='category', type=str, nargs='?', default='gallery', help='the category to download, gallery/scraps/favorites')
parser.add_argument('username', metavar='username', type=str, nargs='?', help='username of the furaffinity user')
parser.add_argument('folder', metavar='folder', type=str, nargs='?', help='name of the folder (full path, for instance 123456/Folder-Name-Here)')
parser.add_argument('--output', '-o', dest='output', type=str, default='.', help="output directory")
parser.add_argument('--cookies', '-c', dest='cookies', type=str, default='', help="path to a NetScape cookies file")
parser.add_argument('--ua', '-u', dest='ua', type=str, default='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.7) Gecko/20100101 Firefox/68.7', help="Your browser's useragent, may be required, depending on your luck")
parser.add_argument('--start', '-s', dest='start', type=str, default=1, help="page number to start from")
parser.add_argument('--stop', '-S', dest='stop', type=str, default='', help="Page number to stop on. For favorites pages, specify the full URL after the username (1234567890/next).")
parser.add_argument('--dont-redownload', '-d', const='dont_redownload', action='store_const', help="Don't redownload files that have already been downloaded")
parser.add_argument('--interval', '-i', dest='interval', type=float, default=0, help="delay between downloading pages")
parser.add_argument('--metadir', '-m', dest='metadir', type=str, default=None, help="directory to put meta files in")

args = parser.parse_args()
if args.username is None:
    parser.print_help()
    exit()

# Create output directory if it doesn't exist
if args.output != '.':
    os.makedirs(args.output, exist_ok=True)
    
if args.metadir == None:
    args.metadir = args.output
else:
    os.makedirs(args.metadir, exist_ok=True)


# Check validity of category
valid_categories = ['gallery', 'favorites', 'scraps']
if args.category not in valid_categories:
    raise Exception('Category is not valid', args.category)

# Check validity of username
if bool(re.compile(r'[^a-zA-Z0-9\-~._]').search(args.username)):
    raise Exception('Username contains non-valid characters', args.username)

# Initialise a session
session = requests.session()
session.headers.update({'User-Agent': args.ua})

# Load cookies from a netscape cookie file (if provided)
if args.cookies != '':
    cookies = cookielib.MozillaCookieJar(args.cookies)
    cookies.load()
    session.cookies = cookies

base_url = 'https://www.furaffinity.net'
gallery_url = '{}/{}/{}'.format(base_url, args.category, args.username)
if args.folder is not None:
    gallery_url += "/folder/"
    gallery_url += args.folder
page_num = args.start


def download_file(url, fname, desc):
    r = session.get(url, stream=True)
    if r.status_code != 200:
        print("Got a HTTP {} while downloading {}; skipping".format(r.status_code, fname))
        return False

    total = int(r.headers.get('Content-Length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=desc.ljust(40)[:40],
        total=total,
        miniters=100,
        unit='b',
        unit_scale=True,
        unit_divisor=1024
    ) as bar:
        for data in r.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    return True


# The cursed function that handles downloading
def download(path):
    page_url = '{}{}'.format(base_url, path)
    response = session.get(page_url)
    s = BeautifulSoup(response.text, 'html.parser')

    # System messages
    if s.find(class_='notice-message') is not None:
        message = s.find(class_='notice-message').find('div').find(class_="link-override").text.strip()
        raise Exception('System Message', message)

    image = s.find(class_='download').find('a').attrs.get('href')
    title = s.find(class_='submission-title').find('p').contents[0]
    filename = image.split("/")[-1:][0]
    data = {
        'id': int(path.split('/')[-2:-1][0]),
        'filename': filename,
        'author': s.find(class_='submission-id-sub-container').find('a').find('strong').text,
        'date': s.find(class_='popup_date').attrs.get('title'),
        'title': title,
        'description': s.find(class_='submission-description').text.strip().replace('\r\n', '\n'),
        "tags": [],
        'category': s.find(class_='info').find(class_='category-name').text,
        'type': s.find(class_='info').find(class_='type-name').text,
        'species': s.find(class_='info').findAll('div')[2].find('span').text,
        'gender': s.find(class_='info').findAll('div')[3].find('span').text,
        'views': int(s.find(class_='views').find(class_='font-large').text),
        'favorites': int(s.find(class_='favorites').find(class_='font-large').text),
        'rating': s.find(class_='rating-box').text.strip(),
        'comments': []
    }

    # Extact tags
    try:
        for tag in s.find(class_='tags-row').findAll(class_='tags'):
            data['tags'].append(tag.find('a').text)
    except:
        pass

    # Extract comments
    for comment in s.findAll(class_='comment_container'):
        temp_ele = comment.find(class_='comment-parent')
        parent_cid = None if temp_ele is None else int(temp_ele.attrs.get('href')[5:])

        # Comment is deleted or hidden
        if comment.find(class_='comment-link') is None:
            continue

        data['comments'].append({
            'cid': int(comment.find(class_='comment-link').attrs.get('href')[5:]),
            'parent_cid': parent_cid,
            'content': comment.find(class_='user-submitted-links').text.strip().replace('\r\n', '\n'),
            'username': comment.find(class_='comment_username').text,
            'date': comment.find(class_='popup_date').attrs.get('title')
        })

    url = 'https:{}'.format(image)
    output_path = os.path.join(args.output, filename)

    if not args.dont_redownload or not os.path.isfile(output_path):
        if not download_file(url, output_path, data["title"]):
            return False
    else:
        print('Skipping "{}", since it\'s already downloaded'.format(data["title"]))
        return True

    # Write a UTF-8 encoded JSON file for metadata
    with open(os.path.join(args.metadir, '{}.json'.format(filename)), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return True


# Main downloading loop
while True:
    if args.stop and args.stop == page_num:
        print(f"Reached page {args.stop}, stopping.")
        break

    page_url = '{}/{}'.format(gallery_url, page_num)
    response = session.get(page_url)
    s = BeautifulSoup(response.text, 'html.parser')

    # Account status
    if page_num == 1:
        if s.find(class_='loggedin_user_avatar') is not None:
            account_username = s.find(class_='loggedin_user_avatar').attrs.get('alt')
            print('Logged in as', account_username)
        else:
            print('Not logged in, NSFW content is inaccessible')

    # System messages
    if s.find(class_='notice-message') is not None:
        message = s.find(class_='notice-message').find('div').find(class_="link-override").text.strip()
        raise Exception('System Message', message)

    # End of gallery
    if s.find(id='no-images') is not None:
        print('End of gallery')
        break

    # Download all images on the page
    for img in s.findAll('figure'):
        download(img.find('a').attrs.get('href'))
        sleep(args.interval)

    if args.category != "favorites":
        next_button = s.find('button', class_='button standard', string="Next")
        if next_button is None or next_button.parent is None:
            print('Unable to find next button')
            break

        page_num = next_button.parent.attrs['action'].split('/')[-2]

        print('Downloading page', page_num, page_url)
    else:
        next_button = s.find('a', class_='button mobile-button right', string="Next")
        if next_button is None:
            print('Unable to find next button')
            break

        # unlike galleries that are sequentially numbered, favorites use a different scheme.
        # the "page_num" is instead: [set of numbers]/next (the trailing /next is required)
        
        next_page_link = next_button.attrs['href']
        next_fav_num = re.search(r'\/\d+', next_page_link)

        if next_fav_num == None:
            print('Failed to parse next favorite link.')
            break

        page_num = next_fav_num.group(0) + "/next"

        # parse it into numbers/next


        print('Downloading page', page_num, page_url)


print('Finished downloading')
