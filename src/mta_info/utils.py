import json
from typing import Union
import os

import requests
import logging
from git import Repo
import re

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_json(filename: str) -> Union[list, dict]:
    with open(filename, "r") as f:
        return json.load(f)


def write_json(filename: str, contents: Union[list, dict], name: str = ""):
    logger.debug(f"writing {name} to {filename}")
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, "w") as f:
        f.write(json.dumps(contents, indent=4))


def query_api(url: str, additional_params: dict = {}) -> requests.Response:
    if mta_api_key is None:
        key_request_url = "https://register.developer.obanyc.com/"
        raise Exception(
            f"""you need to set your MTA_API_KEY.
        Confirm that you have set the environment variable.
        If not, go to {key_request_url} to request a key."""
        )
    params = {"key": mta_api_key, **additional_params}
    return requests.get(url, params)


def change_is_expected(rel_path: str, repo: Repo) -> bool:
    rgx = r"<currenttime>\n-\s*[0-9]+\n\+\s*[0-9]+\n\s*<\/currenttime>\n\s*<text>\n\s*OK\s*$"
    diff_output = repo.git.diff(os.path.join(pkg_dir, rel_path))
    return bool(re.search(rgx, diff_output))


def check_for_changes():
    repo = Repo(pkg_dir)
    changed_data = [
        d
        for d in repo.index.diff(None)
        if d.b_path.startswith("data") and not change_is_expected(d.b_path, repo)
    ]
    if len(changed_data) > 0:
        logger.info("changes detected! Please update the map")


src_dir = os.path.dirname(__file__)
logger.debug(f"src_dir : {src_dir}")
pkg_dir = os.path.normpath(os.path.join(src_dir, "..", ".."))
logger.debug(f"pkg_dir : {pkg_dir}")
data_dir = os.path.join(pkg_dir, "data")
logger.debug(f"data_dir : {data_dir}")
stops_dir = os.path.join(data_dir, "stops")
routes_dir = os.path.join(data_dir, "routes")
all_routes_filename = os.path.join(routes_dir, "all_routes.json")
temp_dir = os.path.join(data_dir, "temp")

mta_api_key = os.getenv("MTA_API_KEY")


nyct_ag = "MTA NYCT"
abc_ag = "MTABC"
agencies = [nyct_ag, abc_ag]
