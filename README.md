# FurAffinity Downloader
**furaffinity-dl** is a BASH script for batch downloading of galleries, scraps and favorites from furaffinity.net users. 
I've written it for preservation of culture, to counter the people nuking their galleries every once a while. 

Supports all known submission types: images, texts and audio. Right now it dowloads only the files themselves. 
I'd like to eventually expand it to download the description pages as well and arrange them in chronologiclal order. Patches are welcome!

## Requirements

Coreutils, bash and wget are the only requirements.

furaffinity-dl was tested only on Linux. It should also work on Mac and BSDs.
Windows users can probably get it to work via Cygwin, but running a virtual machine with Linux might be simpler.

## Usage
 `furaffinity-dl section/username`

All files from the given section and user will be downloaded to the current directory.
### Examples
 `furaffinity-dl gallery/ymxa`
 `furaffinity-dl scraps/---`
 `furaffinity-dl favorites/kivuli`

## TODO
 * Support cookies - needs UI and documentation, can already be achieved by
   adding  "--load-cookies *file*" the wget line in the begginning of the script
 * Download author's description of the artwork, and ideally the entire description page along with user comments
 * Sort the downloaded stuff in chronological order
