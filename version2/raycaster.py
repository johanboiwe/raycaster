import pygame as pg
import numpy as np
import math
import sys
from numba import jit, njit
from multiprocessing import *
LEGACY_RAYCAST = False
FOV = 60
BLOCK_SIZE = 64
COLOURS = {
    "OPAQUE": np.array((255, 255, 255, 255), dtype="f"),
    "BLACK": np.array((0, 0, 0, 0), dtype="f"),
    "GREEN": np.array((0, 255, 0, 0), dtype="f"),
    "RED": np.array((255, 0, 0, 0), dtype="f"),
    "BLUE": np.array((0, 0, 255, 0), dtype="f"),
    "GRAY": np.array((96, 96, 96, 0), dtype="f"),
    "YELLOW": np.array((255, 255, 0, 0), dtype="f"),
}


# "BLACK": (0, 0, 0, 0),
# "GREEN": (0, 0, 0, 0),
# "RED": (255, 0, 0, 0),
# "BLUE": (0, 0, 255, 0),
# "GRAY": (96, 96, 96, 0),
# "YELLOW": (255, 255, 0, 0),

@njit()
def cast_ray(iteration, angle, rotation, position_x, position_y, level_matrix, level_size):
    # print("This is iteration", iteration)
    radians = math.radians(angle + 0.01)
    fisheye = math.cos(radians - math.radians(rotation))
    x = math.cos(radians)
    y = math.sin(radians)
    if x < 0:
        is_x_positive = False
    else:
        is_x_positive = True
    if y < 0:
        is_y_positive = False
    else:
        is_y_positive = True
    # sx = lambda length=1: (length * (math.sqrt((1 ** 2) + ((y / x) ** 2))))
    # sy = lambda length=1: (length * (math.sqrt((1 ** 2) + ((x / y) ** 2))))
    x_ray = 0
    y_ray = 0
    x_at_end = False
    y_at_end = False
    current_position_x_x = position_x
    current_position_x_y = position_y
    current_position_y_x = position_x
    current_position_y_y = position_y

    # getting into blocks

    if x > 0:
        x_ray = (abs(position_x - (int(position_x / BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE))) * (
            math.sqrt((1 ** 2) + ((y / x) ** 2)))
    if x < 0:
        x_ray = (position_x - (int(position_x / BLOCK_SIZE) * BLOCK_SIZE - 0)) * (math.sqrt((1 ** 2) + ((y / x) ** 2)))
    if y > 0:
        y_ray = (abs(position_y - (int(position_y / BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE))) * (
            math.sqrt((1 ** 2) + ((x / y) ** 2)))
    if y < 0:
        y_ray = (position_y - (int(position_y / BLOCK_SIZE) * BLOCK_SIZE - 0)) * (math.sqrt((1 ** 2) + ((x / y) ** 2)))

    # travsering

    while not x_at_end or not y_at_end:
        # print("Traverse-loop iteration started")
        # print("X:", current_position_x_x,current_position_x_y, x_ray)
        # print("Y:", current_position_y_x,current_position_y_y, y_ray)
        block_coord_x, block_coord_y = 0, 0
        if x_ray <= y_ray:
            # print("X-ray is smaller than y-ray (or equal)")
            if not x_at_end:
                current_position_x_x = (position_x + (x_ray * x))
                current_position_x_y = (position_y + (x_ray * y))
                current_position_x_x = round(current_position_x_x, 3)
                current_position_x_y = round(current_position_x_y, 3)

                block_coord_x = math.trunc(current_position_x_x / BLOCK_SIZE)
                if not is_x_positive: block_coord_x -= 1
                # if x < 0: block_coord_x -= 1
                block_coord_y = math.trunc(current_position_x_y / BLOCK_SIZE)

                if block_coord_x < 0 or block_coord_y < 0:
                    x_at_end = True
                    continue

                if block_coord_x >= level_size[0] or block_coord_y >= level_size[1]:
                    x_at_end = True
                    continue

                if level_matrix[block_coord_x, block_coord_y]:
                    # print("Hit in x, position:", (current_position_x_x,current_position_x_y), "IE:", (block_coord_x,block_coord_y))
                    x_at_end = True
                    continue
                # print("NO hit in x, position:", (current_position_x_x,current_position_x_y), "IE:", (block_coord_x,block_coord_y))

                x_ray += BLOCK_SIZE * (math.sqrt((1 ** 2) + ((y / x) ** 2)))
                # print("X-ray as been extended")
                # continue

            else:
                # print("but because x is at end, y is called ")
                current_position_y_x = (position_x + (y_ray * x))
                current_position_y_y = (position_y + (y_ray * y))
                current_position_y_x = round(current_position_y_x, 3)
                current_position_y_y = round(current_position_y_y, 3)
                # if y_at_end: continue

                block_coord_x = math.trunc(current_position_y_x / BLOCK_SIZE)
                block_coord_y = math.trunc(current_position_y_y / BLOCK_SIZE)
                if not is_y_positive: block_coord_y -= 1
                # if y<0: block_coord_y -=1
                if block_coord_x < 0 or block_coord_y < 0:
                    y_at_end = True
                    continue

                if block_coord_x >= level_size[0] or block_coord_y >= level_size[1]:
                    y_at_end = True
                    continue

                if level_matrix[block_coord_x, block_coord_y]:
                    # print("Hit in y, position:", (current_position_y_x, current_position_y_y), "IE:",(block_coord_x, block_coord_y))
                    y_at_end = True
                    continue
                # print("NO hit in y, position:", (current_position_y_x, current_position_y_y), "IE:",(block_coord_x, block_coord_y))
                y_ray += BLOCK_SIZE * (math.sqrt((1 ** 2) + ((x / y) ** 2)))
                # print("Y-ray as been extended")
                # continue
        else:
            # print("y-ray is smaller than x-ray")
            if not y_at_end:
                current_position_y_x = (position_x + (y_ray * x))
                current_position_y_y = (position_y + (y_ray * y))
                current_position_y_x = round(current_position_y_x, 3)
                current_position_y_y = round(current_position_y_y, 3)

                block_coord_x = math.trunc(current_position_y_x / BLOCK_SIZE)
                block_coord_y = math.trunc(current_position_y_y / BLOCK_SIZE)
                if not is_y_positive: block_coord_y -= 1
                # if y < 0: block_coord_y -=1
                if block_coord_x < 0 or block_coord_y < 0:
                    y_at_end = True
                    continue

                if block_coord_x >= level_size[0] or block_coord_y >= level_size[1]:
                    y_at_end = True
                    continue

                if level_matrix[block_coord_x, block_coord_y]:
                    # print("Hit in y, position:", (current_position_y_x, current_position_y_y), "IE:",(block_coord_x, block_coord_y))
                    y_at_end = True
                    continue
                # print("NO hit in y, position:", (current_position_y_x, current_position_y_y), "IE:",(block_coord_x, block_coord_y))

                y_ray += BLOCK_SIZE * (math.sqrt((1 ** 2) + ((x / y) ** 2)))
            # print("Y-ray as been extended")
            # continue

            else:
                #  print("but because y is at end, x is called ")
                current_position_x_x = (position_x + (x_ray * x))
                current_position_x_y = (position_y + (x_ray * y))
                current_position_x_x = round(current_position_x_x, 3)
                current_position_x_y = round(current_position_x_y, 3)
                # if x_at_end:continue

                block_coord_x = math.trunc(current_position_x_x / BLOCK_SIZE)
                if not is_x_positive: block_coord_x -= 1
                # if x < 0: block_coord_x -=1
                block_coord_y = math.trunc(current_position_x_y / BLOCK_SIZE)

                if block_coord_x < 0 or block_coord_y < 0:
                    x_at_end = True
                    continue

                if block_coord_x >= level_size[0] or block_coord_y >= level_size[1]:
                    x_at_end = True
                    continue

                if level_matrix[block_coord_x, block_coord_y]:
                    # print("Hit in x, position:", (current_position_x_x,current_position_x_y), "IE:", (block_coord_x,block_coord_y))
                    x_at_end = True
                    continue
                # print("NO hit in x, position:", (current_position_x_x,current_position_x_y), "IE:", (block_coord_x,block_coord_y))

                x_ray += BLOCK_SIZE * (math.sqrt((1 ** 2) + ((y / x) ** 2)))
                # print("X-ray as been extended")
                # continue

    x_ray *= fisheye
    y_ray *= fisheye
    final_result = (current_position_x_x, current_position_x_y, x_ray)
    if x_ray > y_ray: final_result = (current_position_y_x, current_position_y_y, y_ray)
    # print("X-candidate is:",(current_position_x_x, current_position_x_y, x_ray))
    # print("Y-candidate is:",(current_position_y_x, current_position_y_y, y_ray))
    # print("Final result is:", final_result)
    return final_result

class CalculationAids:
    def __init__(self):
        self.adjusted_block_polarity = lambda x_or_y: (abs(x_or_y) / x_or_y) * BLOCK_SIZE
        self.adjusted_angle_in_radians = lambda angle_in_degrees: math.radians((angle_in_degrees % 360) - 180)
        self.vector_polarity = lambda x_or_y: (abs(x_or_y) / x_or_y)
        self.pixels_to_matrix_address = lambda cords: list([math.trunc(i / BLOCK_SIZE) for i in cords])

    @staticmethod
    def extract_line(matrix, start_coordinates, end_coordinates):
        x0 = start_coordinates[0]
        y0 = start_coordinates[1]
        x1 = end_coordinates[0]
        y1 = end_coordinates[1]
        length = int(math.sqrt(((x1 - x0) ** 2) + ((y1 - y0) ** 2)))
        # length = int(math.ceil(((x1-x0) + (y1-y0))/2))
        # print(length)
        x, y = np.linspace(x0, x1, length), np.linspace(y0, y1, length)
        zi = matrix[x.astype(np.int_), y.astype(np.int_)]
        return zi


class Game:
    def __init__(self):
        self.image_sprites = pg.sprite.Group()
        self.wall_sprites = pg.sprite.Group()
        level = [
            "WWWWWWWWWW",
            "W........W",
            "W........W",
            "W.W....W.W",
            "W.W....W.W",
            "W.W....W.W",
            "W.W....W.W",
            "W.WWWWWW.W",
            "W........W",
            "WWWWWWWWWW"
        ]
        self.level_matrix = np.zeros((len(level), len(level[0])), dtype=np.uint8)
        for x, line in enumerate(level):
            for y, block in enumerate(line):
                if block == "W":
                    self.level_matrix[x][y] = 1
                elif block == ".":
                    self.level_matrix[x][y] = 0
        self.level_size = (len(self.level_matrix), len(self.level_matrix[0]))
        self.blocks = (tuple(zip(*np.where(self.level_matrix == 1))))
        for wall in self.blocks:
            Sprites.Wall(self, wall)
        # "for text in self.blocks:
        # ""   print(text)
        self.projection_plane = (320 / math.tan(math.radians(FOV / 2)))
        #print(self.projection_plane)
        self.block_image = pg.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.block_image.fill(COLOURS["RED"])
        self.running = True
        pg.init()
        self.master_screen = pg.display.set_mode((1280, 640))
        self.left_slave = pg.Surface((640, 640))
        self.right_slave = pg.Surface((640, 640))
        self.clock = pg.time.Clock()
        self.player = Sprites.Player(self)
        self.game_loop()

    def quit(self):

        pg.quit()
        sys.exit()

    def game_loop(self):
        while self.running:
            self.events()
            self.update()
            self.render()

            pg.display.flip()
            self.clock.tick(-1)
            pg.display.set_caption(str(int(self.clock.get_fps())))

    @staticmethod
    def events():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    def update(self):
        self.image_sprites.update()

    def render(self):
        ray_array = self.player.ray_casting()
        # print (ray_array)
        self.left_slave.fill(COLOURS["OPAQUE"])
        pg.draw.line(self.left_slave, COLOURS["RED"], self.player.position,
                     self.player.position + pg.math.Vector2(50, 0).rotate(self.player.rotation))

        for block in self.blocks:
            self.left_slave.blit(self.block_image, (block[0] * BLOCK_SIZE, block[1] * BLOCK_SIZE))
        self.image_sprites.draw(self.left_slave)

        for row in range(len(self.level_matrix)):
            pg.draw.line(self.left_slave, COLOURS["GRAY"], (row * BLOCK_SIZE, 0), (row * BLOCK_SIZE, 640))
            pg.draw.line(self.left_slave, COLOURS["GRAY"], (0, row * BLOCK_SIZE), (640, row * BLOCK_SIZE))

        #for ray in ray_array:
         #   pg.draw.line(self.left_slave, COLOURS["BLUE"], self.player.position, (ray[0], ray[1]))

        self.master_screen.blit(self.left_slave, (0, 0))

        self.render_raycast(ray_array)

    def render_raycast(self, ray_array):
        self.right_slave.fill(COLOURS["GRAY"])
        sky = pg.Rect(0, -320, 640, 640)
        pg.draw.rect(self.right_slave, COLOURS["BLUE"], sky)

        for pos, line in enumerate(ray_array):
            height = math.ceil(BLOCK_SIZE / line[2] * self.projection_plane)
            colour = COLOURS["YELLOW"].copy()
            colour *= (abs(line[2] - 640) / 640) * 0.8
            column = pg.Rect((pos, 320 - height / 2), (1, height))
            pg.draw.rect(self.right_slave, colour, column)

        self.master_screen.blit(self.right_slave, (640, 0))


class Sprites:
    class Player(pg.sprite.Sprite):
        def __init__(self, game):
            self.game = game
            self.calc_aid = CalculationAids()
            self.all_sprites = game.image_sprites
            pg.sprite.Sprite.__init__(self, self.all_sprites)
            self.image = pg.Surface((25, 25))
            self.image.fill(COLOURS["GREEN"])

            self.position = pg.math.Vector2(255, 255)
            self.rect = self.image.get_rect()
            self.rect.center = self.position
            self.rotation = float(0)
            self.angle_array = np.linspace(-20, 20, 10)
            self.number_of_rays = 640
            self.acceleration = pg.math.Vector2(0, 0)

        def wall_collision(self, rot):
            old_position = self.position - self.acceleration.rotate(rot)
            hits = pg.sprite.spritecollide(self, self.game.wall_sprites, False)
            if hits:
                for hit in hits:
                    print(hit)



        def update(self):
            self.acceleration.xy = (0, 0)
            rot = 0
            # poll keys
            keys = pg.key.get_pressed()
            if keys[pg.K_UP]: self.acceleration.x += 1
            if keys[pg.K_DOWN]: self.acceleration.x += -0.5
            if keys[pg.K_z]: self.acceleration.y += -0.5
            if keys[pg.K_x]: self.acceleration.y += 0.5
            if keys[pg.K_LEFT]: rot += -1
            if keys[pg.K_RIGHT]: rot += 1

            self.rotation += rot
            self.rotation %= 360

            self.position += self.acceleration.rotate(self.rotation)

            self.rect.center = self.position

            self.wall_collision(rot)

        def ray_casting(self):
            #if LEGACY_RAYCAST: return self.legacy_ray_cast()
            result_array = np.zeros(self.number_of_rays, dtype="f,f,f")
            self.angle_array = np.linspace(-20, 20, self.number_of_rays)
            self.angle_array += self.rotation
            self.angle_array %= 360

            for pos, angle in enumerate(self.angle_array):
                result_array[pos] = cast_ray(pos, angle, self.rotation, self.position.x, self.position.y, self.game.level_matrix, self.game.level_size)

            return result_array


        def legacy_ray_cast(self):
            result_array = np.zeros(self.number_of_rays, dtype="f,f,f")
            level_matrix = self.game.level_matrix
            position = self.position
            self.angle_array = np.linspace(-20, 20, self.number_of_rays)
            self.angle_array += self.rotation
            self.angle_array %= 360

            def traversing_x(ray, end):
                # print("X value is", x)
                position_x, position_y = self.position.x + (ray * x), self.position.y + (ray * y)
                position_x = round(position_x, 3)
                position_y = round(position_y, 3)
                position = None
                if end: return ray, (position_x, position_y), end

                block_coordinates = self.calc_aid.pixels_to_matrix_address((position_x, position_y))
                if x < 0: block_coordinates[0] -= 1
                # if y < 0: block_coordinates[1] -= 1
                block_coordinates = tuple(block_coordinates)
                if block_coordinates[0] < 0 or block_coordinates[1] < 0:
                    end = True
                    return ray, (position_x, position_y), end
                if block_coordinates[0] >= self.game.level_size[0] or block_coordinates[1] >= self.game.level_size[
                    1]:
                    end = True
                    return ray, (position_x, position_y), end
                if level_matrix[block_coordinates]:
                    # print("Hit in x, position:", (position_x,position_y), "IE:", block_coordinates)
                    end = True
                    return ray, (position_x, position_y), end
                # print("No hit in x, position:", (position_x,position_y), "IE:", block_coordinates)

                ray += sx(BLOCK_SIZE)
                return ray, (position_x, position_y), end

            def traversing_y(ray, end):
                # print("Y-value is", y )
                position_x, position_y = self.position.x + (ray * x), self.position.y + (ray * y)
                position_x = round(position_x, 3)
                position_y = round(position_y, 3)
                if end: return ray, (position_x, position_y), end

                block_coordinates = self.calc_aid.pixels_to_matrix_address((position_x, position_y))
                # if x < 0: block_coordinates[0] -= 1
                if y < 0: block_coordinates[1] -= 1
                block_coordinates = tuple(block_coordinates)
                if block_coordinates[0] < 0 or block_coordinates[1] < 0:
                    end = True
                    return ray, (position_x, position_y), end
                if block_coordinates[0] >= self.game.level_size[0] or block_coordinates[1] >= self.game.level_size[
                    1]:
                    # print("bloch outside field")
                    end = True
                    return ray, (position_x, position_y), end
                if level_matrix[block_coordinates]:
                    # print("Hit in y, position:", (position_x,position_y), "IE:", block_coordinates)
                    end = True
                    return ray, (position_x, position_y), end
                # print("NO hit in y, position:", (position_x,position_y), "IE:",block_coordinates)
                ray += sy(BLOCK_SIZE)
                return ray, (position_x, position_y), end

            for pos, angle in enumerate(self.angle_array):
                radians = math.radians(angle + 0.01)
                fisheye = math.cos(radians - math.radians(self.rotation))
                x = math.cos(radians)
                y = math.sin(radians)
                x_ray = 0
                y_ray = 0
                x_at_end = False
                y_at_end = False
                position_x = self.position.x
                position_y = self.position.y
                current_position_x_x = self.position.x
                current_position_x_y = self.position.y
                current_position_y_x = self.position.x
                current_position_y_y = self.position.y
                # current_position_x = pg.math.Vector2(self.position)
                # current_position_y = pg.math.Vector2(self.position)
                sx = lambda length=1: (length * (math.sqrt((1 ** 2) + ((y / x) ** 2))))
                sy = lambda length=1: (length * (math.sqrt((1 ** 2) + ((x / y) ** 2))))

                # getting into blocks

                if x < 0: x_ray += sx(position.x - (int(position.x / BLOCK_SIZE) * BLOCK_SIZE - 0))
                if x > 0: x_ray += sx(abs(position.x - (int(position.x / BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE)))
                if y < 0: y_ray += sy(position.y - (int(position.y / BLOCK_SIZE) * BLOCK_SIZE - 0))
                if y > 0: y_ray += sy(abs(position.y - (int(position.y / BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE)))

                # starting traversing loop
                while not x_at_end or not y_at_end:
                    if x_ray <= y_ray:
                        # print("X-ray is smaller than y-ray (or equal)")
                        if not x_at_end:
                            x_ray, (current_position_x_x, current_position_x_y), x_at_end = traversing_x(x_ray,
                                                                                                         x_at_end)
                            continue

                        else:
                            # print("but because x is at end, y is called ")
                            y_ray, (current_position_y_x, current_position_y_y), y_at_end = traversing_y(y_ray,
                                                                                                         y_at_end)
                            continue

                    else:
                        # print("y-ray is smaller than x-ray")
                        if not y_at_end:
                            y_ray, (current_position_y_x, current_position_y_y), y_at_end = traversing_y(y_ray,
                                                                                                         y_at_end)
                            continue

                        else:
                            x_ray, (current_position_x_x, current_position_x_y), x_at_end = traversing_x(x_ray,
                                                                                                         x_at_end)
                            continue

                # current_position_x_x = position.x + (x_ray * x)
                # current_position_x_y = position.y + (x_ray * y)
                # current_position_y_x = position.x + (y_ray * x)
                # current_position_y_y = position.y + (y_ray * y)
                x_ray *= fisheye
                y_ray *= fisheye

                final_result = (current_position_x_x, current_position_x_y, x_ray)
                if x_ray > y_ray: final_result = (current_position_y_x, current_position_y_y, y_ray)
                result_array[pos] = final_result

            return result_array

    class Wall(pg.sprite.Sprite):
        def __init__(self, game, position):
            self.position = pg.math.Vector2(position[0] * BLOCK_SIZE, position[1] * BLOCK_SIZE)
            self.game = game
            pg.sprite.Sprite.__init__(self, game.wall_sprites)
            self.rect = pg.Rect(self.position, (BLOCK_SIZE,BLOCK_SIZE))




if __name__ == '__main__':
    print("This script is not be run independently")
    sys.exit()
