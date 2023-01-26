# globals
import itertools
from tsp_data_structures import City, EdgeList, OEdge, UEdge, Orbit, P, I, Slot
from tsp_data_structures import n, to_edges

p_best = None
I = {}


def solve():
    for i in range(2, n):
        I[i] = I(i=i)
        I_i = I[i]
        I_i.init_slots()

        # Only add orbits on first I_2
        if i > 2:
            for slot in I[I_i.i - 1].slots:
                try_adding_xy(slot, I_i)
            if (i - 2) in I:
                add_orbits(I_i)


def try_adding_xy(slot, I_i):
    p0 = slot.p_1st
    p1 = slot.p_2nd

    not_in_p1 = p_2nd_ties.keys()

    # edges that can't be added to p0
    # This is any possible edge that doesn't appear in p0, but appears in one of p_2nd_ties
    a = set(p0.uedges) - set(not_in_p1)

    # edges that can be added to both or just p0
    b = set(to_edges.uedges) - set(p0.uedges)

    for xy in b:
        p_new = p0.add_edge_light(xy, slot.end_segment)
        for seg in p_new.segments.oedges:
            try_update_bests(p_new=p_new, I_i=I_i)
            did_update = try_update_slot(slot=I_i.slots[seg], p_new=p_new)

    for xy in a:
        p_new = p1.add_edge_light(xy, slot.end_segment)
        for seg in p_new.segments.oedges:
            try_update_bests(p_new=p_new, I_i=I_i)
            did_update = try_update_slot(slot=I_i.slots[seg], p_new=p_new)


def try_update_bests(p_new, I_i):
    if p_new.has_subtours():
        return

    if p_best.delta_o > p_new.delta_o:
        p_best = p_new
    if I_i.p_1st.delta_o > p_new.delta_o:
        I_i.p_2nd = I_i.p_1st
        I_i.p_1st = p_new
    elif I_i.p_2nd.delta_o > p_new.delta_o:
        I_i.p_2nd = p_new


# returns T/F if there was an update to the slot
def try_update_slot(slot, p_new):

    if slot.p_1st is None:
        slot.p_1st = p_new
        return True

    did_update = False

    if p_new.delta_o < slot.p_1st.delta_o:
        slot.p_2nd = slot.p_1st
        slot.p_1st = p_new
        did_update = True
    elif slot.p_2nd.delta_o is None:
        slot.p_2nd = p_new
        for segment in p_new.segments.oedges:
            if segment not in slot.p_2nd_ties:
                slot.p_2nd_ties[segment] = p_new
        did_update = True
    elif p_new.delta_o < slot.p_2nd.delta_o:
        slot.p_2nd = p_new
        for segment in p_new.segments.oedges:
            if segment not in slot.p_2nd_ties:
                slot.p_2nd_ties[segment] = p_new
        did_update = True
    elif p_new.delta_o == slot.p_2nd.delta_o:
        for segment in p_new.segments.oedges:
            if segment not in slot.p_2nd_ties:
                slot.p_2nd_ties[segment] = p_new
        did_update = True

    return did_update


def add_orbits(I_i):
    I_i_2 = I_i.i - 2

    ps = []
    for slot in I_i_2.slots:
        ps.append(slot.p_1st)
        ps.extend(list(slot.p_2nd_ties))
    for p in ps:
        orbits = Orbit.get_or_create_orbits(p.edges_not_in_p):
        for orbit in orbits:
            p_new = p.add_orbit(orbit)
            for seg in p_new.segments.oedges:
                try_update_bests(p_new=p_new, I_i=I_i)
                did_update = try_update_slot(slot=I_i.slots[seg], p_new=p_new)

