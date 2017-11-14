import igraph as ig
import numpy as np
import itertools as it
import random
from collections import defaultdict

W = 0

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
    g.vs['r_copy'] = [_ for _ in g.vs['r']]
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
    while len(tba) < total: tba.append(random.choice(new_edges))
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
        size = min(len(posts), node['num_read'])
        return np.random.choice(posts, size=size, replace=False) if posts else []

    # select candidates
    adopted = node['behaviors']
    can_adopt = set(behavior_cost.keys()) - adopted
    candidates = []
    final = []

    nborhood = get_observed_nborhood()
    if len(nborhood) == 0: return set()

    const = 1./len(nborhood)
    behavior_signals = defaultdict(float)

    for nbor in nborhood:
        for behavior in nbor['behaviors']:
            behavior_signals[behavior] += const

    for behavior, signal in behavior_signals.items():
        score = behavior_util[behavior]*W + signal*(1.-W)
        if score > node['theta']: candidates.append(behavior)

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
        adopted_behaviors.extend(list(new_behavior_set[node]))

    for node, new_behaviors in new_behavior_set.items():
        node['behaviors'] = node['behaviors'].union(new_behaviors)

    return new_behavior_set, adopted_behaviors

def compute_resource_utilization(g, behavior_cost):
    costs, resources = 0., np.sum(g.vs['r_copy'])
    for node in g.vs: costs += sum(behavior_cost[b] for b in node['behaviors'])
    return costs/resources

def update_seed_nodes(g, behaviors,seeds=None):
    if seeds is not None:
        num_seeds = int(round(np.log2(len(g.vs))))
        for _ in xrange(num_seeds):
            node = random.choice(g.vs)
            node['behaviors'].add(random.choice(behaviors))
        return g
    else:
        for s in seeds: g.vs[s]['behaviors'].add(random.choice(behaviors))
        return g

def run(g, lambda_read, lambda_post, num_behaviors=3, c=0., max_iter=None,seeds=None):
    num_nodes = len(g.vs)
    behavior_cost, behavior_util = get_behaviors(num_behaviors)
    g = initialize_graph(g.copy(), lambda_read, lambda_post)
    g = alter_structure(g, c=c)
    g = update_seed_nodes(g, list(behavior_cost.keys()), seeds=seeds)

    max_iter = max_iter or np.inf
    at_equilibrium = False
    it = 0

    while not at_equilibrium and it <= max_iter:
        new_behavior_set, adopted_behaviors = update(g, behavior_cost, behavior_util)
        at_equilibrium = adopted_behaviors == []
        it += 1
        g.vs['num_post'] = np.random.poisson(lambda_post, size=num_nodes)
        g.vs['num_read'] = np.random.poisson(lambda_read, size=num_nodes)

    B = compute_resource_utilization(g, behavior_cost)
    return B, g











