import os
from utils import stops_dir, data_dir
import json
from tqdm import tqdm

route_dirs = [d for d in os.listdir(stops_dir)]
raw_filename = os.path.join(data_dir, "all_stops_raw.csv")
filtered_filename = os.path.join(data_dir, "all_stops_filtered.csv")

# all_stops: list[dict] = []


def read_all_stops() -> list[dict]:
    all_stops = []
    for d in route_dirs:
        stop_filename = os.path.join(stops_dir, d, "stops.json")
        with open(stop_filename) as f:
            stops = json.load(f)
        all_stops.extend(stops)
    return all_stops

def write_to_single_file(stops: list[dict], filename: str):
    with open(filename, "w") as f:
        f.write(json.dumps(stops, indent=4))
        print(f"wrote {filename}")

def remove_duplicates(stops: list[dict]) -> list[dict]:
    first = stops[0]
    first_keys = first.keys()
    # print(f"first_keys : {json.dumps(first, indent=4)}")

    filtered = []
    for stop in tqdm(stops):
        keys = stop.keys()
        assert keys == first_keys, f"DIFFERENT keys : {json.dumps(keys, indent=4)}"
        if stop not in filtered:
            filtered.append(stop)
    return filtered


if __name__ == "__main__":
    all_stops = read_all_stops()
    write_to_single_file(all_stops, raw_filename)
    filtered = remove_duplicates(all_stops)
    print(f"len(filtered) : {len(filtered)}")
    write_to_single_file(filtered, filtered_filename)
    
