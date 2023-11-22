import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import distance
plt.ion()


# Challenge: 
# design an algorithm which draws a graph over a given set of coordinates
# two coordinates can only be connected by a straight line 
# the angle between two lines must be 90 degrees or greater
# -> special case of travelling sales man problem
# create a brute-force algorithm to prove if set of coordinates is unsolvable


# still unfinished: algorithm gets slow at hgígh level of recursion & haven´t found satisfying solution to selecting the starting coordinates




def closest_node(node, nodes):
    x = distance.cdist([node], nodes).argmin()
    return x

#optional
def update_plot(path):
    
    x,y = path.T
    line.set_data(x,y)
    fig.canvas.draw()
    fig.canvas.flush_events()
    

# recursive function
def next_node(coordinates, path):
    global mean
    
    coordinates = np.copy(coordinates)
    path = np.copy(path)

    #return if path is finished, also 1 as confirmation signal
    if not np.any(coordinates):
        print("jetzt")
        return path, 1

    #vector connecting last two nodes
    x = (path[-1] - path[-2])

    #normal vector to x
    sep_line = np.array([x[1],-x[0]])

    #sort nodes according to ratio: (dist. last node) / (dist. centroid)
    coordinates = coordinates[(((path[-1][0] - coordinates[:,0])**2 + (path[-1][1] - coordinates[:,1])**2)/
                              ((mean[0] - coordinates[:,0])**2 +(mean[1] - coordinates[:,1])**2))
                              .argsort()]

    for i in range (len(coordinates)):
        
        #if node is above sep_line (angle greater than 90 degrees)
        if float(np.cross(coordinates[i] - path[-1], sep_line)) < 0:

            #node is appended to path and deleted from coordinates, than fed back to function
            path1 = np.append(path, [coordinates[i]], axis = 0)
            coordinates1 = np.delete(coordinates, i, 0)

            ## include Animation, if wished:
            # remove for greater speed & efficiency

            update_plot(path1)




            a,b = next_node(coordinates1, path1)

            #returning if signal is positive (path terminated)
            if b == 1:
                return a, 1

    #returning 0 to signal that path could not be finished
    return path, 0
    

#select file of interest    
coordinates = np.loadtxt("wenigerkrumm4.txt", delimiter = " ")
coordinates_copy = np.copy(coordinates)


### Select Starting Points ###
# still struggling here; current strategy: select node farthest away from centroid & the second node is closest to first one
# works well for some problems, but very bad e.g. for file 3

#sort according to distance from centroid
mean = np.mean(coordinates, axis=0)
coordinates = coordinates[((mean[0] - coordinates[:,0])**2 +(mean[1] - coordinates[:,1])**2).argsort()]


#first node of path
path = np.array([coordinates[-1]])
coordinates = np.delete(coordinates, -1, 0)

#second
x = closest_node(path[-1], coordinates)
path = np.append(path, [coordinates[x]], axis = 0)
coordinates = np.delete(coordinates, x, 0)



#creating plot
plt.ion()
fig = plt.figure()
ax = fig.add_subplot()
a,b = coordinates_copy.T
points = ax.scatter(a,b)
x,y = path.T
line, = ax.plot(x,y)
plt.axis("scaled")
fig.canvas.draw()

print("los")
path, z = next_node(coordinates, path)

if z == 0:
    print("nö")

#show graph if could be finished
else:
    x,y = path.T
    plt.plot(x,y, c="RoyalBlue")
    plt.axis("scaled")
    plt.show(block=True)

