TODO
==============

## map

### devise a better way to group routes
In spite of [the numerical constraints](./README.md#route-groups), it'd be great to be able to group routes in a way that makes more sense from a user's point of view. This could be by area / select service vs regular service / direction, etc.
Whichever way would allow people to easily set the map to display only the routes most relevant to their particular use-case. 
It may be possible to leverage the Google Maps API to help for some of this: use the latitude/longitude of a route's stops to find which neighborhood they're in?

### contribute the data to [OpenStreetMap](https://openstreetmap.us/)
Perhaps also contribute to [an app](https://apps.apple.com/us/app/osmand-maps-travel-navigate/id934850257) and see if it's possible to include the MTA query directly within the app (ie, select a bus stop, query the bustime API, show the results).

## code

### build on the existing functionalities to allow more analyses of the data
 - Expand `get_select_routes.py` into a generalized `analysis.py`
 - what other features can be enabled by this data?

### better logs in CLI
if you wanna go all out you can do like one of those cute python CLIs with all sort of emojis etc
