import os
import json
from bs4 import BeautifulSoup
import re
import traceback
import urllib.parse
import utils
from typing import Union
from tqdm import tqdm

def get_route_from_id(rid: str) -> dict:
    """
    Given a route id, return a dictionary with all the route's info
    """
    all_routes = get_all_routes()
    route = next(filter(lambda x: x["id"] == rid, all_routes), None)
    if route is None:
        raise Exception(f"Couldn't find this route-id in the database: {rid}")
    return route

def get_stops_for_route(r: Union[dict, str],
                        overwrite: bool = False) -> list[dict]:
    """
    Given a route, return all of its stops.
    """
    # make sure you have all needed info for the route
    if isinstance(r, str):
        route_id = r
        route = get_route_from_id(route_id)
    elif isinstance(r, dict):
        route = r
    shortname = route["shortname"]
    rid = route["id"]
    stops_filename = os.path.join(utils.stops_dir, f"{shortname}.json")

    # check if we need to query the API
    if os.path.exists(stops_filename) and not overwrite:
        routes = utils.read_json(stops_filename)
        assert isinstance(routes, list)
        return routes

    format_id = urllib.parse.quote(rid, safe='')
    print(f"Getting stops for route: {format_id} from API")
    url = f"https://bustime.mta.info/api/where/stops-for-route/{format_id}.json"
    params = {
        "includePolylines": "false",
        "version": "2"
    }
    resp = utils.query_api(url, params)
    if resp.status_code != 200:
        print(f"r.status_code : {resp.status_code}")
        print(f"r.content : {resp.content}")
        raise Exception()
    content = resp.json()
    stops = content["data"]["references"]["stops"]
    utils.write_json(stops_filename, stops)
    return stops

def get_agency_info(agency: str, overwrite: bool = False) -> BeautifulSoup:
    """
    Return all the info for the given agency.

    If overwrite is True, or if we have no saved xml file for this agency,
    we first query the API
    """
    agency_filename = os.path.join(utils.data_dir, f"agency_{agency}.xml")
    if os.path.exists(agency_filename) and not overwrite:
        with open(agency_filename, "r") as f:
            return BeautifulSoup(f.read())

    print(f"getting agency info from API")
    url = f"https://bustime.mta.info/api/where/routes-for-agency/{agency}.xml"
    r = utils.query_api(url)
    content = r.text

    soup = BeautifulSoup(content)
    pretty = soup.prettify()

    with open(agency_filename, "w") as f:
        f.write(pretty)
    return soup

def get_agency_routes(agency: str, overwrite: bool = False) -> list[dict]:
    """
    Return all the routes for the given agency
    """
    info = get_agency_info(agency, overwrite)
    route_els = [r for r in info.find_all("route")]
    keys = ["shortname", "id", "longname", "description"]
    all_routes = []
    for el in route_els:
        tags = {k: el.find(k) for k in keys}
        route = {k: v.text.strip() if v is not None else None
                 for (k,v) in tags.items()}
        all_routes.append(route)
    return all_routes

def get_all_routes(overwrite: bool = False) -> list[dict]:
    """
    Return a list of dictionaries: each dict has the info for each route.

    If overwrite is True, or if there is no saved all_routes.json file,
    we first query the API for the info about all routes
    """
    all_routes = []
    all_routes_filename = os.path.join(utils.routes_dir,
                                       "all_routes.json")
    if os.path.exists(all_routes_filename) and not overwrite:
        routes = utils.read_json(all_routes_filename)
        assert isinstance(routes, list)
        return routes

    print(f"getting all routes, from the agency API")
    for ag in utils.agencies:
        ag_routes = get_agency_routes(ag, overwrite)
        all_routes.extend(ag_routes)
    utils.write_json(all_routes_filename, all_routes)
    return all_routes

def get_all_stops(overwrite: bool = False) -> list[dict]:
    """
    Retun a list of dictionaries with info for each stops.

    *NOTE* that this function lists stops by iterating through each route,
    and therefore there are going to be duplicate stops for any stops covered
    by multiple routes.
    """
    all_routes = get_all_routes(overwrite)
    all_stops = []
    for r in tqdm(all_routes):
        try:
            stops = get_stops_for_route(r, overwrite)
            all_stops.extend(stops)
        except Exception as e:
            print(f"""Got an exception at route: {r}
            e: {e}""")
            print(traceback.format_exc())
    return all_stops

def get_unique_stops():
    """
    Return all stops, filtered so that we don't have any duplicates
    """
    all_stops = get_all_stops()
    print(f"len(all_stops) : {len(all_stops)}")
    filtered = []
    for s in all_stops:
        if s not in filtered:
            filtered.append(s)
    return filtered


def get_stops_for_rids_no_repeats(rids: list[str]) -> list[dict]:
    """
    Given a series of route-ids, retrieve all stops for each route,
    then return a list of all stops (with any duplicates filtered out)
    """
    processed_stops = []
    all_stops = []
    for r in rids:
        stops = get_stops_for_route(r)
        stops = [s for s in stops if s not in processed_stops]
        processed_stops.extend(stops)
        all_stops.extend(stops)
    return all_stops

# if __name__ == "__main__":
#     get_all_stops(overwrite=False)
#     uniques = get_unique_stops()
#     print(f"len(uniques) : {len(uniques)}")

#     all_routes = get_all_routes()
#     for r in all_routes:
#         assert r["id"] is not None, f"weird: {r}"
#     all_rids = [r["id"] for r in all_routes]
#     no_repeats = get_stops_for_rids_no_repeats(all_rids)
#     print(f"len(no_repeats) : {len(no_repeats)}")
#     # assert len(no_repeats) == len(uniques)
#     # TODO would be cool to check which is faster
#     print("done")
