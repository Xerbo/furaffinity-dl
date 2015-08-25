# FurAffinity Downloader
**furaffinity-dl** is a bash script for batch downloading of galleries and favorites from furaffinity.net users.
I've written it for preservation of culture, to counter the people nuking their galleries every once a while.

Supports all known submission types: images, texts and audio. Sorts downloaded files in chronological order.
I'd like to eventually expand it to download the description pages as well. Patches are welcome!

## Requirements

Coreutils, bash and wget are the only dependencies.

furaffinity-dl was tested only on Linux. It should also work on Mac and BSDs.
Windows users can probably get it to work via Cygwin, but running a virtual machine with Linux might be simpler.

## Usage
 `furaffinity-dl section/username`

All files from the given section and user will be downloaded to the current directory.

### Examples
 `furaffinity-dl gallery/kodardragon`

 `furaffinity-dl scraps/---`

 `furaffinity-dl favorites/kivuli`

You can also log in to FurAffinity and download restricted content, like this:

 `furaffinity-dl gallery/mithril07 your_username_here`

In this case you will be prompted for your password. It will not be displayed on the screen as you type it!

## TODO
 * Download author's description of the artwork, and ideally the entire description page along with user comments

## Disclaimer
It is your own responsibility to check whether batch downloading is allowed by FurAffinity terms of service and to abide by them. For further disclaimers see LICENSE.
