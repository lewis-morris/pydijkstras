import itertools
import random
import sys
import PySimpleGUI as sg
import cv2
import numpy as np

from misc import PriQ, MazeMaker
from road import Map

actions = None
maze = None
window_name = None
brush_size = 1
brush_type = 0

class BasicNode():

    def __init__(self, pos):
        self.y, self.x = pos
        self.connected = []
        self.position = None
        self.weight = sys.maxsize
        self.via = None
        self.queued = False
        self.queued_com = False


class Maze(Map):

    def __init__(self, height, width):

        #set height and width
        self.h = height
        self.w = width

        # load the board
        self.reset_map()

        #create the node array
        self.node_count = itertools.count()
        self.nodes = []
        self.create_nodes()

        #create the images
        self.board_searched: np.array = None
        self.board: np.array = None
        self.display_board: np.array = None
        self.reset_map()

        self.pq = PriQ()

        # used for storing the best route
        self.route = []

        # set the start and end node vars
        self.end_pos = None
        self.start_pos = None
        self.end_node = None

    def reset_q(self):
        # reset the priority queue
        self.pq = PriQ()

    def get_weight_from_val(self,val):

        if val == 255:
            return 1
        if val == 185:
            return 3
        if val == 120:
            return 6
        if val == 75:
            return 9
        else:
            print()
    def check_created(self, node):
        """
        Not proud of this one - it checks if adjacent pixels are nodes or not and creates where needed.
        #todo - tidy up
        :param node:
        :return:
        """
        x = node.x
        y = node.y

        #loop surrounding nodes
        for yy, xx in [(y - 1, x), (y + 1, x), (y, x + 1), (y, x - 1)]:
            if (yy >= 0 and xx >= 0) and (yy < self.h and xx < self.w) and (yy != node.y or xx != node.x):
                # if not wall colour

                if not (self.board_searched[yy, xx, :] == [0, 0, 0]).all():

                    #create node if needed

                        if self.nodes[yy,xx] is None:
                            self.nodes[yy,xx] = BasicNode((yy, xx))

                        #check the colour of the cell if its grey then its harder to get through
                        weight = self.get_weight_from_val(self.board[yy, xx, 0])

                            #create node with weight
                        if not self.nodes[yy,xx] in node.connected:
                            node.connected.append([self.nodes[yy,xx], weight])
                        if not node in self.nodes[yy,xx].connected:
                            self.nodes[yy,xx].connected.append([node, weight])
            else:
                print("")

    def create_nodes(self):
        # create node array that matches the image
        ar = np.array([None], dtype=object)
        self.nodes = np.resize(ar, (self.h, self.w))
        self.nodes[:, :] = None

    def set_postion(self, position, x, y):
        # set position of the nodes
        node = self.nodes[y][x]
        if node is None:
            node = BasicNode((y, x))
        node.start_pos = (y, x)
        node.position = position
        if position == "start":
            node.weight = 0
            self.start_pos = (y,x)
        else:
            self.end_pos = (y,x)

    def draw_searched(self, indexs):
        y_ind = [x[0] for x in indexs]
        x_ind = [x[1] for x in indexs]
        self.board_searched[y_ind, x_ind, :] = (239, 176, 245)

    def draw_start_end(self):

        # draw the start and end point

        self.display_board = self.board_searched.copy()
        if not self.start_pos is None:
            y, x = self.start_pos
            self.display_board[y, x] = (252, 211, 3)

        if not self.end_pos is None:
            y, x = self.end_pos
            self.display_board[y, x, :] = (3, 252, 20)

    def reset_map(self):

        # reset the map to blank
        self.board = np.ones((self.h, self.w, 3), dtype=np.uint8) * 255
        self.board_searched = self.board.copy()

    def create_start_end(self):
        # set the start and end point of search space
        if self.start_pos:
            # self.get_index(self.start_pos)
            y, x = self.start_pos
            self.nodes[y][x] = BasicNode((y,x))
            self.nodes[y][x].position = "start"
        if self.end_pos:
            # index = self.get_index(node_pos)
            y, x = self.end_pos
            self.nodes[y][x] = BasicNode((y,x))
            self.nodes[y][x].position = "end"

    def clear_nodes(self, leave_startend=True):
        # clear all nodes
        self.create_nodes()
        self.create_start_end()
        self.end_node = None

    def draw_queued(self):
        # not needed / implemented
        pass

    def check_draw_over_node(self,node):
        # if node is start or end remove pos
        if not node is None:
            if node.position == "start":
                self.start_pos = None
            if node.position == "end":
                self.end_pos = None

    def draw_point(self, x, y):
        # make the board black in drawn area
        global brush_type
        global brush_size

        brush = brush_size
        if brush_type == 4:
            brush_col = 255
        elif brush_type == 3:
            brush_col = 185
        elif brush_type == 2:
            brush_col = 120
        elif brush_type == 1:
            brush_col = 75
        else:
            brush_col = 0

        self.board[y - brush:y + brush, x - brush:x + brush,:] = brush_col

        # remove nodes
        for yy in range(y - brush, y + brush):
            for xx in range(x - brush, x + brush):
                try:
                    # self.get_index((yy, xx))
                    node = self.nodes[yy,xx]
                    self.check_draw_over_node(node)
                except IndexError:
                    # node does not exist
                    pass
                node = None
        self.board_searched = self.board.copy()

    def reset_search_map(self):
        # used to reset the board
        self.board_searched = self.board.copy()

    def refresh(self):
        """ fill missing gaps"""
        self.route = []
        self.reset_map()
        self.create_nodes()
        self.start_pos = None
        self.end_pos = None

    def start_node_zero_weight(self):
        """ zero weight of start item"""
        for row in self.nodes:
            for node in row:
                if not node is None and node.position == "start":
                    node.weight = 0

    def draw_route(self):
        # draw the best route on the map
        if self.route != []:
            routes = np.hsplit(np.array([[node.y, node.x] for node in self.route]), 2)
            # route = np.array([[node.y, node.x] for node in self.route])
            self.board_searched[routes[0], routes[1], :] = (0, 0, 255)
            # for i in range(len(route)):
            #     try:
            #         self.board_searched = cv2.line(self.board_searched,route[i],route[i+1],(0,0,255),1)
            #     except:
            #         print("Route error")

    def find_solution(self, start=None, stop_on_find=True):
        """ Find the optimal solution"""

        #clear all previous nodes
        self.clear_nodes()

        #set the start node
        start_node = start

        # put start node into the queue
        start_node.queued = True
        self.pq.put(start_node)

        # iterate the queue until empty
        while not self.pq.empty():
            # get highest priority item
            node = self.pq.pop()
            node.queued_com = True

            self.check_created(node)

            # print(f"Searching node for routes - {node.ident}")
            # search all sub nodes
            for sub_node_details in node.connected:
                # print(f"Checking weight to sub_node - {sub_node.ident}")
                # get distance to node and subnode
                sub_node, distance = sub_node_details
                #print(sub_node, node, distance)
                # if distace is better than current distance to this node then log
                if sub_node.weight > node.weight + distance:

                    # print(f"New Distance Shorter Distance Found to sub_node - {sub_node.ident}")
                    # if has never been queued or "searched" then queue the item and not the node its already came from.
                    # print(f"Old weight {sub_node.weight} new weight = {node.weight + distance}")
                    sub_node.weight = node.weight + distance

                    if sub_node != node.via and not sub_node.queued:
                        # print(f"Subnode not searched yet, adding to queue - {sub_node.ident}")
                        self.pq.put(sub_node)
                        sub_node.queued = True
                        sub_node.via = node
                    elif sub_node != node.via and sub_node.queued and not sub_node.queued_com:
                        # print(f"Sub node priority updated in queue - {sub_node.ident}")
                        sub_node.via = node
                        self.pq.put(sub_node)
                    else:
                        pass

                    if sub_node.position == "end":
                        self.end_node = sub_node
                        yield True

                yield (sub_node.y, sub_node.x)

            yield

        yield True


def create_maze(maze):
    #used to create the maze
    mazeMaker = MazeMaker(maze.h, maze.w, random.choice([1]))

    n = 0
    for i in mazeMaker.search(generator=True):
        n +=1
        if n%10==0:
            maze.board = mazeMaker.get_image()
            maze.reset_search_map()
            cv2.imshow(window_name, cv2.resize(maze.board_searched,dsize=(int(maze.w*8),int(maze.h*8)), interpolation=cv2.INTER_AREA))
            cv2.waitKey(1)

def mouse_draw(event, x, y, flags, param):

    """ used to get the draw events from CV2 window"""

    global maze
    x = round(x / 8)
    y = round(y / 8)

    if (event == cv2.EVENT_LBUTTONDOWN and actions["draw"] == "draw") or actions["mouse_down"]:
        maze.draw_point(x, y)
        actions["mouse_down"] = True
    if event == cv2.EVENT_LBUTTONUP:
        actions["mouse_down"] = False
    if (event == cv2.EVENT_LBUTTONDOWN and actions["draw"] == "change_start"):
        maze.set_postion("start", x, y)
    if (event == cv2.EVENT_LBUTTONDOWN and actions["draw"] == "change_end"):
        maze.set_postion("end", x, y)


def get_maze_window():

    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Button('Make Maze', key="maze", tooltip="Do a fresh reset of the board"),
               sg.Button('Clear', key="refresh", tooltip="Do a fresh reset of the board"),
               sg.Button('Draw', key="draw", tooltip="Click screen to draw obstacles"),
               sg.Button('Change Start Point', key="change_start", tooltip="Click nodes to set as start point"),
               sg.Button('Change End Point', key="change_end", tooltip="Click nodes to set as end node"),
               sg.Button('Search', key="search", tooltip="Search the board for the solution"),
               sg.Button('Quit', key="quit", tooltip="quit")],
              [sg.Text("Brush Size:"), sg.Slider(range=(1, 7), default_value=2, size=(40, 15),orientation='horizontal', key="brush")],
              [sg.Text("Terrain Type"),sg.Radio('Impassable', "brush_type",default=True),
               sg.Radio('Hard', "brush_type"), sg.Radio('Medium', "brush_type"),sg.Radio('Easy', "brush_type"),sg.Radio('Remove', "brush_type")]]

    # Create the Window
    return sg.Window('Options', layout, keep_on_top=True)
    # Event Loop to process "events" and get the "values" of the inputs


def check_maze_window(gui_window):
    """
    Check pysimplegui for input and react
    :param gui_window:
    :return:
    """
    global maze
    global actions
    global brush_size
    global brush_type
    event, values = gui_window.read(1)


    brush_size = int(values["brush"])

    if values[0] == True:
        brush_type = 0
    elif values[1] == True:
        brush_type = 1
    elif values[2] == True:
        brush_type = 2
    elif values[3] == True:
        brush_type = 3
    elif values[4] == True:
        brush_type = 4

    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        actions["quit"] = True

    if event == "maze":
        create_maze(maze)
        maze.route = []
    if event == "refresh":

        actions["search"] = False
        actions["route"] = False
        maze.refresh()
        maze.reset_search_map()

    if event == "change_start":

        actions["draw"] = event
        actions["search"] = False
        actions["route"] = False
        maze.route = []
        maze.reset_search_map()

    if event == "draw":
        actions["draw"] = event
        actions["search"] = False
        actions["route"] = False
        maze.route = []
        maze.reset_search_map()

    if event == "change_end":
        actions["draw"] = event
        actions["route"] = False
        maze.reset_search_map()
        actions["search"] = False
        actions["route"] = False
        maze.route = []

    if event == "search":
        maze.reset_q()
        maze.clear_nodes()
        maze.reset_search_map()
        maze.route = []
        maze.start_node_zero_weight()
        actions["search"] = True
        actions["route"] = False

    if event == "quit":
        actions["quit"] = True


def run_maze(height, width):

    """ used to run the maze """

    global maze

    #get the gui window
    window = get_maze_window()

    #set vars
    search = None
    route = []


    while True:

        #if init then load the new maze
        if actions["init"]:
            actions["init"] = False
            maze = Maze(int(height / 8), int(width / 8))

        #used to find the solution while letting the board/ actions continue.
        # todo - tidy this up
        if actions["search"] or actions["clear_search"]:
            if search is None:
                actions["clear_search"] = False
                if maze.start_pos and maze.end_pos:
                    # maze.get_index(maze.start_pos)
                    y, x = maze.start_pos
                    search = maze.find_solution(start=maze.nodes[y][x], stop_on_find=False)
                else:
                    actions["search"] = False
                    actions["route"] = False

            if actions["search"]:
                colour_index = []
                for loop in range(int((maze.w * maze.h) / 200)):
                    out = next(search)
                    if out is True:
                        search = None
                        actions["search"] = False
                        actions["route"] = True
                        if not maze.end_node is None:
                            maze.get_route(maze.end_node)

                        break
                    elif not out is None:
                        colour_index.append(out)

                if colour_index != []:
                    maze.draw_searched(colour_index)

        maze.draw_route()
        #check for user input
        check_maze_window(window)
        #draw start and end points
        maze.draw_start_end()
        #draw queued items
        maze.draw_queued()
        #show window
        cv2.imshow(window_name, cv2.resize(maze.display_board, dsize=(width, height), interpolation=cv2.INTER_AREA))
        cv2.waitKey(1)

        if actions["quit"]:
            return


def load_maze(height, width, window):

    """ used to load the maze board, settings and cv2 window """
    global actions
    global maze
    global window_name
    window_name = window

    actions = {"init": True, "route": True, "draw": "draw", "clear_search": False, "mouse_down": False, "quit": False,
               "search": False}

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_draw)

    maze = None

    run_maze(height, width)
