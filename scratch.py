from analyze_stops import get_select_routes
from retrieve import get_stops_for_route

select_routes = get_select_routes()

total_select_stops = 0

for r in select_routes:
    stops = get_stops_for_route(r["id"])
    total_select_stops += len(stops)

print(f"total_select_stops : {total_select_stops}")
