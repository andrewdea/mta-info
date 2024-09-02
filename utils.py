import json
from typing import Union
import os

def read_json(filename: str) -> Union[list, dict]:
    with open(filename, "r") as f:
        return json.load(f)

def write_json(filename: str, contents: Union[list, dict], name: str = ""):
    print(f"writing {name} to {filename}")
    with open(filename, "w") as f:
        f.write(json.dumps(contents, indent=4))
    
data_dir = "data"
routes_dir_root = os.path.join(data_dir, "routes")
all_routes_filename = os.path.join(routes_dir_root, "all_routes.json")
temp_dir = "temp"

mta_api_key = os.getenv("MTA_API_KEY")
if mta_api_key is None:
    key_request_url = "https://register.developer.obanyc.com/"
    raise Exception(f"""you need to set your MTA_API_KEY.
    Confirm that you have set the environment variable.
    If not, go to {key_request_url} to request a key.""")

nyct_ag = "MTA NYCT"
abc_ag = "MTABC"
agencies = [nyct_ag, abc_ag]
