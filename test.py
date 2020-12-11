import itertools
from dataclasses import dataclass
import cv2
import math
import random
import numpy as np
from queue import PriorityQueue
from shapely.geometry import Polygon, Point
import sys
import heapq as h
import itertools
import random
import PySimpleGUI as sg


class PriQ:
    """ Amended example from python docs"""

    def __init__(self):
        self.pq = []  # list of entries arranged in a heap
        self.entry_finder = {}  # mapping of tasks to entries
        self.REMOVED = '<removed-task>'  # placeholder for a removed task
        self.counter = itertools.count()  # unique sequence count

    def empty(self):
        return len([x for x in self.pq if x[2] != self.REMOVED]) == 0

    def put(self, task, priority=0):
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [task.weight, count, task]
        self.entry_finder[task] = entry
        h.heappush(self.pq, entry)

    def remove_task(self, task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = h.heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')


class Node:
    """ holds the city coords etc """

    def __init__(self, maps, ident, pos=None):

        self.ident = ident

        # while maps.node_intersects_any(self):
        #     self.setup(maps)
        if pos:
            self.x, self.y = pos
        else:
            self.x = self.y = None

        self.setup(maps)

        # get distance dict
        self.distances = {}
        # current weight
        self.weight = sys.maxsize
        # passed through
        self.via = None
        # position
        self.position = None
        self.queued = False
        self.queued_com = False

    def setup(self, maps):
        """
        Takes map object as input and randomly creates objects
        """
        # x position
        if not self.y:
            self.y = random.randint(0 + int(maps.w * 0.05), maps.w - int(maps.w * 0.05))
        # y position
        if not self.x:
            self.x = random.randint(0 + int(maps.h * 0.05), maps.h - int(maps.h * 0.05))
        # list of connected nodes
        self.connected = []
        # shapely point
        self.point = Point((self.y, self.x))
        # current radius - used for finding nearby points
        self.radius = int(maps.w * 0.008)
        # radius polygon for above
        self.set_radius_poly()

    def set_radius_poly(self):
        """Set the polygon for this object"""
        self.poly = self.point.buffer(self.radius)

    def get_colour_size(self):
        """
        Used to get colour of the shape for drawing
        :return:
        """
        if self.position == "start":
            return (227, 71, 255), 0.006
        elif self.position == "end":
            return (71, 191, 255), 0.006
        if self.queued:
            return (171, 203, 224), 0.004
        return (145, 145, 145), 0.004

    def get_distance_to_node(self, node):
        """
        Get the distance from self to input node
        """
        return math.hypot(node.x - self.x, node.y - self.y)

    def get_position(self):
        # return current position
        return self.y, self.x

    def add_join(self, node):

        self.connected.append(node)


class Map:
    """
    hold the map details
    """

    def __init__(self, h, w, nodes=None, connections=(1, 4)):
        self.h = h
        self.w = w
        self.connections = connections
        # number of cities
        self.no_nodes = nodes
        # cities list
        self.nodes = []
        # create cities, randomly if no points are passed
        for node in range(self.no_nodes):
            # create node
            self.nodes.append(Node(self, node))

        # init the closest points
        self.init_random_edges()

        # set the start and end point
        self.set_start_end()

        # load the board
        self.board = np.ones((self.h, self.w, 3), dtype=np.uint8) * 255
        self.board_drawn = None
        self.route = []

    def node_intersects_any(self, test_node):
        """Used to check for click action on nodes"""
        for node in self.nodes:
            if node.radius_poly.intersects(test_node.radius_poly):
                return True
        return False

    def get_set_clicked(self, pos, position):
        """use for getting and setting the start and end position"""
        point = Point(pos)
        for node in self.nodes:
            if node.poly.contains(point):
                self.clear_position(position)
                node.position = position
                if "start" in position:
                    self.has_start = True
                    node.weight = 0
                elif "end" in position:
                    self.has_end = True

                return True

    def clear_position(self, position):
        """used to clear to start and end position"""
        for node in self.nodes:
            if node.position == position:
                node.position = None
                return

    def clear_nodes(self):
        """clear all nodes"""
        self.has_start = self.has_end = False
        self.nodes = []

    def start_node_zero_weight(self):

        start = [x for x in self.nodes if x.position == "start"]
        if start != []:
            start[0].weight = 0

    def clear_other(self, queued=False, edges=False, weight=False, via=False):
        """ Clear node parameters"""
        for node in self.nodes:
            if edges:
                node.connected = []
            if queued:
                node.queued = False
                node.queued_com = False
            if weight:
                node.weight = sys.maxsize
            if via:
                node.via = None

    def init_random_edges(self):
        """
        Create all edges to nodes in an semi random fashion
        :param connections:
        :return:
        """

        # clear nodes connections
        self.clear_other(edges=True)

        # loop every node
        for node in self.nodes:
            # loop every subnode if not node
            for sub_node in self.nodes:
                if sub_node != node:
                    # add distance to dictionary
                    node.distances[sub_node] = node.get_distance_to_node(sub_node)

            no_connected = random.randint(*self.connections)*2

            i = 0
            sorted_nodes = sorted(node.distances.items(), key=lambda x: x[1])
            # sorted_nodes = sorted_nodes[:int(no_connected*2)]
            # random.shuffle(sorted_nodes)
            # sorted_nodes = sorted_nodes[:int(no_connected/2)]

            for no in sorted_nodes:
                if no in node.connected:
                    pass
                else:
                    node.connected.append(no)
                    no[0].connected.append((node, no[1]))
                i += 1
                if i > no_connected:
                    break

            random.shuffle(node.connected)


    def set_start_end(self):
        """Sent the start and end position as long as they are far enough away"""
        while self.get_distance(0, -1) < self.w * .7:
            random.shuffle(self.nodes)
        self.nodes[0].position = "start"
        self.nodes[0].weight = 0
        self.nodes[-1].position = "end"
        self.has_start = self.has_end = True

    def get_distance(self, pos, pos2):
        # get distance between two cities
        node1 = self.nodes[pos]
        node2 = self.nodes[pos2]

        dist = math.hypot(node2.x - node1.x, node2.y - node1.y)
        return dist

    def find_solution(self):
        """ Find the optimal solution"""

        # get starting node
        pq = PriQ()

        # get start node
        self.make_start_end_last()
        startNode = self.nodes[-2]

        # print(f"Start node - {startNode.ident}")
        # put start node into the queue
        startNode.queued = True
        pq.put(startNode)

        # iterate the queue until empty
        while not pq.empty():
            # get highest priority item
            node = pq.pop()
            node.queued_com = True

            # print(f"Searching node for routes - {node.ident}")
            # search all sub nodes
            for sub_node_details in node.connected:
                # print(f"Checking weight to sub_node - {sub_node.ident}")
                # get distance to node and subnode
                sub_node, distance = sub_node_details
                # if distace is better than current distance to this node then log
                if sub_node.weight > node.weight + distance:

                    print(f"New Distance Shorter Distance Found to sub_node - {sub_node.ident}")
                    # if has never been queued or "searched" then queue the item and not the node its already came from.
                    # print(f"Old weight {sub_node.weight} new weight = {node.weight + distance}")
                    sub_node.weight = node.weight + distance

                    if sub_node != node.via and not sub_node.queued:
                        print(f"Subnode not searched yet, adding to queue - {sub_node.ident}")
                        pq.put(sub_node)
                        sub_node.queued = True
                        sub_node.via = node
                    elif sub_node != node.via and sub_node.queued and not sub_node.queued_com:
                        print(f"Sub node priority updated in queue - {sub_node.ident}")
                        sub_node.via = node
                        pq.put(sub_node)

    def set_route(self):
        """ used to set the route based on start and end point"""
        if len(self.nodes) > 0 and self.has_start and self.has_end:
            self.route = []
            self.get_route()

    def get_route(self, node=None, routes_to=[]):
        """Recursively get the route"""
        if not node:
            node = [x for x in self.nodes if x.position == "end"][0]
        self.route.append(node)
        if node.via:
            self.get_route(node.via, routes_to)
        return

    def make_start_end_last(self):
        """ used to make sure the start and end last on the node list for drawing purposes"""
        start = [x for x in self.nodes if x.position == "start"]
        if start != []:
            startNode = start[0]
            self.nodes.remove(startNode)
            self.nodes += [startNode]
        end = [x for x in self.nodes if x.position == "end"]
        if end != []:
            endNode = end[0]
            self.nodes.remove(endNode)
            self.nodes += [endNode]


    def draw_nodes(self):
        "Draw the nodes"
        self.board_drawn = self.board.copy()

        for node in self.nodes:
            colour, size = node.get_colour_size()
            if node.queued:
                self.board_drawn = cv2.circle(self.board_drawn, (node.y, node.x), radius=int(self.w * size),
                                              color=(224, 145, 24), thickness=3)
            self.board_drawn = cv2.circle(self.board_drawn, (node.y, node.x), radius=int(self.w * size), color=colour,
                                          thickness=-1)

    def draw_edges(self):
        """ Draw the node edges """
        drawn = []

        for node in self.nodes:
            node_pos = node.get_position()
            for join in node.connected:
                # check if node has been drawn
                if not [node.ident, join[0].ident] in drawn:
                    self.board_drawn = cv2.line(self.board_drawn, node_pos, join[0].get_position(),
                                                color=(120, 120, 120), thickness=1)
                    drawn.append([node.ident, join[0].ident])
                    drawn.append([join[0].ident, node.ident])

    def draw_solution(self):
        """Draw the actual solution"""
        for node in range(len(self.route)):
            if node != len(self.route) - 1:
                self.board_drawn = cv2.line(self.board_drawn, self.route[node].get_position(),
                                            self.route[node + 1].get_position(),
                                            color=(63, 224, 38),
                                            thickness=2)


def change_nodes(val):
    global nodes
    nodes = val


def mouse_event(event, x, y, flags, param):
    """
    do the mouse event
    :param event: mouse event
    :param x: x pos
    :param y: y pos
    :param flags: None
    :param param: None
    """
    global maps
    global actions
    global route

    if actions["draw"] == "draw_nodes" and event == cv2.EVENT_LBUTTONDOWN:
        maps.no_nodes += 1
        maps.nodes.append(Node(maps, maps.no_nodes, (y, x)))
        actions["draw_board"] = True

    elif actions["draw"] == "change_start" and event == cv2.EVENT_LBUTTONDOWN:
        maps.clear_other(queued=True, weight=True, via=True)
        if maps.get_set_clicked((x, y), "start"):
            actions["find"] = True
            actions["draw_board"] = True
    elif actions["draw"] == "change_end" and event == cv2.EVENT_LBUTTONDOWN:
        if maps.get_set_clicked((x, y), "end"):
            actions["find"] = True
            actions["draw_board"] = True


def get_window():
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Button('Refresh', key="refresh"),
               sg.Button('Change Start', key="change_start"),
               sg.Button('Change End', key="change_end"),
               sg.Button('Draw New Nodes', key="draw_nodes"),
               sg.Button('Clear Nodes', key="clear_nodes"),
               sg.Button('Clear Edges', key="clear_edges"),
               sg.Button('Reload Edges', key="reload_edges"),
               sg.Button('Quit', key="quit")]]

    # Create the Window
    return sg.Window('Options', layout)
    # Event Loop to process "events" and get the "values" of the inputs


def check_window(window):
    global maps
    global actions
    event, values = window.read(1)

    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        actions["quit"] = True

    if event == "change_start":
        actions["draw"] = event

    if event == "change_end":
        actions["draw"] = event

    if event == "draw_nodes":
        actions["draw"] = event

    if event == "refresh":
        actions["draw_board"] = True
        actions["init"] = True
        actions["find"] = True
        actions["draw"] = True

    if event == "clear_nodes":
        actions["draw_board"] = True
        maps.clear_nodes()
        maps.route = []

    if event == "clear_edges":
        actions["draw_board"] = True
        maps.clear_other(queued=True, edges=True, weight=True, via=True)
        maps.route = []

    if event == "reload_edges":
        actions["draw_board"] = True
        maps.clear_other(queued=True, weight=True)
        maps.init_random_edges()
        actions["find"] = True
        maps.start_node_zero_weight()
        maps.route = []

    if event == "quit":
        actions["quit"] = True


def run():
    global maps

    while True:
        # get user defined board if needed
        if actions["init"]:
            actions["init"] = False
            maps = Map(height, width, nodes=nodes)

        # find solution if needed
        if actions["find"]:
            actions["find"] = False
            maps.find_solution()

        # draw if needed
        if actions["draw_board"]:
            maps.draw_nodes()
            maps.draw_edges()
            actions["draw_board"] = False

        maps.set_route()
        if maps.route:
            maps.draw_solution()

        # check for keypresses
        check_window(window)

        # show image
        cv2.imshow(window_name, maps.board_drawn)
        cv2.waitKey(1)

        if actions["quit"]:
            return


nodes = 600
height = 800
width = 1600
max_nodes = int((height * width) / 750)
window_name = "diijkstras"
maps = None
cv2.namedWindow(window_name)
cv2.createTrackbar("Nodes", window_name, nodes, max_nodes, change_nodes)
cv2.setMouseCallback(window_name, mouse_event)
window = get_window()

actions = {"init": True, "find": True, "draw": True, "draw_board": True, "quit": False}

run()

if __name__ == "__main__":
    pass