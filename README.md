MTA Info
==============

This repo is used to build [this custom Google Maps](https://www.google.com/maps/d/u/0/edit?mid=1Y-euNeFcsu06Zxfdl6u6-sca3Yp-KYY&usp=sharing).  
The map shows the codes for all the bus-stops within [MTA's bustime system](https://bustime.mta.info/m/index). This makes it easier to know what code to send to the MTA to know when the bus will arrive at any specific stop.  

## Map designs and details
Each stop within the map contains all the information provided by the MTA, including which bus-routes use the stop, which direction the routes go in, the stop's exact latitude and longitude, etc.  
They also contain a link to their bustime page ([example](https://bustime.mta.info/m/index?q=200884)), although hyperlinks aren't allowed on the mobile app, so the links would have to be copy-pasted.  
To make it easier to navigate, the stops are color-coded based on the direction of their route(s), and the stop-code is prominently displayed.  

### Route groups
Unfortunately, Google Maps has a few restraints for custom maps:
 - there can only be a maximum of 10 layers (groups of pins appearing at the same time)
 - there can't be more than 2000 pins per layer
 
Because of this, the routes are grouped into arbitrary layers: the objective of these groups had to be to fit within the above restrictions.  
I would like to eventually group the routes in a way that makes more sense from a user's point of view, which would allow people to easily set the map to display only the routes relevant to their neighborhood/use-case.

## Code design and details

### retrieving the data
All information is ultimately retrieved from the [MTA's API](https://bustime.mta.info/wiki/Developers/Index), although I've set up a mechanism to save the relevant data so as to minimize the amount of repeat calls.  
The two API queries are:
 1) `get_all_routes` to get information about all of the routes in the system
 2) `get_all_stops` to get information about all of the stops

### grouping the routes
Because of the constraints mentioned [here](#route-groups), it was necessary to devise a simple algorithm to build route groups such that:
 - each group contained a total of less than 2000 stops
 - there weren't more than 10 groups total
 
The algorithm, in [route_groups.py](./route_groups.py) is quite rudimentary but it works: 
 1. the routes are sorted by amount of total stops within the route
 2. from the sorted list, we select and remove the top, middle, and bottom elements
 (i.e. the routes with the most, the least, and the median amount of stops)
 3. these routes are put within a group
 4. we repeat step 2 until this group cannot take any more routes (the next route would tip it over the 2000-stop limit)
 5. we then create a new group, repeat steps 2-3-4 until the whole list is exhausted
 
### building the map
The map is built by importing all the CSV files created within `create_map_layers.py` into a Google Maps [custom map](https://www.google.com/maps/about/mymaps/). I am not currently aware of a way to build custom Google Maps programmatically: from the little research into their API I did, it appears there is no API to create/edit custom maps.
 
### Things to improve
See [TODO](./TODO.md).
