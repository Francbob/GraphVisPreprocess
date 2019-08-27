# Graph Visualization Pre-processing

This project works as a preparation for various graph visualization algorithm.

## Input
See samples in  [./data/](https://github.com/Francbob/GraphVisPreprocess/tree/master/data).

```json
{
  "nodes": [
    {
      "id" : "node1"
    },
    {
      "id" : "node1"
    }
  ],
  "links": [
    {
      "source": "node1",
      "target": "node2" 
    }
  ]
}
```

## Output

### Hierarchical Clustering with Virtual Nodes

- Argument: `-m "hierarchy" -v -s "/Users/..."`
- Output Sample:
```json
{
  "nodes": [
    {
      "label": "BrighamYoung",
      "idx": 0,
      "virtual": false,
      "height": 0,
      "ancIdx": 115
    }
  ],
  "links": [
     {
       "sourceIdx": 81,
       "targetIdx": 82
     }
  ]
}
```