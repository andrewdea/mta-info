import os
import csv
from utils import data_dir
from analyze_stops import get_route_groups
from tqdm import tqdm

keys = [
    "code",
    "link",
    "direction",
    "id",
    "Latitude,Longitude",
    "name",
    "routeIds",
     # TODO: adjust routeIds to remove agency name and just keep the route name
    # "routes",

    # "wheelchairBoarding" is always "UNKNOWN" & "locationType" is always 0
    # so I'm not including those values for now
    # "wheelchairBoarding",
    # "locationType",
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

layers_dir = os.path.join(data_dir, "layers")
if __name__ == "__main__":
    route_groups = get_route_groups(overwrite=True)
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
        
        
            
