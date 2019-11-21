import networkx as nx
import argparse
import json
import re

def parse_walrus_graph(filepath):
    print('Reading {}'.format(filepath))
    state = None
    G = nx.Graph()
    edges = []

    with open(filepath) as f:
        lines = f.readlines()
        for line in lines:
            if line == '\'links\': [\n':
                state = 'links'
                continue
            if line == '\'treelinks\':[\n':
                state = 'tree'
                continue
            if state == 'links':
                if line == ']\n':
                    continue

                nodes = re.findall(r'[0-9]+', line)
                G.add_edge(int(nodes[0]), int(nodes[1]), tree=False, parent=None)
                edges.append([int(nodes[0]), int(nodes[1])])

            elif state == 'tree':
                if line == ']':
                    continue

                edgeIdx = int(re.findall(r'[0-9]+', line)[0])
                G[edges[edgeIdx][0]][edges[edgeIdx][1]]['tree'] = True
                G[edges[edgeIdx][0]][edges[edgeIdx][1]]['parent'] = edges[edgeIdx][0]
                continue

    # TODO return rootIdx and Graph
    return 0, G


def parse_from_gml(filepath):
    print('Reading {}'.format(filepath))

    G = nx.read_gml(filepath, label='id')
    for n in G.nodes_iter():
        G.node[n]['idx'] = n
        G.node[n]['label'] = 'node_' + str(n)

    return G


def parse_pickle(obj):
    G = nx.Graph()
    # n_idx = {node['id']: idx for idx, node in enumerate(obj['nodes'])}
    # G.add_nodes_from([(idx, {'label': label, 'idx': idx}) for label, idx in n_idx.items()])
    G.add_nodes_from([(node['idx'], {'label': node['label'], 'idx': node['idx']}) for idx, node in enumerate(obj['nodes'])])

    G.add_edges_from([(e['sourceIdx'], e['targetIdx'])
                      for e in obj['links']])

    return G


def parse_json_nature(filepath):
    print('Reading {}'.format(filepath))
    G = nx.Graph()

    with open(filepath) as f:
        d = json.load(f)

    n_idx = {node['id']: {'idx': idx, 'title': node['title'], 'size': node['size'], 'year': node['pubYear']}
             for idx, node in enumerate(d['nodes'])}
    G.add_nodes_from([(node['idx'],
                       {'label': node['title'], 'idx': node['idx'], 'size': node['size'], 'year': node['year']})
                      for label, node in n_idx.items()])
    G.add_edges_from([(n_idx[e['source']]['idx'], n_idx[e['target']]['idx'])
                      for e in d['links']])

    return G


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


