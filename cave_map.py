from dungeon import Generator
import enum


Dir = {
    'N': (0, -1),
    'S': (0, 1),
    'E': (1, 0),
    'W': (-1, 0),
    'nop': (0, 0)
}

# Tuple add
def tadd(a, b):
    return (a[0] + b[0], a[1] + b[1])

# Tuple mult
def tmul(a, b):
    return (a[0] * b[0], a[1] * b[1])

# Tuple scalar mult
def tscal(s, a):
    return (s * a[0], s * a[1])

class Bot:
    tile = None
    def __init__(self, grid, id, vision_radius=2):
        self.id = id
        self.strid = 'bot' + str(id)
        self.vision_radius = vision_radius
        self.grid = grid

    def start(self):
        self.place()
        self.mark_seen()
        self.mark_vision()

    def place(self):
        for row in reversed(range(self.grid.width)):
            for col in range(self.grid.height):
                if self.grid.is_open(row, col):
                    bot.tile = (row, col)
                    self.grid.level[row][col] = bot.strid

                    return

    def move(self):
        self.mark_seen()
        move = self.get_move()
        tmp = self.tile
        new_tile = tadd(self.tile, Dir[move])
        print(self.strid, tmp, '->', new_tile)
        self.tile = new_tile 
        self.grid.level[new_tile[0]][new_tile[1]] = self.strid
        # Mark old pos as seen
        self.mark_vision()

    def get_vision_tiles_idx(self):
        # TODO fix seeing thru walls
        tiles = []
        for i in range(self.tile[0] - self.vision_radius, self.tile[0] + self.vision_radius):
            for j in range(self.tile[1] - self.vision_radius, self.tile[1] + self.vision_radius + 1):
                tiles.append((i, j))
        return tiles

    def get_vision_tiles(self):
        tiles = []
        for i in range(self.tile[0] - self.vision_radius, self.tile[0] + self.vision_radius):
            for j in range(self.tile[1] - self.vision_radius, self.tile[1] + self.vision_radius + 1):
                tiles.append(self.grid.level[i][j])
        return tiles

    def mark_vision(self):
        for i, j in self.get_vision_tiles_idx():
            if not self.valid_move((i, j)):
                continue
            if self.grid.is_open(i, j):
                self.grid.level[i][j] = 'vision'

    def mark_seen(self):
        for i, j in self.get_vision_tiles_idx():
            if not self.valid_move((i, j)):
                continue
            if self.grid.is_open(i, j):
                self.grid.level[i][j] = 'explored'

    def valid_move(self, m):
        if m[0] < 0 or m[0] >= self.grid.width:
            return False
        if m[1] < 0 or m[1] >= self.grid.height:
            return False
        if self.grid.level[m[0]][m[1]] in ['wall', 'stone']:
            return False

        return True

    def get_move(self):
        '''Move toward the unknown'''
        unexplored = dict(Dir)
        for direction in Dir.keys():
            unexplored[direction] = 0
            for i in range(1, 1 + self.vision_radius):
                del_x, del_y = tscal(i, Dir[direction])
                x = self.tile[0] + del_x
                y = self.tile[1] + del_y
                # Don't check outside map
                if not self.valid_move((x, y)):
                    print('invalid ', x, y)
                    continue
                print(x, y)
                unexplored[direction] += score_tiles([self.grid.level[x][y]])

        for direction in unexplored:
            print('dir {} has {} moves'.format(direction, unexplored[direction]))
        
        if sum(unexplored.values()) == 0:
            print('{} no good moves, staying put'.format(self.strid))
            return 'nop'
        move_dir = [d for d in sorted(unexplored, key=unexplored.get, reverse=True)][0]
        print('{} moving {}'.format(self.strid, move_dir))
        return move_dir




def score_tiles(tiles):
    score = 0
    for t in tiles:
        if t in ['floor', 'vision']:
            score += 1
        elif t in ['explored']:
            score += 0.25
        #elif t in ['wall', 'stone']:
        #    score -= 1
    return score

def get_order(bots):
    visible_tiles = []
    for bot in bots:
        visible_tiles.append(
            [bot.id, score_tiles(bot.get_vision_tiles())]
        )
    order = sorted(visible_tiles, key=lambda x: x[1], reverse=True)
    order = [o[0] for o in order]
    print('New order is ', order)
    return order


g = Generator(width=20, height=20)
g.gen_level()
bots = [Bot(g, i) for i in range(1, 4)]

# Start botleft corner
for bot in bots:
    bot.start()

g.gen_tiles_level()


import time
import os
while(True):
    order = get_order(bots)
    print('ord', order)
    for bot in order:
        print(bots[bot - 1].strid, 'is moving')
        bots[bot - 1].move()
        g.print_tiles()
        time.sleep(3)

# leader is selected by furthest away from mapped area
# leader jumps towards unmapped area
# if behind mapped + sides mapped, single file
# if behind not mapped, slave move to scan behind
# if side not mapped, form a line with leader until mapped
