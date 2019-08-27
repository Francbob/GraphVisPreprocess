import graph_tool.all as gt
import json
import pickle


def export_dataset(name, filepath):
    g = gt.collection.data[name]

    json_file = hierarchy_partition(g)
    f = open('./data', 'wb')
    pickle.dump(json_file, f)
    # json.dump(f, json_file)

    # for e in g.edges():
    #     f.write(str(int(e.source())) + ' ' + str(int(e.target())) + '\n')
    f.close()
    return g


def hierarchy_partition(graph):
    graph_json = {}
    graph_json['nodes'] = []
    graph_json['links'] = []

    # form the json file
    for e in graph.edges():
        graph_json['links'].append({
            'sourceIdx': int(e.source()),
            'targetIdx': int(e.target())
        })

    for v in graph.get_vertices():
        assert v == len(graph_json['nodes'])
        graph_json['nodes'].append({
            'label': 'node_' + str(v),
            'idx': int(v),
            'virtualNode': False,
            'height': 0,
            'ancIdx': None
        })

    vertex_num = len(graph.get_vertices())
    # find the latent hierarchical tree structure
    state = gt.minimize_nested_blockmodel_dl(graph, verbose=True)
    levels = state.get_levels()
    level_num = len(levels)

    level_block_count = []
    for level in range(0, level_num):
        level_block_count.append(levels[level].B)

    # Get the partition from blocks
    partition = {}
    virtual_node_list = set()
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

    graph_json['rootIdx'] = len(graph_json['nodes'])-1
    for i in range(len(graph_json['nodes']) - 1):
        if graph_json['nodes'][i]['ancIdx'] is None:
            graph_json['nodes'][i]['ancIdx'] = graph_json['rootIdx']

    return graph_json


if __name__ == '__main__':
    print(export_dataset('celegansneural', '/Users/francbob/Projects/GraphVisPreprocess/data/node2node_data/data.txt'))

