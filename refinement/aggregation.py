import networkx as nx

# aggregate links in different levels
def get_links_by_levels(graph):
    abstract_adj = {}
    level_links = {}

    print(len(graph.edges()))

    hierarchy = {}
    for n in graph.nodes():
        h = graph.node[n]['height']
        if h not in hierarchy:
            hierarchy[h] = []
            level_links[h] = []
        hierarchy[h].append(n)

    # for real nodes
    for nodeIdx in hierarchy[0]:
        adj_nodes = graph.adj[nodeIdx]
        parent = graph.node[nodeIdx]['ancIdx']

        if parent not in abstract_adj:
            abstract_adj[parent] = {}

        for neighbor in adj_nodes:
            neighbor_parent = graph.node[neighbor]['ancIdx']
            if parent == neighbor_parent:
                continue

            if neighbor_parent not in abstract_adj:
                abstract_adj[neighbor_parent] = {}

            if neighbor_parent not in abstract_adj[parent]:
                abstract_adj[parent][neighbor_parent] = {'weight': 0}
                abstract_adj[neighbor_parent][parent] = {'weight': 0}

            abstract_adj[parent][neighbor_parent]['weight'] += 1
            # abstract_links[neighbor_parent][parent]['weight'] += 1

    for level in range(1, len(hierarchy)-1):
        for nodeIdx in hierarchy[level]:
            parent = graph.node[nodeIdx]['ancIdx']

            if parent not in abstract_adj:
                abstract_adj[parent] = {}

            for neighbor in abstract_adj[nodeIdx].keys():
                neighbor_parent = graph.node[neighbor]['ancIdx']
                if parent == neighbor_parent:
                    continue
                if neighbor_parent not in abstract_adj:
                    abstract_adj[neighbor_parent] = {}

                if neighbor_parent not in abstract_adj[parent]:
                    abstract_adj[parent][neighbor_parent] = {'weight': 0}
                    abstract_adj[neighbor_parent][parent] = {'weight': 0}

                abstract_adj[parent][neighbor_parent]['weight'] += abstract_adj[nodeIdx][neighbor]['weight']
                # abstract_links[neighbor_parent][parent]['weight'] += abstract_links[nodeIdx][neighbor]['weight'];

    keys = list(abstract_adj.keys())

    for i in range(0, len(keys) - 1):
        nodeA = keys[i]
        h = graph.node[nodeA]['height']
        for j in range(i, len(keys) - 1):

            nodeB = keys[j]
            if nodeB in list(abstract_adj[nodeA].keys()):
                level_links[h].append({
                    'source': nodeA,
                    'target': nodeB,
                    'weight': abstract_adj[nodeA][nodeB]['weight']
                })

    for e in graph.edges():
        level_links[0].append({
            'source': e[0],
            'target': e[1],
            'weight': 1
        })

    return level_links