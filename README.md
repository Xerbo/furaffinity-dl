This branch is the development version of furaffinity-dl rewritten in python.

# FurAffinity Downloader

**furaffinity-dl** is a python script for batch downloading of galleries (and scraps/favourites) from furaffinity users users or your submissons!
It was written for preservation of culture, to counter the people nuking their galleries every once a while.
and then modified for confinience.

Supports all known submission types: images, text, flash and audio.

## Requirements

`python 3`

`pip3 install -r requirements.txt`

**The script currently only works with the "Modern" theme**

furaffinity-dl has only been tested only on Linux, however it should also work on Mac, Windows or any other platform that supports python.

## Usage

When downloading a folder make sure to put everything after **/folder/**, for example 123456/Folder-Name-Here instead of just 123456 (ref [#60](https://github.com/Xerbo/furaffinity-dl/issues/60)).

```help

usage: furaffinity-dl.py [-h] [--submissions] [--folder FOLDER [FOLDER ...]] [--cookies COOKIES [COOKIES ...]]
                         [--user-agent USER_AGENT [USER_AGENT ...]] [--start START [START ...]] [--stop STOP [STOP ...]] [--dont-redownload]
                         [--interval INTERVAL [INTERVAL ...]] [--rating] [--filter] [--metadata] [--download DOWNLOAD] [--json-description]
                         [--login]
                         [username] [category]

Downloads the entire gallery/scraps/folder/favorites of a furaffinity user, or your submissions notifications

positional arguments:
  username              username of the furaffinity user
  category              the category to download, gallery/scraps/favorites [default: gallery]

options:
  -h, --help            show this help message and exit
  --submissions         download your submissions
  --folder FOLDER [FOLDER ...]
                        full path of the furaffinity gallery folder. for instance 123456/Folder-Name-Here
  --cookies COOKIES [COOKIES ...], -c COOKIES [COOKIES ...]
                        path to a NetScape cookies file
  --user-agent USER_AGENT [USER_AGENT ...]
                        Your browser's useragent, may be required, depending on your luck
  --start START [START ...], -s START [START ...]
                        page number to start from
  --stop STOP [STOP ...], -S STOP [STOP ...]
                        Page number to stop on. Specify the full URL after the username: for favorites pages (1234567890/next) or for submissions pages: (new~123456789@48)
  --dont-redownload, -d
                        Allow to redownload files that have been downloaded already
  --interval INTERVAL [INTERVAL ...], -i INTERVAL [INTERVAL ...]
                        delay between downloading pages in seconds [default: 0]
  --rating, -r          disable rating separation
  --filter              disable submission filter
  --metadata, -m        enable downloading of metadata
  --download DOWNLOAD   download a specific submission /view/12345678/
  --json-description    download description as a JSON list
  --login               extract furaffinity cookies directly from your browser

Examples:
 python3 furaffinity-dl.py koul -> will download gallery of user koul
 python3 furaffinity-dl.py koul scraps -> will download scraps of user koul
 python3 furaffinity-dl.py mylafox favorites -> will download favorites of user mylafox

You can also log in to FurAffinity in a web browser and load cookies to download age restricted content or submissions:
 python3 furaffinity-dl.py letodoesart -c cookies.txt -> will download gallery of user letodoesart including Mature and Adult submissions
 python3 furaffinity-dl.py --submissions -c cookies.txt -> will download your submissions notifications

DISCLAIMER: It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them.

```

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, and use `python3 furaffinity-dl.py --login` to export furaffinity cookies from your web browser in Netscape format directly in file `cookies.txt` or export them manually with extensions: [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome based browsers](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en), then you can then pass them to the script with the `-c` flag, like this (you may also have to provide your user agent):

`python3 furaffinity-dl.py letodoesart -c cookies.txt --user_agent 'Mozilla/5.0 ....'`

## TODO

- Download user profile information.
- "Classic" theme support
- Login without having to export cookies

## Disclaimer

It is your own responsibility to check whether batch downloading is allowed by FurAffinity's terms of service and to abide by them. For further disclaimers see LICENSE.
