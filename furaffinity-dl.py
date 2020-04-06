#!/usr/bin/python3
import argparse
from argparse import RawTextHelpFormatter
import json
from bs4 import BeautifulSoup
import requests
import urllib.request
import http.cookiejar as cookielib
import urllib.parse
import re
import os

'''
Please refer to LICENSE for licensing conditions.

current ideas / things to do:
 -r replenish, keep downloading until it finds a already downloaded file
 -n number of posts to download
 file renaming to title
 metadata injection (gets messy easily)
 sqlite database
 support for beta theme
 using `requests` instead of `urllib`
 turn this into a module
'''

# Argument parsing
parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description='Downloads the entire gallery/scraps/favorites of a furaffinity user', epilog='''
Examples:
 python3 fadl.py gallery koul
 python3 fadl.py -o koulsArt gallery koul
 python3 fadl.py -o mylasFavs favorites mylafox\n
You can also log in to FurAffinity in a web browser and load cookies to download restricted content:
 python3 fadl.py -c cookies.txt gallery letodoesart\n
DISCLAIMER: It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them.
''')
parser.add_argument('category', metavar='category', type=str, nargs='?', default='gallery',
                    help='the category to download, gallery/scraps/favorites')
parser.add_argument('username', metavar='username', type=str, nargs='?',
                    help='username of the furaffinity user')
parser.add_argument('-o', metavar='output', dest='output', type=str, default='.', help="output directory")
parser.add_argument('-c', metavar='cookies', dest='cookies', type=str, default='', help="path to a NetScape cookies file")
parser.add_argument('-s', metavar='start', dest='start', type=int, default=1, help="page number to start from")

args = parser.parse_args()
if args.username == None:
    parser.print_help()
    exit()

# Create output directory if it doesn't exist
if args.output != '.':
    os.makedirs(args.output, exist_ok=True)

# Check validity of category
valid_categories = ['gallery', 'favorites', 'scraps']
if not args.category in valid_categories:
    raise Exception('Category is not valid', args.category)

# Check validity of username
if bool(re.compile(r'[^a-zA-Z0-9\-~._]').search(args.username)):
    raise Exception('Username contains non-valid characters', args.username)
    
# Initialise a session
session = requests.Session()
session.headers.update({'User-Agent': 'furaffinity-dl redevelopment'})

# Load cookies from a netscape cookie file (if provided)
if args.cookies != '':
    cookies = cookielib.MozillaCookieJar(args.cookies)
    cookies.load()
    session.cookies = cookies

base_url = 'https://www.furaffinity.net'
gallery_url = '{}/gallery/{}'.format(base_url, args.username)
page_num = args.start

# The cursed function that handles downloading
def download_file(path):
    page_url = '{}{}'.format(base_url, path)
    response = session.get(page_url)
    s = BeautifulSoup(response.text, 'html.parser')

    image = s.find(class_='download').find('a').attrs.get('href')
    title = s.find(class_='submission-title').find('p').contents[0];
    filename = image.split("/")[-1:][0]
    data = {
        'id': int(path.split('/')[-2:-1][0]),
        'filename': filename,
        'author': s.find(class_='submission-id-sub-container').find('a').find('strong').text,
        'date': s.find(class_='popup_date').attrs.get('title'),
        'title': title,
        'description': s.find(class_='submission-description').text.strip().replace('\r\n', '\n'),
        "tags": [],
        'views': int(s.find(class_='views').find(class_='font-large').text),
        'favorites': int(s.find(class_='favorites').find(class_='font-large').text),
        'rating': s.find(class_='rating-box').text.strip(),
        'comments': []
    }

    # Extact tags
    for tag in s.find(class_='tags-row').findAll(class_='tags'):
        data['tags'].append(tag.find('a').text)

    # Extract comments
    for comment in s.findAll(class_='comment_container'):
        temp_ele = comment.find(class_='comment-parent')
        parent_cid = None if temp_ele == None else int(temp_ele.attrs.get('href')[5:])

        # Comment deleted or hidden
        if comment.find(class_='comment-link') == None:
            continue

        data['comments'].append({
            'cid': int(comment.find(class_='comment-link').attrs.get('href')[5:]),
            'parent_cid': parent_cid,
            'content': comment.find(class_='comment_text').contents[0].strip(),
            'username': comment.find(class_='comment_username').text,
            'date': comment.find(class_='popup_date').attrs.get('title')
        })

    # Write a UTF-8 encoded JSON file for metadata
    with open(os.path.join(args.output, '{}.json'.format(filename)), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print('Downloading "{}"... '.format(title))

    # Because for some god forsaken reason FA keeps the original filename in the upload, in the case that it contains non-ASCII
    # characters it can make this thing blow up. So we have to do some annoying IRI stuff to make it work. Maybe consider `requests`
    # instead of urllib
    def strip_non_ascii(s): return ''.join(i for i in s if ord(i) < 128)
    url = 'https:{}'.format(image)
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    urllib.request.urlretrieve(url, os.path.join(args.output, strip_non_ascii(filename)))

# Main downloading loop
while True:
    page_url = '{}/{}'.format(gallery_url, page_num)
    response = session.get(page_url)
    s = BeautifulSoup(response.text, 'html.parser')

    # Account status
    if page_num == 1:
        if s.find(class_='loggedin_user_avatar') != None:
            account_username = s.find(class_='loggedin_user_avatar').attrs.get('alt')
            print('Logged in as', account_username)
        else:
            print('Not logged in, some users gallery\'s may be unaccessible and NSFW content is not downloadable')

    # System messages
    if s.find(class_='notice-message') != None:
        message = s.find(class_='notice-message').find('div')
        for ele in message:
            if ele.name != None:
                ele.decompose()
        
        raise Exception('System Message', message.text.strip())

    # End of gallery
    if s.find(id='no-images') != None:
        print('End of gallery')
        break

    # Download all images on the page
    for img in s.findAll('figure'):
        download_file(img.find('a').attrs.get('href'))

    page_num += 1
    print('Downloading page', page_num)

print('Finished downloading')