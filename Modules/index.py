import contextlib
import re
from functools import lru_cache
from pathlib import Path

import Modules.config as config

@lru_cache(maxsize=None)
def start_indexing(path, layer=0):

    """Recursively iterate over each item in path
    and print item's name.
    """

    # make Path object from input string
    path = Path(path)
    with open(f"{config.output_folder}/index.idx", encoding="utf-8", mode="a+") as idx:

        # iter the directory
        for p in path.iterdir():

            name = p.stem
            if p.is_file():
                fname = re.search(r"\([0-9]{5,}\)", name)
                if fname is None and name != "index":
                    return

                if match := re.search(r"\([0-9]{5,}\)", name):
                    idx.write(f"{match[0]}\n")
                    print(f"found: {p} by {match[0]}")

            elif p.is_dir():
                start_indexing(p, layer + 1)
            else:
                raise FileNotFoundError()


@lru_cache(maxsize=None)
def check_file(path):
    view_id = path.split("/")[-2:-1][0]
    with contextlib.suppress(FileNotFoundError):
        with open(f"{config.output_folder}/index.idx", encoding="utf-8") as idx:
            index = idx.read()
            match = re.search(rf"\({view_id}\)", index)
        if match is not None:
            return True
