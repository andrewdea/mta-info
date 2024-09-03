from retrieve import get_all_routes
import re


sbs_pattern = r"^(s|S)elect (b|B)us (s|S)ervice"
via_pattern = r"^(V|v)ia "

non_pattern_sbs_names = [
    "Via Woodhaven Blvd / Cross Bay Blvd",
    "Via Broadway / Queens Blvd / Woodhaven Blvd / Cross Bay Blvd",
    "Woodside LIRR, Jackson Heights E F M R 7 Subway, LaGuardia Airport",
]


def get_select_routes() -> list[dict]:
    """
    Return list of all select routes.

    Select routes are ones that have a '+' at the end of their id.
    """
    formatted = get_all_routes()
    select_routes = []
    for r in formatted:
        id = r["id"]
        desc = r["description"]
        if "+" in id:
            assert (
                re.match(sbs_pattern, desc)
                or desc is None
                or desc in non_pattern_sbs_names
            )
        if desc is not None and re.match(sbs_pattern, desc):
            assert "+" in id
            select_routes.append(r)
    return select_routes


# select_rids = [r["id"] for r in get_select_routes()]
# print(f"select_rids : {select_rids}")

import os
from utils import write_json, temp_dir
def get_unique_areas():
    formatted = get_all_routes()
    unique_longnames = []
    unique_desc = []
    for r in formatted:
        longname = r["longname"]
        ln_split = longname.split(" - ")
        for l in ln_split:
            if l not in unique_longnames:
                unique_longnames.append(l)
        desc = r["description"]
        if desc is None:
            continue
        # TODO: maybe this should be a regex
        if re.match(sbs_pattern, desc):
            # print(f"desc : {desc}")
            desc = desc[len("Select Bus Service "):]
            # print(f"updated desc : '{desc}'")
        if re.match(via_pattern, desc):
            desc = desc[len("via "):]
        else:
            print(f"desc without via: {desc}")
        desc_split = desc.split(" / ")
        for d in desc_split:
            if d not in unique_desc:
                unique_desc.append(d)
    ln_filename = os.path.join(temp_dir, "unique_longnames")
    write_json(ln_filename, unique_longnames)
    desc_filename = os.path.join(temp_dir, "unique_descriptions")
    write_json(desc_filename, unique_desc)

get_unique_areas()
