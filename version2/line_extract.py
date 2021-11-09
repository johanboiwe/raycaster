import math

import numpy as np


def extract_line(matrix, start_coordinates, end_coordinates):
    x0 = start_coordinates[0]
    y0 = start_coordinates[1]
    x1 = end_coordinates[0]
    y1 = end_coordinates[1]
    #length= int(math.sqrt(((x1 - x0)**2)+((y1 - y0)**2)))
    length = int(math.ceil(((x1-x0) + (y1-y0))/2))
    print(length)
    x, y = np.linspace(x0, x1, length), np.linspace(y0, y1, length)
    zi = matrix[x.astype(np.int_), y.astype(np.int_)]
    return zi



#array = np.zeros(100, dtype=np.int_)
#for i in range(len(array)):
#    array[i] = i
#array = array.reshape((10, 10))
#print (array, "\n")
#print(extract_line(array, (0,0), (9,8)))


