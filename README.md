# FurAffinity Downloader - Next Gen
**furaffinity-dl-ng** is a bash script for batch downloading of galleries and favorites from furaffinity.net users.
It was written for preservation of culture, to counter the people nuking their galleries every once a while.

Supports all known submission types: images, texts and audio.

## Requirements
Coreutils, bash and wget are the only dependencies. However if you want to embed metadata into files you will need eyed3 and exiftool

furaffinity-dl-ng was tested only on Linux. It should also work on Mac and BSDs.
Windows users can get it to work via Microsoft's [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Cygwin is not supported.

## Usage
Make it executable with
 `chmod +x faraffinity-dl-ng`
And run it with
 `./faraffinity-dl-ng section/username`

All files from the given section and user will be downloaded to the current directory.

### Examples
 `./faraffinity-dl-ng gallery/mylafox`

 `./faraffinity-dl-ng -o=myla gallery/mylafox`

 `./faraffinity-dl-ng --out=koul favorites/koul`

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, export cookies to a file from your web browser in Netscape format (there are extensions to do that [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome/Vivaldi](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg)) and pass them to the script as a second parameter, like this:

 `furaffinity-dl gallery/gonnaneedabiggerboat /path/to/your/cookies.txt`

## TODO
 * Download user bio, post tags and ideally user comments

## Disclaimer
It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them. For further disclaimers see LICENSE.
