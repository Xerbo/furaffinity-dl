import argparse

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="Downloads the entire gallery/scraps/folder/favorites \
of a furaffinity user, or your submissions notifications",
    epilog="""
Examples:
 python3 furaffinity-dl.py koul -> will download gallery of user koul
 python3 furaffinity-dl.py koul scraps -> will download scraps of user koul
 python3 furaffinity-dl.py mylafox favorites -> will download favorites \
of user mylafox \n
You can also download a several users in one go like this:
 python3 furaffinity-dl.py "koul radiquum mylafox" \
-> will download gallery of users koul -> radiquum -> mylafox
You can also provide a file with user names that are separated by a new line\n
You can also log in to FurAffinity in a web browser and load cookies to \
download age restricted content or submissions:
 python3 furaffinity-dl.py letodoesart -c cookies.txt -> will download \
gallery of user letodoesart including Mature and Adult submissions
 python3 furaffinity-dl.py --submissions -c cookies.txt -> will download your \
submissions notifications \n
DISCLAIMER: It is your own responsibility to check whether batch downloading \
is allowed by FurAffinity terms of service and to abide by them.
""",
)
parser.add_argument(
    "username",
    nargs="?",
    help="username of the furaffinity \
user",
)
parser.add_argument(
    "category",
    nargs="?",
    help="the category to download, gallery/scraps/favorites \
[default: gallery]",
    default="gallery",
)
parser.add_argument("-c", "--cookies", help="path to a NetScape cookies file")
parser.add_argument(
    "--output",
    "-o",
    dest="output_folder",
    default="Submissions",
    help="set a custom output folder",
)
parser.add_argument(
    "--check",
    action="store_true",
    help="check and download latest submissions of a user",
)
parser.add_argument(
    "-ua",
    "--user-agent",
    dest="user_agent",
    default="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 \
Firefox/101.0",
    help="Your browser's useragent, may be required, depending on your luck",
)
parser.add_argument(
    "-sub",
    "--submissions",
    action="store_true",
    help="download your \
submissions",
)
parser.add_argument(
    "-f",
    "--folder",
    help="full path of the furaffinity gallery folder. for instance 123456/\
Folder-Name-Here",
)
parser.add_argument(
    "-s",
    "--start",
    default=1,
    help="page number to start from",
)
parser.add_argument(
    "-S",
    "--stop",
    default=0,
    help="Page number to stop on. Specify the full URL after the username: for \
favorites pages (1234567890/next) or for submissions pages: \
(new~123456789@48)",
)
parser.add_argument(
    "-rd",
    "--redownload",
    action="store_false",
    help="Redownload files that have been downloaded already",
)
parser.add_argument(
    "-i",
    "--interval",
    type=int,
    default=0,
    help="delay between downloading pages in seconds [default: 0]",
)
parser.add_argument(
    "-r",
    "--rating",
    action="store_false",
    help="disable rating separation",
)
parser.add_argument(
    "--filter",
    action="store_true",
    dest="submission_filter",
    help="enable submission filter",
)
parser.add_argument(
    "-m",
    "--metadata",
    action="store_true",
    help="enable metadata saving",
)
parser.add_argument(
    "--download",
    help="download a specific submission by providing its id",
)
parser.add_argument(
    "-jd",
    "--json-description",
    dest="json_description",
    action="store_true",
    help="download description as a JSON list",
)
parser.add_argument(
    "--login",
    action="store_true",
    help="extract furaffinity cookies directly from your browser",
)
parser.add_argument(
    "--index",
    action="store_true",
    help="create an index of downloaded files in an output folder",
)

args = parser.parse_args()

# positional
username = args.username
category = args.category

if username is not None:
    username = username.split(" ")

# Custom input
cookies = args.cookies
output_folder = args.output_folder
download = args.download
interval = args.interval
user_agent = args.user_agent
start = args.start
stop = args.stop
folder = args.folder

# True\False

login = args.login
check = args.check
index = args.index
submissions = args.submissions
json_description = args.json_description
metadata = args.metadata
dont_redownload = args.redownload
rating = args.rating
submission_filter = args.submission_filter

# Colors
SUCCESS_COLOR = "\033[1;92m"
WARN_COLOR = "\033[1;33m"
ERROR_COLOR = "\033[1;91m"
END = "\033[0m"

# Globals
BASE_URL = "https://www.furaffinity.net"
username_replace_chars = {
    " ": "",
    "_": "",
}
search = 'YCH[a-z $-/:-?{-~!"^_`\\[\\]]*OPEN\
|OPEN[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*CLOSE\
|CLOSE[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*ABLE\
|AVAIL[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*CLONE\
|CLONE[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|YCH[a-z $-/:-?{-~!"^_`\\[\\]]*LIM\
|LIM[a-z $-/:-?{-~!"^_`\\[\\]]*YCH\
|COM[a-z $-/:-?{-~!"^_`\\[\\]]*OPEN\
|OPEN[a-z $-/:-?{-~!"^_`\\[\\]]*COM\
|COM[a-z $-/:-?{-~!"^_`\\[\\]]*CLOSE[^r]\
|CLOSE[a-z $-/:-?{-~!"^_`\\[\\]]*COM\
|FIX[a-z $-/:-?{-~!"^_`\\[\\]]*ICE\
|TELEGRAM[a-z $-/:-?{-~!"^_`\\[\\]]*STICK\
|TG[a-z $-/:-?{-~!"^_`\\[\\]]*STICK\
|REM[insder]*\\b\
|\\bREF|\\bSale|auction|multislot|stream|adopt'
