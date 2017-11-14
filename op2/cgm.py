import igraph as ig
import numpy as np
from collections import defaultdict
import random

def get_sample(xk, pk):
    return np.random.choice(xk, p=pk)

def get_cgm_graph(n, m, p_new, p_in, p_vc, xk, pk, er_n=20, er_m=4):
    """generate graph with n new nodes. each node joins the network and forms m edges."""

    # assertions
    p_out = 1-p_new-p_in

    assert 0 <= p_out <= 1
    assert 0 <= p_new <= 1
    assert 0 <= p_new <= 1
    assert p_new + p_in + p_out == 1.

    xk, pk = map(np.array, [xk, pk])
    pk = pk/np.sum(pk)

    # initial graph
    gpre = ig.Graph.Erdos_Renyi(n=er_n, m=er_m*er_n)

    # mechanisms
    mech_xk, mech_pk = map(np.array, [['vc', 'tc', 'un'], [p_new, p_in, p_out]])

    # setup
    nodes_rem = n
    nid_attr_map = {}
    node_idx = len(gpre.vs)
    attr_nids_map = defaultdict(list)
    neighbors = defaultdict(list)

    edges = [(e.source,e.target) for e in gpre.es]

    for nid in gpre.vs.indices:
        nid_attr_map[nid] = get_sample(xk, pk)
        attr_nids_map[nid_attr_map[nid]].append(nid)

    for node in gpre.vs:
        neighbors[node.index] = [nbor.index for nbor in node.neighbors()]

    # gen
    while nodes_rem != 0:
        mech = get_sample(mech_xk, mech_pk)
        new_edges = []

        if mech == 'vc':
            attr_val = get_sample(xk, pk)
            nid_attr_map[node_idx] = attr_val
            attr_nids_map[attr_val].append(node_idx)

            for _ in range(m):
                found = False
                while not found:
                    enid = np.random.randint(0, len(neighbors)-1)
                    if nid_attr_map[enid] == attr_val: found = True
                if random.random() > p_vc: enid = np.random.choice(neighbors[enid])
                new_edges.append((node_idx, enid))
                neighbors[node_idx].append(enid)
                neighbors[enid].append(node_idx)

            nodes_rem -= 1
            node_idx += 1


        elif mech == 'tc':
            enid = np.random.randint(0, len(neighbors)-1)
            n1, n2 = np.random.choice(neighbors[enid], size=2)
            new_edges.append((n1,n2))

        else: # un
            n1,n2 = np.random.randint(0, len(neighbors)-1, size=2)
            new_edges.append((n1,n2))

        edges.extend(new_edges)

    # build
    g = gpre.copy()
    g.add_vertices(n+len(gpre.vs))
    g.add_edges(edges)
    g.vs['attr'] = [nid_attr_map[nid] for nid in range(len(nid_attr_map))]
    g = g.simplify()
    return g

if __name__ == '__main__':
    g = get_cgm_graph(1000, 5, 0.7, 0.2, 0.1, [0,1], [0.5,0.5])
    print (g.summary())








