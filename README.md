# FurAffinity Downloader
**furaffinity-dl** is a bash script for batch downloading of galleries and favorites from furaffinity.net users.
I've written it for preservation of culture, to counter the people nuking their galleries every once a while.

Supports all known submission types: images, texts and audio. Sorts downloaded files in chronological order.
I'd like to eventually expand it to download the description pages as well. Patches are welcome!

## Requirements

Coreutils, bash and wget are the only dependencies.

furaffinity-dl was tested only on Linux. It should also work on Mac and BSDs.
Windows users can get it to work via Microsoft's "BASH on Windows". Cygwin is not supported.

## Usage
 `furaffinity-dl section/username`

All files from the given section and user will be downloaded to the current directory.

### Examples
 `furaffinity-dl gallery/kodardragon`

 `furaffinity-dl scraps/---`

 `furaffinity-dl favorites/kivuli`

You can also log in to download restricted content. To do that, log in to FurAffinity in your web browser, export cookies to a file from your web browser in Netscape format (there are extensions to do that [for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/) and [for Chrome/Vivaldi](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg)) and pass them to the script as a second parameter, like this:

 `furaffinity-dl gallery/gonnaneedabiggerboat /path/to/your/cookies.txt`

## TODO
 * Download author's description of the artwork, and ideally the entire description page along with user comments

## Disclaimer
It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them. For further disclaimers see LICENSE.

## See also

There is a similar downloader for VCL art library, see https://github.com/Shnatsel/vcl-dl
