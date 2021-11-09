import pygame as pg
import numpy as np
import math
COLOURS = {
    "OPAQUE" : (255 ,255 ,255 ,255),
    "BLACK" : (0,0,0,0),
    "GREEN" :(0,255,0,0),
    "RED":  (255,0,0,0),
    "BLUE": (0,0,255,0)
}

BLOCK_SIZE = 64
RAY_GAP = float(np.float_(60 / 640))


class Game:
    def __init__(self):
        self.allSprites = pg.sprite.Group()
        level =[
            "WWWWWWWWWW",
            "W..W..W..W",
            "W..W..W..W",
            "W..W..W..W",
            "W........W",
            "W.....W..W",
            "W....WWWWW",
            "W........W",
            "W........W",
            "WWWWWWWWWW"
            ]
        self.level_matrix = np.zeros((len(level), len(level[0])), dtype= np.uint8)
        for x, line in enumerate(level):
            for y, block in enumerate(line):
                if block == "W": self.level_matrix[x][y] = 1
                elif block == ".": self.level_matrix[x][y] = 0

        self.running = True
        pg.init()
        self.master_screen = pg.display.set_mode((1280, 640))
        self.left_slave = pg.Surface((640,640))
        self.right_slave = pg.Surface((640,640))
        self.block = pg.image.load("version1/bricksx64.png")
        self.player = Sprites.Player(self)
        self.clock = pg.time.Clock()

        self.game_loop()


    def game_loop(self):
        while self.running:
            self.events()
            self.update()
            self.render()

            pg.display.flip()
            self.clock.tick(60)
            pg.display.set_caption(str(self.clock))



    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    def update(self):
        self.allSprites.update()


    def render(self):

        #left
        self.left_slave.fill(COLOURS["OPAQUE"])
        blocks = (tuple(zip(*np.where(self.level_matrix == 1))))
        for block in blocks:
            self.left_slave.blit(self.block, (block[0]*BLOCK_SIZE, block[1] * BLOCK_SIZE))
        self.allSprites.draw(self.left_slave)
        self.player.draw()
        self.master_screen.blit(self.left_slave, (0,0))

        #right
        self.right_slave.fill((COLOURS["BLUE"]))
        horizon = pg.Rect(0,520,640,640)


        pg.draw.rect(self.right_slave, COLOURS["BLACK"], horizon)
        for pixelcolumn, ray in enumerate(self.player.ray_array):
            length = int((abs(self.player.position.distance_to((ray[1][0], ray[1][1])))) * math.cos(self.player.rotation - self.player.rotation-30))
            colour = COLOURS["RED"]
            colour = (colour[0],int(colour[1]+length*3),colour[2],(int(colour[3])))
            print(colour)

            column_surface = pg.Surface((1, (1280-length)/4))
            #print(column_surface)
            if self.level_matrix[int(ray[0][0])][int(ray[0][1])]: column_surface.fill(colour)
        #    if self.level_matrix[int(ray[0][0])][int(ray[0][1])]:
        #        image = self.block
        #    else: continue
        #    column_surface = pg.Surface((1,64))
#
 #           offset =round(ray[1][0]%BLOCK_SIZE)
#
 #           column_surface.blit(image,(1 - offset, 0))
            self.right_slave.blit(column_surface, (pixelcolumn, 520 - (1280-length)/4))




        self.master_screen.blit(self.right_slave, (640, 0))




class Sprites:
    class Player(pg.sprite.Sprite):
        def __init__(self, game):
            self.game = game
            self.all_sprites = game.allSprites
            pg.sprite.Sprite.__init__(self, self.all_sprites)
            self.image = pg.Surface((25,25))
            self.image.fill(COLOURS["GREEN"])
            self.position = pg.math.Vector2(500,500)
            self.rotation_vector = pg.math.Vector2(0,50)
            self.rect = self.image.get_rect()
            self.rect.center = self.position
            self.rotation = float()
            self.angle_array = np.linspace(0, 1, 640)
            self.emty_ray_array = np.zeros((len(self.angle_array), 2, 2))
            self.ray_array = self.emty_ray_array.copy()


        def update(self):
            def ray_casting():
                self.angle_array = np.linspace(-30+ self.rotation, 30 + self.rotation, 640)
                self.ray_array = self.emty_ray_array.copy()
                for pos, angle in enumerate(self.angle_array):
                    vectorised_angle = pg.math.Vector2(1,1).rotate(angle%360)
                    for length in range(1,640):
                        end_point = (vectorised_angle * length) + self.position
                        if self.game.level_matrix[int(end_point.x/BLOCK_SIZE)][int(end_point.y/BLOCK_SIZE)]:

                            self.ray_array[pos][0][0] = int(end_point.x/BLOCK_SIZE)
                            self.ray_array[pos][0][1] = int(end_point.y/BLOCK_SIZE)
                            self.ray_array[pos][1][0] = end_point.x
                            self.ray_array[pos][1][1] = end_point.y
                            break


            self.rotation +=1
            self.rotation %= 360
            #print(self.rotation)


            ray_casting()





        def draw(self):
            for ray in self.ray_array:

                #print(ray)
                pg.draw.line(self.game.left_slave, COLOURS["RED"], self.position, (ray[1]))






if __name__ == '__main__': exit()


