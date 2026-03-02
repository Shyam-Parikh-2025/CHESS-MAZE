import numpy as np, random, sys
from numba import njit

game_dict = {
    1: 'wall',
    0: 'room',
    2: 'start',
    4: 'boss_start',
    3: 'battles'
}

class MapGen:
    def __init__(self, numBattles:int = 4, difficulty:int = 2, maze_size=(20, 20)):
        self.size = maze_size
        self.grid = np.ones(self.size, dtype=np.int8)
        self.numBattles = numBattles
        self.difficulty = difficulty

    def generate_full(self):
        maze_obj = MazeGen(self.size, self.numBattles, self.difficulty)
        maze_obj.gen_maze()
        self.grid = maze_obj.maze.copy()

        self.grid[1: 5, 1: 5] = 0
        self.grid[2, 2] = 2

        self.grid[-6: -1, -6: -1] = 0
        self.grid[-3, -3] = 4
        # have to ensure boss walls are 1
        return self.grid, maze_obj.portals

    def __repr__(self):
        maze_lst = []
        symbols = {
            0: "  ",
            1: "██",
            2: "ST",
            3: "BT",
            4: "BS"
        }
        for row in self.grid:
            maze_lst.append("".join(symbols.get(int(x), "NA") for x in row))
        return "\n".join(maze_lst)


class MazeGen:
    def __init__(self, size_desired:tuple, numBattles:int, level:int = 2):
        w, h = size_desired
        w, h = [side if side % 2 == 1 else side + 1 for side in [w, h]]
        self.size = (w, h)
        self.num_Battles = numBattles
        self.level = level
        self.maze = None
        self.portals = {}

    def gen_maze(self):
        w, h = self.size
        maze = _gen_maze(h=h, w=w)
        maze = _detail_maze(self.num_Battles, maze, w, h, 3)
        maze = _easify(self.level, maze, w=w, h=h)

        self.maze = maze
        self.portals = {}

        portal_idxs = np.argwhere(maze == 3)
        for idx, pos in enumerate(portal_idxs):
            self.portals[f'portal {idx+1}'] = (int(pos[0]), int(pos[1]))


@njit
def _gen_maze(h, w):
    """
    Generates a maze using Recursive Backtracking - iterative to avoid the recursion limit.
    
    Algorithm:
    1. Mark the starting cell as a room (0).
    2. Append it to stack.
    3. While the stack is not empty:
        a. Pop the last cell in the stack list.
        b. If the current cell has any neighbours which have not been visited:
            i. Append the current cell to the stack.
            ii. Choose one of the unvisited neighbours randomly.
            iii. Remove the wall between the current cell and the chosen neighbour.
            iv. Make the chosen neighbour as 0 (so room) and append it to the stack.
    """
    maze = np.ones((h, w), dtype=np.int8)
    start_r, start_c = 1, 1
    maze[start_r, start_c] = 0

    stack = [(start_r, start_c)]
    dirs = np.array([(0, 2), (2, 0), (-2, 0), (0, -2)])

    while len(stack) > 0:
        sq_r, sq_c = stack[-1]
        neighbors = []

        for i in range(4):
            dr, dc = dirs[i]
            nr, nc = sq_r + dr, sq_c + dc
            if 0 < nr < h-1 and 0 < nc < w-1:
                if maze[nr, nc] == 1:
                    neighbors.append((nr, nc))

        if len(neighbors) == 0:
            stack.pop()
        else:
            idx = np.random.randint(0, len(neighbors))
            nr, nc = neighbors[idx]

            maze[nr, nc] = 0
            maze[(sq_r + nr) // 2, (sq_c + nc) // 2] = 0
            stack.append((nr, nc))

    return maze

# we will handle 'easifing' by probability, meaning
# if we want easiest, it is more likely to drop a wall
@njit
def _easify(level, maze, w, h):
    if level == 2:
        return maze

    probs = 0.5 if level == 0 else 0.3
    for r in range(1, h-1, 2):
        for c in range(1, w-1, 2):
            if maze[r, c] == 0:
                wall_cnt = 0
                wall_lst = np.zeros((4, 2), dtype=np.int32)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 < nr < h-1 and 0 <nc < w-1: # if in range
                        if maze[nr, nc] == 1:
                            wall_lst[wall_cnt, 0] = nr
                            wall_lst[wall_cnt, 1] = nc
                            wall_cnt += 1
                if wall_cnt == 3:
                    if np.random.random() < probs:
                        idx = np.random.randint(0, wall_cnt)
                        chosen_r = wall_lst[idx, 0]
                        chosen_c = wall_lst[idx, 1]
                        maze[chosen_r, chosen_c] = 0
    return maze


@njit
def _detail_maze(num_Battles, maze, w, h, num):
    cnt = 0
    
    for _ in range(99): # essentially giving more spawn attempts
        for r in range(1, h-1):
            for c in range(1, w-1):
                #if 3 <= r <= h-6 and 3 <= c <= w-6:
                if not (r <= 3 and c <= 3) and not (r >= h-6 and c >= w-6):
                    if cnt >= num_Battles:
                        return maze
                    if maze[r, c] == 0:
                        wall_cnt = 0
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            if maze[r+dr, c+dc] == 1:
                                wall_cnt +=1
                        if wall_cnt == 3:
                            if np.random.random() < 0.36:
                                maze[r, c] = num
                                cnt += 1
    if cnt < 5:
        for _ in range(3): # essentially giving more spawn attempts
            for r in range(1, h-1):
                for c in range(1, w-1):
                    #if 3 <= r <= h-6 and 3 <= c <= w-6:
                    if not (r <= 3 and c <= 3) and not (r >= h-6 and c >= w-6):
                        if cnt >= 9:
                            return maze
                        if maze[r, c] == 0:
                            wall_cnt = 0
                            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                if maze[r+dr, c+dc] == 1:
                                    wall_cnt +=1
                            if wall_cnt >= 2:
                                if np.random.random() < 0.36:
                                    maze[r, c] = num
                                    cnt += 1
    return maze

if __name__ == "__main__":
    map = MapGen()
    map.generate_full()
    print(map)