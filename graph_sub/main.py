import graph_tool.all as gt
import json
import pickle
import argparse


def export_dataset(name, args):
    g = gt.collection.data[name]

    json_file = hierarchy_partition(g, args)
    f = open('/Users/francbob/Projects/GraphVisPreprocess/graph_sub/data', 'wb')
    pickle.dump(json_file, f)
    f.close()
    return g

def get_hierarchy_gt(graph, graph_json, state):
    # Get the partition from blocks
    levels = state.get_levels()
    level_num = len(levels)
    vertex_num = len(graph.get_vertices())
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



def get_hierarchy_hand(graph, graph_json, state):
    for v in graph.get_vertices():
        assert v == len(graph_json['nodes'])
        graph_json['nodes'].append({
            'label': 'node_' + str(v),
            'idx': int(v),
            'virtualNode': False,
            'height': 0,
            'ancIdx': None
        })
    # Get the partition from blocks
    levels = state.get_levels()
    level_num = len(levels)
    vertex_num = len(graph.get_vertices())
    partition = {}
    virtual_node_list = set()
    level_block_count = []
    for level in range(0, level_num):
        level_block_count.append(levels[level].B)


    for vertex in graph.get_vertices():
        for level in range(0, level_num):
            r = levels[level].get_blocks()[vertex]
            idx = vertex_num + r + sum(level_block_count[:level])
            virtual_node_list.add(idx)
            if partition.get(idx) is None:
                partition[idx] = {}
                partition[idx]['child'] = []
                partition[idx]['layer'] = int(level)

            partition[idx]['child'].append(int(vertex))

    virtual_node_list = sorted(list(virtual_node_list))
    # add the block to the graph_json
    for key in virtual_node_list:
        assert len(graph_json['nodes']) == key
        value = partition[key]
        graph_json['nodes'].append({
            'label': 'node_' + str(key),
            'idx': int(key),
            'virtualNode': True,
            'height': value['layer'] + 1,
            'ancIdx': None,
            'childIdx': []
        })
        if value['layer'] == 0:
            graph_json['nodes'][key]['childIdx'] = value['child']
            for childIdx in value['child']:
                graph_json['nodes'][childIdx]['ancIdx'] = int(key)
        else:
            child_set = set()
            for childIdx in value['child']:
                idx = graph_json['nodes'][childIdx]['ancIdx']
                while graph_json['nodes'][idx]['height'] < value['layer']:
                    idx = graph_json['nodes'][idx]['ancIdx']
                child_set.add(idx)

            graph_json['nodes'][key]['childIdx'] = list(child_set)
            for childIdx in graph_json['nodes'][key]['childIdx']:
                graph_json['nodes'][childIdx]['ancIdx'] = int(key)

    graph_json['rootIdx'] = len(graph_json['nodes']) - 1
    for i in range(len(graph_json['nodes']) - 1):
        if graph_json['nodes'][i]['ancIdx'] is None:
            graph_json['nodes'][i]['ancIdx'] = graph_json['rootIdx']

    return graph_json

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

    get_hierarchy_gt(graph, graph_json, state)

    return graph_json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='celegansneural')
    parser.add_argument('-v', '--verbose', default=False)
    args = parser.parse_args()

    print(export_dataset(args.dataset, args))

