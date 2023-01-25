from tsp_data_structures import GeoCity, City, UEdge, OEdge
from tsp_solver import all_oedges, all_uedges
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
        print(f"Adding city {first_char} | {data} | {match}")
        geo_cities.append(GeoCity(id=data[0], x=data[1], y=data[2]))

print(f"Done Reading, creating cities")

# Figure out n
n = len(geo_cities)
# iter tools to select all pairs of cities
pairs = list(itertools.combinations(geo_cities, 2))
print(f"Done creating pairs")
# For each tuple calc distance and save UEdge,OEdge
count = 0
for p in pairs:
    count = count + 1
    d = distance.euclidean((p[0].x, p[0].y), (p[1].x, p[1].y))
    ue = UEdge(city_a=p[0].city, city_b=p[1].city, cost=d)
    oe = OEdge(city_a=p[0].city, city_b=p[1].city, cost=d)

    all_oedges.append(oe)
    all_uedges.append(ue)
    print(f"{count}) {ue}")

print(f"Done setting up the problem")
