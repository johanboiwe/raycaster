

    # at this point, current positions needs to be align with blocks



            # continue
    # print(x_ray, y_ray, x_at_end, y_at_end)

    # final adjustment
x_ray = x_ray * fisheye
y_ray = y_ray * fisheye
# current_position_x_x = self.position.x + (x_ray * x)
# current_position_x_y = self.position.y +(x_ray * y)

# current_position_y_x = self.position.x + (y_ray * x)
# current_position_y_y = self.position.y + (y_ray * y)

# pg.draw.line(self.game.left_slave, COLOURS["BLUE"], self.position, (current_position_x_x,current_position_x_y), width= 9)
# pg.draw.line(self.game.left_slave, COLOURS["YELLOW"], self.position, (current_position_y_x, current_position_y_y), width=5)
# print(type(current_position_x_x))
final_position = (current_position_x_x, current_position_x_y, x_ray)
if y_ray < x_ray: final_position = (current_position_y_x, current_position_y_y, y_ray)
# print(final_position)
result_array[pos] = final_position
# pg.draw.line(self.game.left_slave, COLOURS["GREEN"], self.position, final_position, width=7)
# input()

return result_array


def ray_casting():
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
                    x_ray, (current_position_x_x, current_position_x_y), x_at_end = traversing_x(x_ray,
                                                                                                 x_at_end)
                    # continue

                else:
                    # print("but because x is at end, y is called ")
                    y_ray, (current_position_y_x, current_position_y_y), y_at_end = traversing_y(y_ray,
                                                                                                 y_at_end)
                    # continue

            else:
                # print("y-ray is smaller than x-ray")
                if not y_at_end:
                    y_ray, (current_position_y_x, current_position_y_y), y_at_end = traversing_y(y_ray,
                                                                                                 y_at_end)
                    # continue

                else:
                    x_ray, (current_position_x_x, current_position_x_y), x_at_end = traversing_x(x_ray,
                                                                                                 x_at_end)

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