import json
import networkx as nx
import argparse
import os
from refinement.colormap import get_vertex_color
from networkx.readwrite import json_graph
from refinement.aggregation import get_links_by_levels


def open_json_file(filepath):
    print('Reading {}'.format(filepath))

    G = nx.Graph()

    with open(filepath) as f:
        d = json.load(f)

    G.add_nodes_from([
        (node['idx'], {
            'virtualNode': node['virtualNode'],
            'height': node['height'],
            'idx': node['idx'],
            'label': node['label'],
            'ancIdx': None if 'ancIdx' not in node else node['ancIdx'],
            'childIdx': [] if 'childIdx' not in node else node['childIdx']
        }) for node in d["nodes"]
    ])

    G.add_edges_from([(e['sourceIdx'], e['targetIdx'])
                      for e in d['links']])

    G.graph['rootIdx'] = d['rootIdx']

    return G


def save_graph(G, filepath, level_links):
    d = json_graph.node_link_data(
        G,
        attrs={
            'source': 'sourceIdx',
            'target': 'targetIdx',
            'key': 'key',
            'id': 'idx'
        })

    del d['directed']
    del d['multigraph']
    del d['graph']

    d['rootIdx'] = G.graph['rootIdx']
    d['levelLinks'] = level_links;

    print('Saving {}'.format(filepath))
    with open(filepath, 'w') as f:
        json.dump(d, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filepath', type=str, help='the filepath of the vidi.json graph definition file')
    parser.add_argument('-s', '--save', type=str, help='the path to save the data', default='/Users/francbob/Desktop/UC '
                                                     'Davis/Project/ViDiImmersiveH3Layout/Assets/StreamingAssets/')
    args = parser.parse_args()
    graph = open_json_file(args.filepath)
    get_vertex_color(graph, args)
    level_links = get_links_by_levels(graph)

    basename = os.path.basename(args.filepath)
    filename = os.path.splitext(basename)[0]

    save_graph(graph, args.save + '{}'.format(filename + '_r.json'), level_links)

