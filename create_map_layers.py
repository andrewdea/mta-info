import os
import csv
from utils import data_dir, agencies
from route_groups import get_route_groups
from tqdm import tqdm
import re

keys = [
    "code",
    "name",
    "routes",
    "direction",
    "link",
    "id",
    "Latitude,Longitude",
    # "wheelchairBoarding" is always "UNKNOWN" & "locationType" is always 0
    # so I'm not including those values for now
    # "wheelchairBoarding",
    # "locationType",
]

def adjust_stops(stops: list[dict]) -> list[dict]:
    """
    Ensure the information in a stop is in the format we'd like to see
    within the Google Maps layer
    """
    # format the route name in a more readable way:
    agency_pattern = rf"({'|'.join(ag for ag in agencies)})_"
    for s in stops:
        s["Latitude,Longitude"] = f"{s.pop('lat')}, {s.pop('lon')}"
        s["link"] = f"https://bustime.mta.info/m/index?q={s['code']}"
        # ensure the code is read as a string, NOT a number:
        # put some whitespace around it
        s["code"] = "" + str(s["code"]) + "\t"
        routes = [re.sub(agency_pattern, "", s) for s in s.pop("routeIds")]
        s["routes"] = ", ".join(routes)
        s.pop("wheelchairBoarding")
        s.pop("locationType")
    return stops

if __name__ == "__main__":
    layers_dir = os.path.join(data_dir, "layers")
    route_groups = get_route_groups()
    if not os.path.exists(layers_dir):
        os.makedirs(layers_dir)
    for i, c in enumerate(tqdm(route_groups)):
        assert c["total"] < 2000, f"issues at chunk index: {i}"
        stops = adjust_stops(c["stops"])
        filename = os.path.join(layers_dir, f"group_{i}.csv")
        with open(filename, "w", newline="") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(stops)
        
        
            
