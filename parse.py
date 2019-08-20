import networkx as nx
import argparse
import json


def parse_json_d3(filepath):
    print('Reading {}'.format(filepath))

    G = nx.Graph()

    with open(filepath) as f:
        d = json.load(f)

    n_idx = {node['id']: idx for idx, node in enumerate(d['nodes'])}
    # Set the number of nodes of current graph
    NUM_REAL_NODES = len(n_idx)

    G.add_nodes_from([(idx, {'label': label, 'idx': idx}) for label, idx in n_idx.items()])

    G.add_edges_from([(n_idx[e['source']], n_idx[e['target']])
                      for e in d['links']])

    return G


def parse_node2node(args):
    print('Read from {}'.format(args.filepath))
    graph = nx.Graph()
    node_limit = args.nodenumber

    with open(args.filepath) as file:
        lines = file.readlines()
        node_set = set()
        link_set = []

        for line in lines:
            link = [int(n) for n in line.split()]
            source = link[0]
            end = link[1]

            # avoid circle
            if node_limit >= source and end <= node_limit:
                if source != end:
                    link_set.append(link)
                    node_set.add(source)
                    node_set.add(end)
                else:
                    node_set.add(source)

        graph.add_nodes_from([(nodeIdx, {'label': 'node_' + str(nodeIdx), 'idx': nodeIdx}) for nodeIdx in node_set])
        graph.add_edges_from([(link[0], link[1]) for link in link_set])

    return graph


if __name__ == '__main__' :
    argparser = argparse.ArgumentParser()
    argparser.add_argument('filepath', type=str, help='input filepath')

    args = argparser.parse_args()

    g = parse_node2node(args)

    print(g.size())


