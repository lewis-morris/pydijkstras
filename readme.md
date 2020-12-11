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
  -h, --help            show this help message and exit
  -w Witht, --cities CITIES
                        This is the amount of 'cities' to add to the map or
                        the hardness of the calculation
  -w WORKERS, --workers WORKERS
                        The amount of workers per family generation
  -f FAMILIES, --families FAMILIES
                        The amount of families per generation
  -b BREED, --breed BREED
                        Generation number to breed between families on ... i.e
                        every n times
  -r RANDOM, --random RANDOM
                        Draw the cities randomly on the map or equally spaced.
                        0= equally (draws a perfect polygon of n sides, which
                        is easy to determine when complete) 1= randomly
                        (points are randomly selected in the 'map' space)
  -d DRAW, --draw DRAW  Draw the output onscreen. 0= no 1= yes

```

i.e 
```
python run.py -c 50 -w 100 -f 10 -b 30 -r 1 -d 10
```