import igraph as ig
import numpy as np
import random

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

def compute_resource_utilization(g):
    raise NotImplementedError

def alter_structure(g, m):
    """
    We alter the graph structure to simulate creation of friendships and observe changes in B over time as a consequence.
    m = float, arbitrary fraction of nodes
    g = original graph 

    Naive implementation - generates num_nodes*num_nodes tuples and samples (m*num_nodes)/2 tuples randomly
                           no duplicates or self-loops

    """

    possible_friendships = [(i,j) for i in xrange(num_nodes) for j in xrange(i,num_nodes) if i != j]
    #g.add_Edges(random.sample(possible_friendships, (m*num_nodes)/2)) #doesn't work because this doesn't consider edges that are already in the graph
    edges = [(node.source, node.target) for node in g.es]
    counter = 0
    while counter < (m*num_nodes)/2:
        candidate_edge = random.choice(possible_friendships)
        if candidate_edge not in edges:
            counter += 1
            g.add_Edges([candidate_edge])

    return g




    raise NotImplementedError

def update(g):
    raise NotImplementedError

def run(g):
    raise NotImplementedError
