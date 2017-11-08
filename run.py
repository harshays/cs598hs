import igraph as ig
import numpy as np
import itertools as it
import random
from collections import defaultdict

W = 0.1

def get_behaviors(n, equal_cost_utility=False):
    """return map of n behaviors b_i with cost c_i and utility u_i"""
    behavior_cost = {idx:np.random.uniform() for idx in range(n)}
    behavior_util = behavior_cost.copy() if equal_cost_utility else {idx:np.random.uniform() for idx in range(n)}
    return behavior_cost, behavior_util

def initialize_graph(g, lambda_read, lambda_post):
    """
    resource constraints r_i ~ U(0,1)
    threshold theta_i ~ U(0,1)
    number of posts posted ~ Poi(lambda_post)
    number of posts read ~ Poi(lambda_read)
    """
    num_nodes = len(g.vs)
    g.vs['r'] = np.random.uniform(size=num_nodes)
    g.vs['theta'] = np.random.uniform(size=num_nodes)
    g.vs['num_post'] = np.random.poisson(lambda_post, size=num_nodes)
    g.vs['num_read'] = np.random.poisson(lambda_read, size=num_nodes)
    g.vs['behaviors'] = [set() for _ in xrange(num_nodes)]
    return g

def alter_structure(g, c):
    """
    We alter the graph structure to simulate creation of friendships and observe changes in B over time as a consequence.
    c = float, arbitrary fraction of edges
    g = original graph
    Naive implementation - generates num_nodes*num_nodes tuples and samples
    (m*num_nodes)/2 tuples randomly no duplicates or self-loops
    """
    num_nodes = len(g.vs)
    edges = set([(node.source, node.target) for node in g.es])

    new_edges = [(i,j) for i,j in it.combinations(range(num_nodes), 2)
                 if (i,j) not in edges and (j,i) not in edges]

    total, tba = int(round(c*len(g.es))), []
    while len(tba) < tba: total.append(random.choice(new_edges))
    g.add_edges(tba)
    return g

def update_node(node, behavior_cost, behavior_util):
    """
    returns set of new behaviors adopted by node
    1. select candidates based on social signal + behavior utility
    2. select behavior based on resource constraints + behavior cost
    """
    def get_observed_nborhood():
        posts = []
        for nbor in node.neighbors(): posts.extend([nbor]*nbor['num_post'])
        return np.random.choice(posts, size=node['num_read'], replace=False)

    # select candidates
    adopted = node['behaviors']
    can_adopt = set(behavior_cost.keys()) - adopted
    candidates = []
    final = []

    nborhood = get_observed_nborhood()
    const = 1./len(nborhood)
    behavior_signals = defaultdict(float)

    for nbor in nborhood:
        for behavior in nbor['behaviors']:
            behavior_signals[behavior] += const

    for behavior, signal in behavior_signals.items():
        score = behavior_util[behavior]*W + signal*(1.-W)
        if score > node['threshold']: candidates.append(behavior)

    # select final
    candidates = sorted(candidates, key=lambda b: behavior_util[b])

    for behavior in candidates:
        if behavior_cost[behavior] <= node['r']:
            node['r'] -= behavior_cost[behavior]
            final.append(behavior)

    return set(final)

def update(g, behavior_cost, behavior_util):
    adopted_behaviors = []
    new_behavior_set = {}
    for node in g.vs:
        new_behavior_set[node] = update_node(node, behavior_cost, behavior_util)
        adopted_behaviors.append(new_behavior_set[node])

    for node, new_behaviors in new_behavior_set.items():
        g.vs[node]['behaviors'] = g.vs[node]['behaviors'] + new_behaviors

    return new_behavior_set, adopted_behaviors

def compute_resource_utilization(g, behavior_cost):
    costs, resources = 0., np.sum(g.vs['r'])
    for node in g.vs: costs += sum(behavior_cost[b] for b in node['behaviors'])
    return costs/resources

def run(g, num_behaviors=3, c=0., max_iter=None):
    behavior_cost, behavior_util = get_behaviors(num_behaviors)
    g = initialize_graph(g.copy())
    g = alter_structure(g, c=c)

    max_iter = max_iter or np.inf
    at_equilibrium = False
    it = 0

    while not at_equilibrium or it >= max_iter:
        new_behavior_set, adopted_behaviors = update(g)
        at_equilibrium = adopted_behavior == []
        it += 1

    B = compute_resource_utilization()
    return B, g











