import copy

# globals at bottom of file because classes need to be defined first


class GeoCity:
    def __init__(self, id, x, y):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)
        self.city = City(id=id)


class City:
    def __init__(self, id):
        self.id = int(id)


class OEdge:
    def __init__(self, city_a, city_b, cost):
        self.city_a = city_a
        self.city_b = city_b
        self.cost = int(cost)


class UEdge:
    def __init__(self, city_a, city_b, cost):
        self.city_a = city_a
        self.city_b = city_b
        self.cost = int(cost)


class EdgeList:
    def __init__(self):
        self.uedges = []
        self.oedges = []

    def add_edge(self, e):
        if isinstance(e, OEdge):
            self.oedges.append(e)

            # They cities need to be in order to find the uedge
            if e.city_a.id < e.city_b.id:
                city_tuple = (e.city_a, e.city_b)
            else:
                city_tuple = (e.city_b, e.city_a)
            self.uedges.append(all_uedges[city_tuple])
        elif isinstance(e, UEdge):
            city_tuple = (e.city_a, e.city_b)
            self.uedges.append(e)
            self.oedges.append(all_oedges[city_tuple])

    def remove_edge(self, e):
        if isinstance(e, OEdge):
            self.oedges.remove(e)

            # They cities need to be in order to find the uedge
            if e.city_a.id < e.city_b.id:
                city_tuple = (e.city_a, e.city_b)
            else:
                city_tuple = (e.city_b, e.city_a)
            self.uedges.remove(all_uedges[city_tuple])
        elif isinstance(e, UEdge):
            city_tuple = (e.city_a, e.city_b)
            self.uedges.remove(e)
            self.oedges.remove(all_oedges[city_tuple])

    def add_edge_between(xy, e_before):
        e = xy
        index = self.uedges.index(e_before)
        self.uedges.insert(index + 1, e)

        oe = all_oedges[e.city_a, e.city_b]
        oe_before = all_oedges[e_before.city_a, e_before.city_b]
        index = self.oedges.index(oe_before)
        self.oedges.insert(index + 1, oe)


class Orbit:
    def __init__(self, edge_a, edge_b):
        self.edge_a = edge_a
        self.edge_b = edge_b
        self.segments = EdgeList()
        seg_a = all_oedges[(edge_a.city_a, edge_b.city_a)]
        seg_b = all_oedges[(edge_a.city_b, edge_b.city_b)]
        self.segments.add_edge(seg_a)
        self.segments.add_edge(seg_b)
        self.delta_o = 0 - edge_a.cost - edge_b.cost + seg_a.cost + seg_b.cost


# Class to hold temp data for P
class PTemp:
    def __init__(self, xy, segment_to_remove):
        self.xy = xy
        self.segment_to_remove = segment_to_remove


class P:
    def __init__(self):
        self.segments = EdgeList()
        self.edges = EdgeList()
        self.edges_not_in_p = EdgeList()
        self.delta_o = 0
        self.groups = []

    # Light weight on purpose for efficiency, it doesn't update all the data structures
    # only the ones needed by the most expensive part of the algorithm
    def add_edge_light(self, xy, segment_to_remove):
        s = segment_to_remove
        p_new = copy.deepcopy(self)
        p_new.segments.remove_edge(s)
        seg1 = all_oedges[(s.city_a, xy.city_a)]
        seg2 = all_oedges[(xy.city_b, s.city_b)]
        p_new.segments.add_edge(seg1)
        p_new.segments.add_edge(seg2)
        p_new.delta_o = p_new.delta_o - s.cost + seg1.cost + seg2.cost
        p_new.temp = PTemp(xy=xy, segment_to_remove=segment_to_remove)

        return p_new

    # Fills in the data structures skipped by add_edge_light(), which
    # intentionally skips some data structures to save time incase it ends up not being needed
    def fill_in(self):
        self.edges_not_in_p.remove_edge(self.temp.xy)
        for g in self.groups:
            # Figure out the two bubbles represented by the segment
            edges_before_switch = segment_to_ues[self.temp.segment_to_remove]
            if edges_before_switch[0] in g.uedges:
                g.add_edge_between(
                    xy=self.temp.xy,
                    e_before=edges_before_switch[0],
                )
        self.temp = None  # Deallocate so can't be used by mistake or takes up memory

    def add_orbit(self, orbit):
        p_new = copy.deepcopy(self)

        edge_list = EdgeList()
        edge_list.add_edge(orbit.edge_a)
        edge_list.add_edge(orbit.edge_b)
        p_new.groups.append(edge_list)

        p_new.segments.add_edge(orbit.segments[0])
        p_new.segments.add_edge(orbit.segments[1])
        p_new.delta_o = p_new.delta_o + orbit.delta_o

        p_new.edges_not_in_p.remove_edge(orbit.edge_a)
        p_new.edges_not_in_p.remove_edge(orbit.edge_b)


# edges indexed by tuple of cities
all_oedges = {}
all_uedges = {}

# indexed by oe's as order they appear in T0
all_orbits = {}

# NOTE these are ue's, as such the final edge is left out because it must be an oe
to_edges = EdgeList()

segment_to_ues = (
    {}
)  # indexed by oe, returns tuple of UEdges represented by that segment
