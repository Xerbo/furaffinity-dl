Python rewrite has been released, I would appreciate it if some people would try it out. It lives on the `python` branch

# FurAffinity Downloader
**furaffinity-dl** is a bash script for batch downloading of galleries and favorites from furaffinity.net users.
It was written for preservation of culture, to counter the people nuking their galleries every once a while.

Supports all known submission types: images, texts and audio.

## Requirements
Coreutils, bash and wget are the only dependencies. However if you want to embed metadata into files you will need eyed3 and exiftool

furaffinity-dl was tested only on Linux. It should also work on Mac and BSDs.
Windows users can get it to work via Microsoft's [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Cygwin is not supported.

## Usage
Make it executable with
 `chmod +x faraffinity-dl`
And then run it with
 `./furaffinity-dl section/username`

All files from the given section and user will be downloaded to the current directory.

### Examples
 `./furaffinity-dl gallery/mylafox`

 `./furaffinity-dl -o mylasArt gallery/mylafox`

 `./furaffinity-dl -o koulsFavs favorites/koul`

For a full list of command line arguemnts use `./furaffinity-dl -h`.

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, export cookies to a file from your web browser in Netscape format (there are extensions to do that [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome/Vivaldi](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg)) and pass them to the script as a second parameter, like this:

 `./furaffinity-dl -c /path/to/your/cookies.txt gallery/gonnaneedabiggerboat`

## TODO
 * Download user bio, post tags and ideally user comments

## Disclaimer
It is your own responsibility to check whether batch downloading is allowed by FurAffinity's terms of service and to abide by them. For further disclaimers see LICENSE.
