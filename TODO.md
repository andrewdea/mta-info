TODO
==============

## map

### substitute routeIds for bus names in stops
The stops currently display the routeIds in the map, but it would look better if they just used the bus names (the more human readable format):
MTA NYCT_B44 -> B44

### devise a better way to group routes
In spite of [the numerical constraints](./README.md#route-groups), it'd be great to be able to group routes in a way that makes more sense from a user's point of view. This could be by area / select service vs regular service / direction, etc.
Whichever way would allow people to easily set the map to display only the routes most relevant to their particular use-case. 
It may be possible to leverage the Google Maps API for this.

## code
### improve the 'overwrite' mechanism
The overwrite parameter is used to ensure we don't query the API unless we actually want to do so (either because we don't have a copy of the data or because we pass `overwrite = True`).
This mostly works but some work is needed to ensure that the parameter is correctly propagated throughout the code.

### make the repo pip-installable
Also add linter, etc

### build on the existing functionalities to allow more analyses of the data
 - Expand `get_select_routes.py` into a generalized `analysis.py`
 - what other features can be enabled from this data?
