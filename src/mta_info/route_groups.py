from mta_info.retrieve import get_all_routes, get_stops_for_route
import mta_info.utils as utils
import os
from tqdm import tqdm
import statistics
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

processed_stops = []


def get_unique_stops_per_rid(rid: str) -> list[dict]:
    stops = get_stops_for_route(rid)
    filtered_stops = [s for s in stops if s not in processed_stops]
    processed_stops.extend(filtered_stops)
    return filtered_stops


def all_unique_stops_per_route() -> list[dict]:
    all_info = []
    logger.info("getting all unique stops per route")
    for r in tqdm(get_all_routes()):
        stops = get_unique_stops_per_rid(r["id"])
        total_stops = len(stops)
        info = {"rid": r["id"], "total unique stops": total_stops, "stops": stops}
        all_info.append(info)
    all_totals = [i["total unique stops"] for i in all_info]
    mean = statistics.fmean(all_totals)
    median = statistics.median(all_totals)
    logger.info(f"mean of total stops per route: {mean}")
    logger.info(f"median of total stops per route: {median}")

    # utils.write_json(info_filename, all_info)
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
        if len(lst) > 0:
            sublist.append(lst.pop(0))
        if len(lst) > 0:
            sublist.append(lst.pop(-1))
        if len(lst) > 0:
            middle_index = len(lst) // 2
            sublist.append(lst.pop(middle_index))

        sublists.append(sublist)

        total = sum(r["total unique stops"] for r in sublist)
        all_rids = [r["rid"] for r in sublist]
        stops = []
        for r in sublist:
            stops.extend(r["stops"])
        res_dict = {"overall total": total, "all routes": all_rids, "stops": stops}
        final_dicts.append(res_dict)
    return final_dicts


def get_route_groups() -> list:
    """
    Group routes into groups such that no group has a total of more than
    2000 stops (this is because of a limit in how many elements Google Maps
    allows in a layer)
    """
    route_groups_filename = os.path.join(utils.data_dir, "route_groups.json")
    if os.path.exists(route_groups_filename):
        route_groups = utils.read_json(route_groups_filename)
        assert isinstance(route_groups, list)
        return route_groups
    infos = all_unique_stops_per_route()
    logger.info(f"len(processed_stops) : {len(processed_stops)}")
    sorted_routes = sorted(infos, key=lambda x: x["total unique stops"])
    logger.info(f"sorted_routes[0] : {sorted_routes[0]}")
    logger.info(f"sorted_routes[-1]['rid'] : {sorted_routes[-1]['rid']}")
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
        current_chunk["all routes"] = (
            current_chunk.get("all routes", []) + d["all routes"]
        )
        current_chunk["total"] = current_chunk.get("total", 0) + sub_total
        try:
            current_chunk["stops"] = current_chunk.get("stops", []) + d["stops"]
        except Exception as e:
            logger.warn(f"e : {e}")
            logger.warn(f"d : {d}")
            raise e
    all_route_groups.append(current_chunk)
    utils.write_json(route_groups_filename, all_route_groups)
    logger.info(f"len(all_route_groups) : {len(all_route_groups)}")
    return all_route_groups
