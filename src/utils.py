import json
from typing import Union
import os

import requests


def read_json(filename: str) -> Union[list, dict]:
    with open(filename, "r") as f:
        return json.load(f)


def write_json(filename: str, contents: Union[list, dict], name: str = ""):
    print(f"writing {name} to {filename}")
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


src_dir = os.path.dirname(__file__)
print(f"src_dir : {src_dir}")
pkg_dir = os.path.normpath(os.path.join(src_dir, ".."))
print(f"pkg_dir : {pkg_dir}")
data_dir = os.path.join(pkg_dir, "data")
print(f"data_dir : {data_dir}")
stops_dir = os.path.join(data_dir, "stops")
routes_dir = os.path.join(data_dir, "routes")
all_routes_filename = os.path.join(routes_dir, "all_routes.json")
temp_dir = os.path.join(data_dir, "temp")

mta_api_key = os.getenv("MTA_API_KEY")


nyct_ag = "MTA NYCT"
abc_ag = "MTABC"
agencies = [nyct_ag, abc_ag]
