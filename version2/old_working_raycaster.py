

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