import numpy as np
from itertools import groupby


data = np.array(
    [0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 2, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0, 2,
        2, 2, 0, 0, 0, 2, 2, 0, 2, 2, 2, 0, 0, 0, 2, 1, 1, 3, 2, 3, 3, 2, 2, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 1,
        3, 0, 0, 3, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0])
    #data = line_color(data, noise_level=3)
    
    
def OrderCheck(data, noise_level, order):
    #create list in a list everytime element value changes
    grouped = ([list(g) for k, g in groupby(data)])
    #grouped = [x.clear() if len(x) < noise_level for x in grouped]
    for i in grouped:
       if len(i) < noise_level:
           i.clear()
           # remove empty lists in list
    filtered = [x for x in grouped if x != []]
    #undo what grouped did
    flat_list = [item for sublist in filtered for item in sublist]
    #print(flat_list)
    #groups the same values into one e.g "AAAA" -> "A"
    ordered_colors = ([k for k, g in groupby(flat_list)])
    print(ordered_colors)
    #order must be tuple checks if sequence exists in the list
    order_exists = (order in zip(ordered_colors, ordered_colors[1:],ordered_colors[2:], ordered_colors[3:]))
    return order_exists
print(OrderCheck(data,2,(1,3,2,3)))
