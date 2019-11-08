import graph_tool.all as gt
import json
import pickle
import argparse
import networkx
import community


def export_dataset(name, args):
    g = None
    if args.konect:
        g = gt.collection.konect_data[name]
    else:
        g = gt.collection.data[name]

    json_file = hierarchy_partition(g, args)
    f = open('/Users/francbob/Projects/GraphVisPreprocess/graph_sub/data', 'wb')
    pickle.dump(json_file, f)
    f.close()
    return g


def get_hierarchy_gt(graph_json, state):
    # Get the partition from blocks
    levels = state.get_levels()
    level_num = len(levels)
    level_block_count = []
    for level in range(0, level_num):
        level_block_count.append(levels[level].B)

    level = 0
    tree, label, order = gt.get_hierarchy_tree(state)
    for v_idx in tree.get_vertices():
        v = tree.vertex(v_idx)
        label_v = label[v]
        # A new level
        if v_idx != 0 and label_v == 0:
            level += 1

        assert v_idx == len(graph_json['nodes'])
        node = {
            'label': 'node_' + str(v_idx),
            'idx': int(v_idx),
            'height': level,
            'ancIdx': None,
            'childIdx': []
        }
        # Virtual Node
        if level == 0:
            node['virtualNode'] = False
        else:
            node['virtualNode'] = True
        # Hierarchy
        if level != 0:
            for vertex in v.out_neighbors():
                node['childIdx'].append(int(vertex))
                graph_json['nodes'][int(vertex)]['ancIdx'] = int(v_idx)

        graph_json['nodes'].append(node)

    graph_json['rootIdx'] = len(graph_json['nodes']) - 1

def hierarchy_partition(graph, args):
    graph_json = {}
    graph_json['nodes'] = []
    graph_json['links'] = []

    # form the json file
    for e in graph.edges():
        graph_json['links'].append({
            'sourceIdx': int(e.source()),
            'targetIdx': int(e.target())
        })

    # find the latent hierarchical tree structure
    state = gt.minimize_nested_blockmodel_dl(graph, verbose=args.verbose)

    get_hierarchy_gt(graph_json, state)

    return graph_json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='celegansneural')
    parser.add_argument('-v', '--verbose', default=False)
    parser.add_argument('-k', '--konect', default=False)

    args = parser.parse_args()

    print(export_dataset(args.dataset, args))

