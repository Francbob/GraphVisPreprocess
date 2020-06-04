import networkx as nx

# aggregate links in different levels
def get_links_by_levels(graph):
    abstract_adj = {}
    level_links = {}
    links_in_node = {}

    print(len(graph.edges()))

    hierarchy = {}
    visit_link = {}
    for n in graph.nodes():
        h = graph.node[n]['height']
        if h > 0:
            links_in_node[n] = []
        if h not in hierarchy:
            hierarchy[h] = []
            level_links[h] = []
        hierarchy[h].append(n)
        visit_link[n] = []

    # for real nodes
    for nodeIdx in hierarchy[0]:
        adj_nodes = graph.adj[nodeIdx]
        parent = graph.node[nodeIdx]['ancIdx']

        if parent not in abstract_adj:
            abstract_adj[parent] = {}

        for neighbor in adj_nodes:
            if nodeIdx not in visit_link[neighbor]:
                visit_link[nodeIdx].append(neighbor)
            else:
                continue

            neighbor_parent = graph.node[neighbor]['ancIdx']
            if parent == neighbor_parent:
                # The inner links
                if parent not in links_in_node:
                    print("h")
                links_in_node[parent].append({
                    'source': nodeIdx,
                    'target': neighbor,
                    'value': 1
                })
                continue

            if neighbor_parent not in abstract_adj:
                abstract_adj[neighbor_parent] = {}

            if neighbor_parent not in abstract_adj[parent]:
                abstract_adj[parent][neighbor_parent] = {'weight': 0}

            abstract_adj[parent][neighbor_parent]['weight'] += 1
            # abstract_links[neighbor_parent][parent]['weight'] += 1


    for level in range(1, len(hierarchy)-1):
        for nodeIdx in hierarchy[level]:
            parent = graph.node[nodeIdx]['ancIdx']
            visit_link[nodeIdx] = []

            if parent not in abstract_adj:
                abstract_adj[parent] = {}

            for neighbor in abstract_adj[nodeIdx].keys():
                if nodeIdx not in visit_link[neighbor]:
                    visit_link[nodeIdx].append(neighbor)
                else:
                    continue

                neighbor_parent = graph.node[neighbor]['ancIdx']
                if parent == neighbor_parent:
                    links_in_node[parent].append({
                        'source': nodeIdx,
                        'target': neighbor,
                        'value': abstract_adj[nodeIdx][neighbor]['weight']
                    })
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

    return hierarchy, links_in_node