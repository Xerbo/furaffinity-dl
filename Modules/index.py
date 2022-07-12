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

            if p.is_file():
                name = p.stem
                ext = p.suffix
                match = re.search(r"\([0-9]{5,}\)", name)
                if match is None and ext not in [".txt", ".idx"]:
                    return

                if match:
                    idx.write(f"{match[0]}\n")
                    print(f"found: {p}")

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
