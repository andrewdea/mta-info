from retrieve import (get_all_routes,
                      get_stops_for_route,
                      get_unique_stops)
import utils
import os
import json
import re
from tqdm import tqdm
import statistics

processed_stops = []
def get_unique_stops_per_rid(rid: str, overwrite: bool = False) -> list[dict]:
    stops = get_stops_for_route(rid, overwrite)
    filtered_stops = [s for s in stops if s not in processed_stops]
    processed_stops.extend(filtered_stops)
    return filtered_stops

def all_unique_stops_per_route(overwrite: bool = False) -> list[dict]:
    info_filename = os.path.join(utils.temp_dir, "info.json")
    if os.path.exists(info_filename) and not overwrite:
        return utils.read_json(info_filename)
    all_info = []
    for r in tqdm(get_all_routes(overwrite)):
        stops = get_unique_stops_per_rid(r["id"], overwrite)
        # getting only the unique stops
        # stops = [s for s in stops if s not in processed_stops]
        # processed_stops.extend(stops)
        total_stops = len(stops)
        info = {"rid": r["id"],
                "total unique stops": total_stops,
                "stops": stops}
        all_info.append(info)
    all_totals = [i["total unique stops"] for i in all_info]
    mean = statistics.fmean(all_totals)
    median = statistics.median(all_totals)
    print(f"mean of total stops per route: {mean}")
    print(f"median of total stops per route: {median}")
    
    utils.write_json(info_filename, all_info)
    return all_info

def select_top_bottom_middle(lst) -> list[dict]:
    """
    retun a list of dictionaries.
    each dictionary is the result of picking the top, bottom, and middle
    in the sorted list, and combining their stops and routes.
    """
    sublists = []
    final_dicts = []
    total = 0
    while len(lst) > 0:
        sublist = []
        # Select and remove the top (first) item
        if len(lst) > 0:
            sublist.append(lst.pop(0))
        # Select and remove the bottom (last) item
        if len(lst) > 0:
            sublist.append(lst.pop(-1))
        # Select and remove the middle item
        if len(lst) > 0:
            middle_index = len(lst) // 2
            sublist.append(lst.pop(middle_index))
        # sublist.append({"overall total": total})
        
        sublists.append(sublist)

        total = sum(r["total unique stops"] for r in sublist)
        all_rids = [r["rid"] for r in sublist]
        stops = []
        for r in sublist:
            stops.extend(r["stops"])
        res_dict = {"overall total": total,
                "all routes": all_rids,
                "stops": stops}
        final_dicts.append(res_dict)
    return final_dicts



def get_route_groups(overwrite: bool = False) -> list:
    route_groups_filename = os.path.join(utils.temp_dir, "route_groups.json")
    if os.path.exists(route_groups_filename) and not overwrite:
        return utils.read_json(route_groups_filename)
    infos = all_unique_stops_per_route(overwrite)
    print(f"len(processed_stops) : {len(processed_stops)}")
    sorted_routes = sorted(infos, key=lambda x: x["total unique stops"])
    print(f"sorted_routes[0] : {sorted_routes[0]}")
    print(f"sorted_routes[-1]['rid'] : {sorted_routes[-1]['rid']}")
    subdicts = select_top_bottom_middle(sorted_routes)
    all_route_groups = []
    current_chunk = {"total": 0}
    for d in subdicts:
        sub_total = d["overall total"]
        if sub_total > 2000:
            raise Exception(f"too large: {d}")
        if current_chunk.get("total", 0) + sub_total > 2000:
            all_route_groups.append(current_chunk)
            current_chunk = {}
        current_chunk["all routes"] = (current_chunk.get("all routes", [])
                                       + d["all routes"])
        current_chunk["total"] = current_chunk.get("total", 0) + sub_total
        try:
            current_chunk["stops"] = current_chunk.get("stops", []) + d["stops"]
        except Exception as e:
            print(f"e : {e}")
            print(f"d : {d}")
            raise e
    all_route_groups.append(current_chunk)
    utils.write_json(route_groups_filename, all_route_groups)
    print(f"len(all_route_groups) : {len(all_route_groups)}")
    return all_route_groups
