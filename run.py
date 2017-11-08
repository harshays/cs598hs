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

def alter_structure(g):
    raise NotImplementedError

def update(g):
    raise NotImplementedError

def run(g):
    raise NotImplementedError
