import os
import json
import traceback
import csv
from retrieve import (get_all_routes,
                         get_stops_for_route,
                         get_stops_for_rids_no_repeats)
from utils import (mta_api_key,
                         nyct_ag,
                         abc_ag,
                         data_dir,
                         temp_dir,
                         routes_dir_root)
# from combine_stops_to_json import remove_duplicates
from analyze_stops import get_chunks
from tqdm import tqdm

route_dirs = [d for d in os.listdir(routes_dir_root)]

csv_filename = os.path.join(data_dir, "stops.csv")


keys = [
    "code",
    # "description", # don't think this adjustment is needed
    "link",
    "direction",
    "id",
    # "locationType",
    "Latitude,Longitude",
    "name",
    "routeIds",
    # "bus names", # don't think this adjustment is needed
    # "wheelchairBoarding",
]

def adjust_stops(stops: list[dict]) -> list[dict]:
    for s in stops:
        # s["description"] = s["code"]
        s["Latitude,Longitude"] = f"{s.pop('lat')}, {s.pop('lon')}"
        s["link"] = f"https://bustime.mta.info/m/index?q={s['code']}"
        # r_ids = [r.replace("MTA NYCT_", "").replace("MTABC_", "") for r in s["routeIds"]]
        # s["bus names"] = r_ids
        s["code"] = "'" + str(s["code"]) + "'" # enforce this as string
        # "wheelchairBoarding" is always "UNKNOWN" & "locationType" is always 0
        # so I'm not including those values for now
        s.pop("wheelchairBoarding")
        s.pop("locationType")
    return stops

def get_route_stops(route: dict) -> list[dict]:
    shortname = route["shortname"]
    filename = os.path.join(routes_dir_root, f"{shortname}", "stops.json")
    with open(filename, "r") as f:
        stops = json.load(f)
    return stops
        
    

def process_and_chunk():
    processed_stops = []
    # getting the routes in the order that the agency call gives them
    # the idea is that their order might make more sense
    all_routes = get_all_routes()

    count_stops = 0
    this_routes = []
    # attempt = os.path.join(temp_dir, "newtry.csv")
    count_files = 0
    for r in all_routes:
        stops = get_route_stops(r)
        stops = [s for s in stops if s not in processed_stops]
        if len(stops) == 0:
            continue
        processed_stops.extend(stops)
        stops = adjust_stops(stops)
        assert len(stops) < 2000 # we'd need to figure out a different way
        if count_stops == 0 or count_stops + len(stops) > 2000:
            count_stops = 0
            count_files += 1
            with open(os.path.join(temp_dir, f"try_{count_files}.csv"), "w", newline="") as f:
                dict_writer = csv.DictWriter(f, keys)
                dict_writer.writeheader()
        with open(os.path.join(temp_dir, f"try_{count_files}.csv"), "a", newline="") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writerows(stops)
        count_stops += len(stops)

processed_stops = []
def get_unique_stops_per_rid(rid: str) -> list[dict]:
    stops = get_stops_for_route(rid)
    filtered_stops = [s for s in stops if s not in processed_stops]
    processed_stops.extend(filtered_stops)
    return filtered_stops

count_same = 0
layers_dir = os.path.join(data_dir, "layers")
if __name__ == "__main__":
    chunks = get_chunks()
    if not os.path.exists(layers_dir):
        os.makedirs(layers_dir)
    for i, c in enumerate(tqdm(chunks)):
        assert c["total"] < 2000, f"issues at chunk index: {i}"
        stops = adjust_stops(c["stops"])
        filename = os.path.join(layers_dir, f"group_{i}.csv")
        with open(filename, "w", newline="") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(stops)
        
        
            
