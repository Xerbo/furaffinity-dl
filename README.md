This branch is the development version of furaffinity-dl rewritten in python.

# FurAffinity Downloader
**furaffinity-dl** was a bash script (now in python) for batch downloading of galleries (and scraps/favourites) from furaffinity users.
It was written for preservation of culture, to counter the people nuking their galleries every once a while.

Supports all known submission types: images, texts and audio.

## Requirements
Exact requirements are unknown since its still in development, but you should only need `beautifulsoup4` to be installed (`pip3 install beautifulsoup4`). I will put a `requirements.txt` file in the repo soon.

**The script currently only works with the "Modern" theme**

furaffinity-dl has only been tested only on Linux, however it should also work on Mac, Windows and any other platform that supports python.

## Usage
Run it with
 `./furaffinity-dl.py category username`
or:
 `python3 furaffinity-dl.py category username`

All files from the given section and user will be downloaded to the current directory.

### Examples
 `python3 furaffinity-dl.py gallery koul`

 `python3 furaffinity-dl.py -o koulsArt gallery koul`

 `python3 furaffinity-dl.py -o mylasFavs favorites mylafox`

For a full list of command line arguments use `./furaffinity-dl -h`.

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, export cookies to a file from your web browser in Netscape format (there are extensions to do that [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome base browsers](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg)), you can then pass them to the script with the `-c` flag, like this:

 `python3 furaffinity-dl.py -c cookies.txt gallery letodoesart`

## TODO

 - Download user profile information.
 - "Classic" theme support
 - Login without having to export cookies

## Disclaimer
It is your own responsibility to check whether batch downloading is allowed by FurAffinity's terms of service and to abide by them. For further disclaimers see LICENSE.
