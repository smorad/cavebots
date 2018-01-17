from dungeon import Generator

g = Generator()
g.gen_level()
g.gen_tiles_level()


class Bot:
    def __init__(self, id, x, y, z, vision_radius=100):
        pass

# leader is selected by furthest away from mapped area
# leader jumps towards unmapped area
# if behind mapped + sides mapped, single file
# if behind not mapped, slave move to scan behind
# if side not mapped, form a line with leader until mapped
