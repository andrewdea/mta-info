TODO
==============

## map

### devise a better way to group routes
In spite of [the numerical constraints](./README.md#route-groups), it'd be great to be able to group routes in a way that makes more sense from a user's point of view. This could be by area / select service vs regular service / direction, etc.
Whichever way would allow people to easily set the map to display only the routes most relevant to their particular use-case. 
It may be possible to leverage the Google Maps API to help for some of this: use the latitude/longitude of a route's stops to find which neighborhood they're in?

## code

### build on the existing functionalities to allow more analyses of the data
 - Expand `get_select_routes.py` into a generalized `analysis.py`
 - what other features can be enabled by this data?

### better CLI interface
features:
 - open map: opens the Google Maps in a default browser
 - update data: confirms whether we want to delete all current data, then runs `create_map_layers.py`
 - anything else?

### better logs in CLI
if you wanna go all out you can do like one of those cute python CLIs with all sort of emojis etc
