import argparse
import community
import networkx as nx
import sys
import json
import os.path

from networkx.readwrite import json_graph

# The number of nodes in the graph
NUM_REAL_NODES = 0


def save_graph(G, filepath, args):

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

    if not args.virtual:
        d['clusters'] = args.cluster_list

    print('Saving {}'.format(filepath))
    with open(filepath, 'w') as f:
        json.dump(d, f)


def hierarchical_cluster_with_vn(Graph, args, resolution=1):
    """
    Using Virtual Node Skill in this function
    :param Graph: Any graph
    :param args:
    :param resolution:
    :return:
    """
    for n in Graph.nodes_iter():
        Graph.node[n]['virtual'] = False
        Graph.node[n]['height'] = 0

    dendo = community.generate_dendrogram(Graph, resolution=resolution)

    num_last_level_nodes = 0
    for level, partition in enumerate(dendo):
        clusters = list(set(partition.values()))
        # number of nodes in current graph
        num_nodes = len(Graph.node)

        # Add virtual Nodes
        Graph.add_nodes_from([(num_nodes + idx, {
            'label': 'Node_'+str(idx),
            'childIdx': [],
            'virtual': True,
            'ancIdx': None,
            'idx': num_nodes + idx,
            'height': level + 1
        }) for idx in clusters])

        # Add the hierarchical structure to the Nodes
        for node_idx, cluster_idx in partition.items():
            Graph.node[node_idx + num_last_level_nodes]['ancIdx'] = cluster_idx + num_nodes
            Graph.node[cluster_idx + num_nodes]['childIdx'].append(node_idx + num_last_level_nodes)

        # The highest level, add a root
        if level == len(dendo) - 1:
            Graph.add_nodes_from([(len(Graph.node), {
                'label': 'Node_' + str(len(Graph.node)),
                'childIdx': [num_nodes + idx for idx in clusters],
                'virtual': True,
                'ancIdx': None,
                'idx': len(Graph.node),
                'height': level + 2
            })])
            for idx in clusters:
                Graph.node[idx + num_nodes]['ancIdx'] = len(Graph.node)-1

        num_last_level_nodes = num_nodes

    return Graph


def hierarchical_clustering(G, resolution=1):
    for n in G.nodes_iter():
        G.node[n]['ancIdxs'] = []

    # A dendrogram is a tree and each level is a partition of the graph nodes
    dendo = community.generate_dendrogram(G, resolution=resolution)

    num_levels = len(dendo)
    clusters_per_level = []
    for level in range(num_levels):
        partition = community.partition_at_level(dendo, level)
        clusters = list(set(partition.values()))
        clusters_per_level.append(clusters)
        print('clusters at level', level, 'are', clusters)
        for n, c in partition.items():
            G.node[n]['ancIdxs'].append(c)

    num_nodes = nx.number_of_nodes(G)

    def get_cluster_idx(level, idx):
        offset = num_nodes
        for i in range(level):
            offset += len(clusters_per_level[i])
        return offset + idx

    cluster_list = []
    for n in G.nodes_iter():
        node = G.node[n]
        node_clusters = node['ancIdxs']
        for level in range(len(node['ancIdxs'])):
            node_clusters[level] = get_cluster_idx(level, node_clusters[level])

        cluster_list.append({
            'idx': n,
            'nodeIdx': n,
            'parentIdx': node_clusters[0],
            'height': 0
        })

    for level, clusters in enumerate(clusters_per_level):
        for c in clusters:
            cluster_list.append({
                'idx': get_cluster_idx(level, c),
                'height': level + 1
            })

    for n in G.nodes_iter():
        node = G.node[n]
        node_clusters = node['ancIdxs']
        for level in range(len(node_clusters) - 1):
            cluster_list[node_clusters[level]]['parentIdx'] = node_clusters[
                level + 1]

    # Root
    root_cluster_idx = len(cluster_list)
    cluster_list.append({
        'idx': root_cluster_idx,
        'height': len(clusters_per_level) + 1
    })

    for c in clusters_per_level[-1]:
        cluster_list[get_cluster_idx(num_levels - 1, c)][
            'parentIdx'] = root_cluster_idx

    return cluster_list


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


def make_argparser():
    p = argparse.ArgumentParser()
    p.add_argument('filepath', type=str, help='input filepath')
    p.add_argument('-r', '--resolution', type=float,
                   help='resolution parameter for hierarchical clustering', default=1.0)
    p.add_argument('-m', '--method', type=str, default='hierarchy', help="The pre-processing method")
    p.add_argument('-v', '--virtual', type=bool, default=True, help="Using virtual nodes")
    p.add_argument('--cluster_list', type=list, default=[])
    p.add_argument('-s', '--save', type=str, default='/Users/francbob/Projects/GraphVisPreprocess/result/')
    return p


def main():
    argparser = make_argparser()

    if len(sys.argv) == 1:
        argparser.print_help()
        return

    args = argparser.parse_args()

    if '.json' in args.filepath:
        G = parse_json_d3(args.filepath)
    else:
        argparser.print_help()
        return

    if args.method == 'hierarchy' and args.virtual:
        G = hierarchical_cluster_with_vn(G, args)
    else:
        cluster_list = hierarchical_clustering(G, resolution=args.resolution)

    basename = os.path.basename(args.filepath)
    filename = os.path.splitext(basename)[0]


    save_graph(G,
               args.save + '{}'.format(filename + '.vidi.json'), args)


if __name__ == '__main__':
    main()
