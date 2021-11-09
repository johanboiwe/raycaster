import pygame as pg
import numpy as np
import math

FOV = 40
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
        self.all_sprites = pg.sprite.Group()
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
        # "for text in self.blocks:
        # ""   print(text)
        self.projection_plane = 320/math.tan(math.radians(20))
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

    def game_loop(self):
        while self.running:
            self.events()
            self.update()
            self.render()

            pg.display.flip()
            self.clock.tick(30)
            pg.display.set_caption(str(int(self.clock.get_fps())))

    @staticmethod
    def events():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    def update(self):
        self.all_sprites.update()

    def render(self):
        ray_array = self.player.ray_casting()
        # print (ray_array)
        self.left_slave.fill(COLOURS["OPAQUE"])
        for ray in ray_array:
            pg.draw.line(self.left_slave, COLOURS["BLUE"], self.player.position, (ray[0], ray[1]))

        for block in self.blocks:
            self.left_slave.blit(self.block_image, (block[0] * BLOCK_SIZE, block[1] * BLOCK_SIZE))
        self.all_sprites.draw(self.left_slave)

        for row in range(len(self.level_matrix)):
            pg.draw.line(self.left_slave, COLOURS["GRAY"], (row * BLOCK_SIZE, 0), (row * BLOCK_SIZE, 640))
            pg.draw.line(self.left_slave, COLOURS["GRAY"], (0, row * BLOCK_SIZE), (640, row * BLOCK_SIZE))
        self.master_screen.blit(self.left_slave, (0, 0))

        self.render_raycast(ray_array)

    def render_raycast(self, ray_array):
        self.right_slave.fill(COLOURS["GRAY"])
        sky = pg.Rect(0, -320, 640, 640)
        pg.draw.rect(self.right_slave, COLOURS["BLUE"], sky)

        for pos, line in enumerate(ray_array):
            height = (640 - line[2])
            colour = COLOURS["YELLOW"].copy()
            colour *= abs(line[2] - 640) / 640

            column = pg.Rect((pos, 640 - height), (1, height))
            pg.draw.rect(self.right_slave, colour, column)

        self.master_screen.blit(self.right_slave, (640, 0))


class Sprites:
    class Player(pg.sprite.Sprite):
        def __init__(self, game):
            self.game = game
            self.calc_aid = CalculationAids()
            self.all_sprites = game.all_sprites
            pg.sprite.Sprite.__init__(self, self.all_sprites)
            self.image = pg.Surface((25, 25))
            self.image.fill(COLOURS["GREEN"])
            self.position = pg.math.Vector2(300, 300)
            self.rect = self.image.get_rect()
            self.rect.center = self.position
            self.rotation = float(0)
            self.angle_array = np.linspace(-20, 20, 10)
            self.number_of_rays = 640
            self.acceleration = pg.math.Vector2(0, 0)

        def update(self):
            self.acceleration.xy = (0, 0)
            rot = 0
            # poll keys
            keys = pg.key.get_pressed()
            if keys[pg.K_UP]: self.acceleration.x += 1
            if keys[pg.K_DOWN]: self.acceleration.x += -0.5
            if keys[pg.K_LEFT]: rot += -1
            if keys[pg.K_RIGHT]: rot += 1

            self.rotation += rot
            self.rotation %= 360

            self.position += self.acceleration.rotate(self.rotation)

            self.rect.center = self.position

        def ray_casting(self):
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
                            x_ray, (current_position_x_x, current_position_x_y), x_at_end = traversing_x(x_ray, x_at_end)
                            # continue

                        else:
                            # print("but because x is at end, y is called ")
                            y_ray, (current_position_y_x, current_position_y_y), y_at_end = traversing_y(y_ray, y_at_end)
                            # continue

                    else:
                        # print("y-ray is smaller than x-ray")
                        if not y_at_end:
                            y_ray, (current_position_y_x, current_position_y_y), y_at_end = traversing_y(y_ray, y_at_end)
                            # continue

                        else:
                            x_ray, (current_position_x_x, current_position_x_y), x_at_end = traversing_x(x_ray, x_at_end)


                #current_position_x_x = position.x + (x_ray * x)
                #current_position_x_y = position.y + (x_ray * y)
                #current_position_y_x = position.x + (y_ray * x)
                #current_position_y_y = position.y + (y_ray * y)
                x_ray *= fisheye
                y_ray *= fisheye

                final_result = (current_position_x_x, current_position_x_y, x_ray)
                if x_ray > y_ray: final_result = (current_position_y_x, current_position_y_y, y_ray)
                result_array[pos] = final_result

            return result_array
