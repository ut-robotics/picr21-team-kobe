from threading import local
import numpy as np
from itertools import groupby
from numba import jit
import timeit


data = np.array(
    [0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 2, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0, 2,
        2, 2, 0, 0, 0, 2, 2, 0, 2, 2, 2, 0, 0, 0, 2, 1, 1, 3, 2, 3, 3, 2, 2, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 3, 1,
        3, 0, 0, 3, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0])
    #data = line_color(data, noise_level=3)
order = np.array([1,1,1])

def Test1(arr, order):
    arr_size = arr.size
    order_size = order.size
    order_range = np.arange(order_size)
    M = (arr[np.arange(arr_size-order_size+1)[:,None] + order_range] == order).all(1)

    if M.any() >0:
        return np.where(np.convolve(M,np.ones((order_size),dtype=int))>0)[0]
    else:
        return []   


def TestReal(arr, noise, order):
    sequence_arr = Test(arr,noise)
    order_exists = Test1(sequence_arr,order)
    #print(arr)
    #print(sequence_arr)
    #print(order_exists)
    return len(order_exists) > 0


@jit(nopython = True, cache = True)   
def Test(data, noise_level):
    data = np.split(data, np.where(np.diff(data[:]))[0]+1)
    new_list = []
    element_counter = 0
    previous_appended = -1
    for i in data:
        if i[0] == 0:
            element_counter += i.size            
            continue
        if i.size + element_counter < noise_level:
            element_counter += i.size
            continue
        if previous_appended == i[0]:
            continue
        previous_appended = i[0]
        new_list.append(i[0])
        element_counter = 0  

    return np.array(new_list)
    

    # Create a 2D array of sliding indices across the entire length of input array.
    # Match up with the input sequence & get the matching starting indices.
    # M = (new_list[np.arange(array_size-seq_size+1)[:,None] + seq_range] == order).all(1)

    # Get the range of those indices as final output
    #return new_list
    #print(data)



def OrderCheck(data, noise_level, order):
    #create list in a list everytime element value changes
    #list(filter(lambda num: num != 0, data))
    data = [value for value in data if value != 0]
    #print(data)
    grouped = ([list(g) for k, g in groupby(data)])
    #grouped = [x.clear() if len(x) < noise_level for x in grouped]
    #print(grouped)
    for i in grouped:

       if len(i) < noise_level:
           i.clear()
           # remove empty lists in list
    filtered = [x for x in grouped if x != []]
    #undo what grouped did
    flat_list = [item for sublist in filtered for item in sublist]
    #groups the same values into one e.g "AAAA" -> "A"
    ordered_colors = ([k for k, g in groupby(flat_list)])
    #print(ordered_colors)
    #order must be tuple checks if sequence exists in the list
    order_exists = (order in zip(ordered_colors, ordered_colors[1:],ordered_colors[2:]))
    return 0
#print(OrderCheck(data,2,(1,3,2,3)))
print(timeit.timeit('TestReal(data,4,order)', globals =locals(), number=1))
#print(timeit.timeit('TestReal(data,10,order)', globals =locals(), number=1))

#print(timeit.timeit('OrderCheck(data,0,(1,1,1))', globals =locals(), number=10))