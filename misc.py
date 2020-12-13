import itertools
import heapq as h
import numpy as np
import random
import cv2

class MazeMaker:
    def __init__(self, height, width, blocksize):
        self.height = int(height)
        self.width = int(width)
        expected_size = np.array((height, width))
        board_shape = np.round((expected_size / blocksize)).astype(int)
        self.board = np.zeros(board_shape)
        self.current_pos = []
        self.queue = []
        self.done_positions = []
        self.to_do_position = []
        self.current_directions = []
        self.set_to_dos()
        self.stride = 2

    def set_to_dos(self):
        for y in range(3,self.board.shape[0]-3,2):
            for x in range(3,self.board.shape[1]-3,2):
                self.to_do_position.append([y,x])

    def mark_done(self,pos):

        self.to_do_position.remove(pos)
        self.done_positions.append(pos)

    def get_start(self):
        while True:
            y,x = random.choice(self.to_do_position)
            if x%2 != 0 and y %2 != 0:
                break
        return [y, x]

    def draw_position(self, pos, move_dir):

        y,x = pos

        if move_dir == "u":
            self.board[y-2:y,x] = 1
            y -=2
        elif move_dir == "d":
            self.board[y:y+3,x] = 1
            y += 2
        elif move_dir == "r":
            self.board[y,x:x+3] = 1
            x += 2
        elif move_dir == "l":
            self.board[y,x-2:x] = 1
            x -=2



        #print("err:" + str(pos))
        return [y,x]

    def get_allowed(self,pos):
        y,x = pos
        allowed = []

        if y> 2:
            if (self.board[y-2:y,x] == 0).all():
                allowed.append("u")
        if y < self.board.shape[0]-2:
            if (self.board[y+1:y+3,x] == 0).all():
                allowed.append("d")
        if x < self.board.shape[1]-3:
            if (self.board[y,x+1:x+3] == 0).all() :
                allowed.append("r")
        if x > 2:
            if (self.board[y,x-2:x] == 0).all():
                allowed.append("l")
        if len(allowed) > 0:
            return allowed
        return None

    def search(self,generator=False):

        self.queue.append(self.get_start())

        while len(self.queue) != 0:
            node = self.queue.pop()
            #self.board[node[0],node[1]] = 0.5
            while True:
                directs = self.get_allowed(node)
                if directs:
                    #print(directs)
                    new_dir = random.choice(directs)
                    #print(new_dir)
                    node = self.draw_position(node,new_dir)
                    #print(node)
                    if len(directs)>1:
                        self.queue.append(node)
                else:
                    break
                if generator:
                    yield

    def show(self):
        cv2.imshow("test", self.get_image())
        cv2.waitKey(0)

    def get_image(self):
        board_img = (np.stack([self.board] * 3, 2) * 255).astype(np.uint8)
        board = cv2.resize(board_img, (self.width, self.height), interpolation=cv2.INTER_AREA)
        return np.where(board < 2 , board, 255).astype(np.uint8)


class PriQ:
    """ Amended example from python docs"""

    def __init__(self):
        self.pq = []  # list of entries arranged in a heap
        self.entry_finder = {}  # mapping of tasks to entries
        self.REMOVED = '<removed-task>'  # placeholder for a removed task
        self.counter = itertools.count()  # unique sequence count

    def empty(self):
        """ is queue empty?"""
        return len([x for x in self.pq if x[2] != self.REMOVED]) == 0

    def put(self, task):
        """Add a new task or update the priority of an existing task"""
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [task.weight, count, task]
        self.entry_finder[task] = entry
        h.heappush(self.pq, entry)

    def remove_task(self, task):
        """Mark an existing task as REMOVED.  Raise KeyError if not found."""
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop(self):
        """Remove and return the lowest priority task. Raise KeyError if empty."""
        while self.pq:
            priority, count, task = h.heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')
