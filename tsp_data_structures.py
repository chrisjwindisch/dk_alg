import copy
import itertools

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

    # gets all possible Orbits from edges, creates them if not created yet
    def get_or_create_orbits(oedges):
        orbits = []
        pairs_for_orbits = list(itertools.combinations(oedges, 2))
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

                if ordered_edge_tuple not in all_orbits:
                    # create it
                    all_orbits[ordered_edge_tuple] = Orbit(edge_a=oe_a, edge_b=oe_b)

                orbits.append(all_orbits[ordered_edge_tuple])
        return orbits


# Class to hold temp data for P
class PTemp:
    def __init__(self, xy, segment_to_remove):
        self.xy = xy
        self.segment_to_remove = segment_to_remove


# Represents a potential diagram that can contain multiple groups
# of independent or inversion dependent potential diagrams
class P:
    def __init__(self):
        self.segments = EdgeList()
        self.edges = EdgeList()
        self.delta_o = 0
        self.groups = []
        self.subtour_recalc_needed = False
        self.does_has_subtours = False

        self.edges_not_in_p = EdgeList()
        for oe in to_edges.oedges:
            self.edges_not_in_p.add_edge(oe)

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
        p_new.subtour_recalc_needed = True

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

        p_new.subtour_recalc_needed = True

    def swap(tour, edge_a, edge_b):
        # find edge_a, edge_b, update them with swap
        city_tuple_a = get_city_tuple(edge_a.city_a, edge_b.city_a)
        city_tuple_b = get_city_tuple(edge_a.city_b, edge_b.city_b)
        new_edge_a = all_oedges[city_tuple_a]
        new_edge_b = all_oedges[city_tuple_b]
        tour.remove_edge(edge_a)
        tour.remove_edge(edge_b)
        tour.add_edge(new_edge_a)
        tour.add_edge(new_edge_b)
        return new_edge_b

    def has_subtours(self):
        if not self.subtour_recalc_needed:
            return self.does_has_subtours

        # Don't maintain a tour, just calc on demand
        for g in self.groups:

            # Copy the tour # Can't use deepcopy because it will create new edges which are supposed to be immutable
            tour = EdgeList()
            # TODO: Optimize this by maintaining an ongoing Tour
            for oe in to_edges.oedges:
                tour.add_edge(oe)

            # first swap
            g_len = len(g.oedges)
            edge_a = g.oedges[0]
            edge_b = g.oedges[1]
            new_edge_b = P.swap(tour, edge_a, edge_b)
            for i in g_len - 1:
                new_edge_b = P.swap(tour, new_edge_b, g.oedge[i + 1])

        count = 0
        for j in len(tour):
            e0 = tour[j]
            e1 = tour[j + 1]
            if e0.city_b == e1.city_a:
                # not end of tour
                count = count + 1
                continue
            else:
                break

        if count < len(tour):
            self.does_has_subtours = True
        else:
            self.does_has_subtours = False

        self.subtour_recalc_needed = False

        return self.does_has_subtours


# Represents and iteration of k-opt
class I:
    def __init__(self, i):
        # i is the number of bubbles in the potential diagram
        self.i = i  # the ith depth of k-opt (i-opt)
        self.p_1st = None  # best potential diagram for i-opt
        self.p_2nd = None  # second best potential diagram
        # UPDATING this makes algorithm O(n^5) so not doing self.p_not_containint_xy_wz = {}  # indexed by UEdge tuple of (xy, wz)

        # slots contains the top 2 p's for a slot for this i
        # so it will be populated after I_i has been iterated through
        self.slots = {}  # indexed by segment

    def init_slots(self):
        for oe in all_oedges.values():
            if oe not in to_edges.oedges:
                self.slots[oe] = Slot(oe.city_a, oe.city_b)


class Slot:
    def __init__(self, city_a, city_b):
        self.best_delta_o = None
        self.p_1st = None
        self.p_2nd = None
        city_tuple = get_city_tuple(city_a, city_b)
        self.end_bubbles = city_tuple  # tuple of cities
        self.end_segment = all_oedges[city_tuple]
        self.p_2nd_ties = {}  # indexed by UEdge xy


def get_city_tuple(city_a, city_b):
    if city_a.id < city_b.id:
        city_tuple = (city_a, city_b)
    else:
        city_tuple = (city_b, city_a)
    return city_tuple


# edges indexed by tuple of cities
all_oedges = {}
all_uedges = {}

# indexed by oe's as order they appear in T0
all_orbits = {}

to_edges = EdgeList()

segment_to_ues = (
    {}
)  # indexed by oe, returns tuple of UEdges represented by that segment
