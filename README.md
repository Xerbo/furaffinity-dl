This branch is the development version of furaffinity-dl rewritten in python.

# FurAffinity Downloader
**furaffinity-dl** is a python script for batch downloading of galleries (and scraps/favourites) from furaffinity.net users.
It was written for preservation of culture, to counter the people nuking their galleries every once a while.

Supports all known submission types: images, texts and audio.

## Requirements
The exacts are unknown due to the fact that this is still early in development, you should only need beautifulsoup4 to be installed though. I will put a `requirements.txt` in the repo soon

furaffinity-dl was tested only on Linux. It should also work on Mac, Windows and any other platform that supports python.

## Usage
Run it with
 `./furaffinity-dl.py category username`
or:
 `python3 furaffinity-dl.py category username`

All files from the given section and user will be downloaded to the current directory.

### Examples
 `python3 fadl.py gallery koul`

 `python3 fadl.py -o koulsArt gallery koul`

 `python3 fadl.py -o mylasFavs favorites mylafox`

For a full list of command line arguments use `./furaffinity-dl -h`.

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, export cookies to a file from your web browser in Netscape format (there are extensions to do that [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome/Vivaldi](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg)) and pass them to the script as a second parameter, like this:

 `python3 fadl.py -c cookies.txt gallery letodoesartt`

## TODO
 * Download user information.

## Disclaimer
It is your own responsibility to check whether batch downloading is allowed by FurAffinity's terms of service and to abide by them. For further disclaimers see LICENSE.
