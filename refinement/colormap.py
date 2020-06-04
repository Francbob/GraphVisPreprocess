import seaborn as sns
import networkx as nx

COLOR_PALETTES = [
    'Greens',
    'Oranges',
    'Blues',
]


def vertex_ordering(graph):
    graph.graph['leafNode'] = []
    graph.graph['community'] = []
    dfs_label(graph.graph['rootIdx'], graph, 0)
    label_by_pub_year(graph)


def label_by_pub_year(graph):
    leaves = []
    for i in graph.nodes():
        node = graph.node[i]
        if node['height'] == 0:
            leaves.append(node)
    leaves.sort(key=lambda x:(x['year'], x['leaf_order']))
    for i in range(len(leaves)):
        leaves[i]['leaf_order'] = i


def dfs_label(root_idx, graph, order_idx):
    """
    Depth First Search
    :param root_idx: the DFS starting node
    :param graph: graph for searching
    :param order_idx: current leaf order index
    :return: order_idx, height, is leaf or not
    """
    node = graph.node[root_idx]

    # not a leaf
    if len(node['childIdx']) != 0:
        height = 0
        is_leaf = False
        for child_idx in node['childIdx']:
            order_idx, height, is_leaf = dfs_label(child_idx, graph, order_idx)

        # define the height for non-leaf node
        node['height'] = height + 1

        # define the communities in graph based on previous setting
        if is_leaf:
            graph.graph['community'].append(root_idx)

        return order_idx, height + 1, False
    else:
        # define the order for the leaf node
        node['leaf_order'] = order_idx
        node['height'] = 0
        graph.graph['leafNode'].append(root_idx)
        order_idx += 1

        return order_idx, 0, True


def get_vertex_color(graph, args):
    # Get color palette
    color_platte = []
    for color in COLOR_PALETTES:
        pl = sns.color_palette(color, 4).as_hex()
        color_platte.append(pl)

    vertex_ordering(graph)

    color_to_community = {}

    num_community = len(graph.graph['community'])
    num_color_platte = len(color_platte)

    for idx, community in enumerate(graph.graph['community']):
        c_idx = int((idx / num_community) * num_color_platte)
        if c_idx not in color_to_community.keys():
            color_to_community[c_idx] = []
        color_to_community[c_idx].append(community)

    community2color = {}
    for c_idx in color_to_community.keys():
        num_color = len(color_platte[c_idx])
        num_community = len(color_to_community[c_idx])
        for idx, community_idx in enumerate(color_to_community[c_idx]):
            color = color_platte[c_idx][int((idx / num_community) * num_color)]
            community2color[community_idx] = color

    for community_idx in community2color.keys():
        children = graph.node[community_idx]['childIdx']
        for child_idx in children:
            graph.node[child_idx]['color'] = community2color[community_idx]



