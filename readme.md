# python-tsp

## A python implementation of Dijkstra's shortest path algorithm.

- Find the shortest path on a node graph.

#### Install dependencies

First navigate to a directory where you want to download it to...

```
git clone https://github.com/lewis-morris/pydiijkstras
cd pydiijkstras
pip install -r requirements.txt

```

#### Run Code


Basic:

In download directory 

```
python run.py
```

Advanced:

```

optional arguments:
  -h, --help       show this help message and exit
  --width WIDTH    Width of the 'map' in pixels
  --height HEIGHT  Height of the 'map' in pixels

```

i.e 
```
python run.py --height 400 --width 400
```

#### How to use

![example board](https://i.imgur.com/R8hch4c.png)

Once open you will see the completed, randomly generated node graph and the quickest route from A to B.

![Toolbar](https://i.imgur.com/4KQ2spA.png)

Using the above toolbar and node slider you can interact with the nodes.

- **Refresh** - refreshes a completely new configuration of nodes and edges (nodes amount is pulled from the node slider)

- **Change Start Node** - Click any node to set as the start point 

- **Change End Node** - Click any node to set as the end point

- **Draw New Nodes** - click on the map to add new nodes

- **Clear Nodes** - Clears all nodes

- **Clear Edges** - Clears all edges

- **Reload Edges** - Regenerates new edges for each node.

- **Quit** - Quit the program.