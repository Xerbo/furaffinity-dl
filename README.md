# FurAffinity Downloader

**furaffinity-dl** is a python script for batch downloading of galleries (and scraps/favorites) from furaffinity users users or your submission notifications!
Mainly it was written for preservation of culture, to counter the people nuking their galleries every once a while.
But no-one is restricting you from just using is for convenience.

Supports all known submission types: images, text, flash and audio.

## Requirements

`python3` (Recommended version is 3.10.x and above)

`pip3 install -r requirements.txt`

furaffinity-dl has been tested on Linux and Windows OSs, however it should also work on Mac or any other platform that supports python.

***The script currently only works with the "Modern" theme***

## Usage

When downloading a folder make sure to put everything after **/folder/**, for example 123456/Folder-Name-Here instead of just 123456 (ref [#60](https://github.com/Xerbo/furaffinity-dl/issues/60)).

```help

usage: furaffinity-dl.py [-h] [--cookies COOKIES] [--output OUTPUT_FOLDER] [--check] [--user-agent USER_AGENT] [--submissions] [--folder FOLDER] [--start START]
                         [--stop STOP] [--redownload] [--interval INTERVAL] [--rating] [--filter] [--metadata] [--download DOWNLOAD] [--json-description] [--login]
                         [--index]
                         [username] [category]

Downloads the entire gallery/scraps/folder/favorites of a furaffinity user, or your submissions notifications

positional arguments:
  username              username of the furaffinity user (if username is starting with '-' or '--' provide them through a file instead)
  category              the category to download, gallery/scraps/favorites [default: gallery]

options:
  -h, --help            show this help message and exit
  --cookies COOKIES, -c COOKIES
                        path to a NetScape cookies file
  --output OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        set a custom output folder
  --check               check and download latest submissions of a user
  --user-agent USER_AGENT, -ua USER_AGENT
                        Your browser's user agent, may be required, depending on your luck
  --submissions, -sub   download your submissions
  --folder FOLDER, -f FOLDER
                        full path of the furaffinity gallery folder. for instance 123456/Folder-Name-Here
  --start START         page number to start from
  --stop STOP           Page number to stop on. Specify the full URL after the username: for favorites pages (1234567890/next) or for submissions pages: (new~123456789@48)
  --redownload, -rd     Redownload files that have been downloaded already
  --interval INTERVAL, -i INTERVAL
                        delay between downloading pages in seconds [default: 0]
  --rating, -r          disable rating separation
  --filter              enable submission filter
  --metadata, -m        enable metadata saving
  --download DOWNLOAD   download a specific submission by providing its id
  --html-description, -hd
                        download description as original html format, this won't work if json-description is enabled
  --json-description, -jd
                        download description as a JSON list
  --login               extract furaffinity cookies directly from your browser
  --index               create an index of downloaded files in an output folder

Examples:
 python3 furaffinity-dl.py koul -> will download gallery of user koul
 python3 furaffinity-dl.py koul scraps -> will download scraps of user koul
 python3 furaffinity-dl.py mylafox favorites -> will download favorites of user mylafox 

You can also download a several users in one go like this:
 python3 furaffinity-dl.py "koul radiquum mylafox" -> will download gallery of users koul -> radiquum -> mylafox
You can also provide a file with user names that are separated by a new line

You can also log in to FurAffinity in a web browser and load cookies to download age restricted content or submissions:
 python3 furaffinity-dl.py letodoesart -c cookies.txt -> will download gallery of user letodoesart including Mature and Adult submissions
 python3 furaffinity-dl.py --submissions -c cookies.txt -> will download your submissions notifications 

DISCLAIMER: It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them.

```

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, and use `python3 furaffinity-dl.py --login` to export furaffinity cookies from your web browser in Netscape format directly in to the file `cookies.txt` or export them manually with extensions: [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome based browsers](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en), then you can then pass them to the script with the `-c` flag, like this (you may also have to provide your user agent):

`python3 furaffinity-dl.py letodoesart -c cookies.txt --user-agent 'Mozilla/5.0 ....'`

<!-- ## TODO

- Download user profile information.
- "Classic" theme support
- Login without having to export cookies -->

## Disclaimer

It is your own responsibility to check whether batch downloading is allowed by FurAffinity's terms of service and to abide by them. For further disclaimers see LICENSE.
