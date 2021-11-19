import numpy as np
from itertools import groupby


data = np.array(
    [0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 2, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0, 2,
        2, 2, 0, 0, 0, 2, 2, 0, 2, 2, 2, 0, 0, 0, 2, 1, 1, 3, 2, 3, 3, 2, 2, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 1,
        3, 0, 0, 3, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0])
    #data = line_color(data, noise_level=3)
    
    
def OrderCheck(data, noise_level, order):
    grouped = ([list(g) for k, g in groupby(data)])
    for i in grouped:
        if len(i) < noise_level:
            i.clear()
    filtered = [x for x in grouped if x != []]
    flat_list = [item for sublist in filtered for item in sublist]
    #print(flat_list)
    ordered_colors = ([k for k, g in groupby(flat_list)])
    print(ordered_colors)
    order_exists = (order in zip(ordered_colors, ordered_colors[1:],ordered_colors[2:], ordered_colors[3:]))
    return order_exists
print(OrderCheck(data,2,(1,3,2,3)))