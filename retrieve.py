import requests
import os
import json
from bs4 import BeautifulSoup
import re
import traceback
import urllib.parse
import utils
from typing import Union
from tqdm import tqdm

def remove_agency_name(s: str) -> str:
    for a in utils.agencies:
        s = s.replace(f"{a}_", "")
    return s

def get_route_from_id(rid: str) -> dict:
    all_routes = get_all_routes()
    route = next(filter(lambda x: x["id"] == rid, all_routes), None)
    if route is None:
        raise Exception(f"Couldn't find this route-id in the database: {rid}")
    return route

def get_stops_for_route(r: Union[dict, str],
                        overwrite: bool = False) -> list[dict]:
    if isinstance(r, str):
        route_id = r
        route = get_route_from_id(route_id)
    elif isinstance(r, dict):
        route = r
    shortname = route["shortname"]
    rid = route["id"]
    stops_filename = os.path.join(utils.stops_dir, f"{shortname}.json")

    if os.path.exists(stops_filename) and not overwrite:
        return utils.read_json(stops_filename)

    format_id = urllib.parse.quote(rid, safe='')
    print(f"Getting stops for route: {format_id} from API")
    url = f"https://bustime.mta.info/api/where/stops-for-route/{format_id}.json"
    params = {
        "key": utils.mta_api_key,
        "includePolylines": "false",
        "version": "2"
    }
    resp = requests.get(url, params)
    if resp.status_code != 200:
        print(f"r.status_code : {resp.status_code}")
        print(f"r.content : {resp.content}")
        raise Exception()
    content = resp.json()
    stops = content["data"]["references"]["stops"]
    utils.write_json(stops_filename, stops)
    return stops

def get_all_routes_str() -> list[str]:
    url = "https://bt.mta.info/m/routes/"
    r = requests.get(url)
    content = r.text
    soup = BeautifulSoup(content)
    pattern = r"\/m\/;jsessionid=[A-Z0-9]{32}\?q=.*"
    all_a_href = [a for a in soup.find_all('a', href=True)]
    all_route_links = [a for a in all_a_href if re.match(pattern, a["href"])]
    all_routes = [a.text for a in all_route_links]
    print(f"\n\n\nGot all routes. Size: {len(all_routes)}")
    return all_routes

def get_agency_info(agency: str, overwrite: bool = False) -> BeautifulSoup:
    agency_filename = os.path.join(utils.data_dir, f"agency_{agency}.xml")
    if os.path.exists(agency_filename) and not overwrite:
        with open(agency_filename, "r") as f:
            return BeautifulSoup(f.read())

    print(f"getting agency info from API")
    url = f"https://bustime.mta.info/api/where/routes-for-agency/{agency}.xml"
    params = {
        "key": utils.mta_api_key,
    }
    r = requests.get(url, params)
    content = r.text

    soup = BeautifulSoup(content)
    pretty = soup.prettify()

    with open(agency_filename, "w") as f:
        f.write(pretty)
    return soup

def get_agency_routes(agency: str, overwrite: bool = False) -> list[dict]:
    info = get_agency_info(agency, overwrite)
    route_els = [r for r in info.find_all("route")]
    keys = ["shortname", "id", "longname", "description"]
    all_routes = []
    for el in route_els:
        tags = {k: el.find(k) for k in keys}
        route = {k: v.text.strip() if v is not None else None
                 for (k,v) in tags.items()}
        # print(f"route : {route}")
        # route = {k: v.text for (k,v) in tags.items()} 
        all_routes.append(route)
    return all_routes

def get_all_routes(overwrite: bool = False) -> list[dict]:
    all_routes = []
    all_routes_filename = os.path.join(utils.routes_dir,
                                       "all_routes.json")
    if os.path.exists(all_routes_filename) and not overwrite:
        return utils.read_json(all_routes_filename)

    print(f"getting all routes, from the agency API")
    for ag in utils.agencies:
        ag_routes = get_agency_routes(ag, overwrite)
        all_routes.extend(ag_routes)
    utils.write_json(all_routes_filename, all_routes)
    return all_routes

def write_stops_for_route(route: dict):
    simple_form_route = route["shortname"]
    route_id = route["id"]
    directory = os.path.join(utils.stops_dir, simple_form_route)
    if not os.path.exists(directory):
        os.makedirs(directory)

    stops_filename = os.path.join(directory, "stops.json")
    if os.path.exists(stops_filename):
        print(f"WARN: skipping this : {route_id}")
        return
    
    # route = unadjusted_route
    stops = get_stops_for_route(route_id)
    with open(stops_filename, "w") as f:
        f.write(json.dumps(stops, indent=4))
    print(f"wrote stops for {route_id}")

def get_all_stops(overwrite: bool = False):
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
    all_stops = get_all_stops()
    print(f"len(all_stops) : {len(all_stops)}")
    filtered = []
    for s in all_stops:
        if s not in filtered:
            filtered.append(s)
    # print(f"len(filtered) : {len(filtered)}")
    return filtered


def get_stops_for_rids_no_repeats(rids: list[str]) -> list[dict]:
    processed_stops = []
    all_stops = []
    for r in rids:
        stops = get_stops_for_route(r)
        stops = [s for s in stops if s not in processed_stops]
        processed_stops.extend(stops)
        all_stops.extend(stops)
    return all_stops

if __name__ == "__main__":
    get_all_stops(overwrite=False)
    uniques = get_unique_stops()
    print(f"len(uniques) : {len(uniques)}")

    all_routes = get_all_routes()
    for r in all_routes:
        assert r["id"] is not None, f"weird: {r}"
    all_rids = [r["id"] for r in all_routes]
    no_repeats = get_stops_for_rids_no_repeats(all_rids)
    print(f"len(no_repeats) : {len(no_repeats)}")
    # assert len(no_repeats) == len(uniques)
    # TODO would be cool to check which is faster
    print("done")
