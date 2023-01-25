from tsp_data_structures import GeoCity, City, UEdge, OEdge, Orbit
from tsp_data_structures import (
    all_oedges,
    all_uedges,
    to_edges,
    segment_to_ues,
    all_orbits,
)
import itertools
import re
from scipy.spatial import distance

# Read file
filename = (
    "/Users/cj/Documents/Dev/quicker-google-docs/dk_alg/tsp_instances/ulysses22.tsp"
)
print(f"Reading {filename}")
file = open(filename, "r")
lines = file.readlines()

count = 0
# create GeoCities class with coordinates
geo_cities = []
print(f"Line by line")
file = open(filename, "r")
for line in lines:
    ln = line.strip()

    # Handle blank lines
    if ln:
        first_char = ln[0]
    else:
        continue

    # This is a data line
    if first_char.isnumeric():
        match = re.findall("[0-9.]*", line.strip())
        # remove empty strings
        data = [i for i in match if i]
        geo_cities.append(GeoCity(id=data[0], x=data[1], y=data[2]))

print(f"Done Reading, creating cities")

# Figure out n
n = len(geo_cities)
# iter tools to select all pairs of cities
print(f"Create city pairs for edges")
pairs = list(itertools.combinations(geo_cities, 2))
print(f"Done creating pairs")
# For each tuple calc distance and save UEdge,OEdge
count = 0
for p in pairs:
    count = count + 1
    d = distance.euclidean((p[0].x, p[0].y), (p[1].x, p[1].y))
    ue = UEdge(city_a=p[0].city, city_b=p[1].city, cost=d)
    oe = OEdge(city_a=p[0].city, city_b=p[1].city, cost=d)
    reverse_oe = OEdge(city_b=p[0].city, city_a=p[1].city, cost=d)

    city_tuple = (oe.city_a, oe.city_b)
    reverse_city_tuple = (reverse_oe.city_a, reverse_oe.city_b)
    all_oedges[city_tuple] = oe
    all_oedges[reverse_city_tuple] = reverse_oe
    all_uedges[city_tuple] = ue

prev_city = None
cur_city = None
for gc in geo_cities:
    cur_city = gc
    if prev_city:
        city_tuple = (prev_city.city, cur_city.city)
        to_edges.add_edge(all_oedges[city_tuple])
    prev_city = gc
# Complete the tour
city_tuple = (prev_city.city, geo_cities[0].city)
to_edges.add_edge(all_oedges[city_tuple])

for oe in all_oedges.values():
    if oe not in to_edges.oedges:
        # Find the to edges with each oe city
        e0 = None
        e1 = None
        for e in to_edges.uedges:
            if (
                (e.city_a == oe.city_a)
                or (e.city_a == oe.city_b)
                or (e.city_b == oe.city_a)
                or (e.city_b == oe.city_b)
            ):
                if not e0:
                    e0 = e
                else:
                    e1 = e

        segment_to_ues[oe] = (e0, e1)

pairs_for_orbits = list(itertools.combinations(to_edges.oedges, 2))
for pair in pairs_for_orbits:
    # Create all 4 combos of oe's for orbits
    if (
        (pair[0].city_a == pair[1].city_a)
        or (pair[0].city_a == pair[1].city_b)
        or (pair[0].city_b == pair[1].city_a)
        or (pair[0].city_b == pair[1].city_a)
    ):
        # Invalid pair because both edges contain one of the same cities
        continue

    # Get all 4 oe's
    oe_a = all_oedges[(pair[0].city_a, pair[0].city_b)]
    oe_rev_a = all_oedges[(pair[0].city_b, pair[0].city_a)]
    oe_b = all_oedges[(pair[1].city_a, pair[1].city_b)]
    oe_rev_b = all_oedges[(pair[1].city_b, pair[1].city_a)]

    orbit_combos = [
        (oe_a, oe_b),
        (oe_a, oe_rev_b),
        (oe_rev_a, oe_b),
        (oe_rev_a, oe_rev_b),
    ]

    for combo in orbit_combos:
        oe_a = combo[0]
        oe_b = combo[1]
        if oe_a.city_a.id < oe_a.city_b.id:
            city_tuple = (oe_a.city_a, oe_a.city_b)
        else:
            city_tuple = (oe_a.city_b, oe_a.city_a)
        ue_a = all_uedges[city_tuple]

        if oe_b.city_a.id < oe_b.city_b.id:
            city_tuple = (oe_b.city_a, oe_b.city_b)
        else:
            city_tuple = (oe_b.city_b, oe_b.city_a)
        ue_b = all_uedges[city_tuple]

        index_a = to_edges.uedges.index(ue_a)
        index_b = to_edges.uedges.index(ue_b)
        # all_orbits indexed by uedge tuple
        if index_a < index_b:
            ordered_edge_tuple = (ue_a, ue_b)
        else:
            ordered_edge_tuple = (ue_b, ue_a)

        all_orbits[ordered_edge_tuple] = Orbit(edge_a=oe_a, edge_b=oe_b)

print(f"Done setting up the problem")
