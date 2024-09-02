from retrieve import (get_all_routes)
import re


sbs_pattern = r"^(s|S)elect (b|B)us (s|S)ervice"
via_pattern = r"^(V|v)ia "   

non_pattern_sbs_names = ["Via Woodhaven Blvd / Cross Bay Blvd",
                         "Via Broadway / Queens Blvd / Woodhaven Blvd / Cross Bay Blvd",
                         "Woodside LIRR, Jackson Heights E F M R 7 Subway, LaGuardia Airport"]

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
            assert (re.match(sbs_pattern, desc) or
                    desc is None or
                    desc in non_pattern_sbs_names)
        if desc is not None and re.match(sbs_pattern, desc):
            assert "+" in id
            select_routes.append(r)
    return select_routes

select_rids = [r["id"] for r in get_select_routes()]
print(f"select_rids : {select_rids}")
