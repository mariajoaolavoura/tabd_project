
## Imports
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.animation import FuncAnimation, FFMpegWriter
import datetime
import csv
import random
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import rcParams

def distanceUnder(dist, list, coord, color, rangeVal, maxVal):
    j = 0
    for i in range(rangeVal):
        x = list[i,0:1][0]
        if((list[i,0:1] != coord[0] or
          list[i,1:2] != coord[1])): #and 
            if(color[i] == 'green'): #and 
                if((math.hypot((list[i,0:1][0] - coord[0][0]), (list[i,1:2][0] - coord[1][0]))) < dist):
                    j+=1
    percent = (0.1*j)*100%100
    if(j>=10):
        return  100
    if (j>0):
        return percent
    if(j==0):
        return 0


### Read offsets file
offsets = []

with open('./../data/offsets3.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    i = 0
    for row in reader:
        l = []
        for j in row:
            x,y = j.split()
            x = float(x)
            y = float(y)
            z = float(0.0)
            l.append([x,y,z])
        offsets.append(np.array(l))

#How to read colors from file:
colors = []
with open('./../data/random_colors.csv', 'r',  newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    i = 0
    for row in reader:
        c = []
        for j in row:
            c.append(j)
        colors.append(c)

def animate(iteration, offsets, scatters, colors):
    d = datetime.datetime.utcfromtimestamp(ts_i + iteration * 10)
    ax.set_title(d)
    angle = iteration%360
    ax.view_init(25, angle)
    for i in range(offsets[0].shape[0]):
        if(colors[iteration][i] == 'green'):            
            x, y, z = offsets[iteration][i,0:1], offsets[iteration][i,1:2], offsets[iteration][i,2:]
            scatters[i]._offsets3d = (x, y, z)
            scatters[i]._facecolor3d[0] = [0., 1., 0., 1.]
        if(colors[iteration][i] == 'red'):
            x, y, z = offsets[iteration][i,0:1], offsets[iteration][i,1:2], offsets[iteration][i,2:]
            z = float(distanceUnder(50, offsets[iteration], [x, y], colors[iteration], offsets[0].shape[0], 10))
            scatters[i]._offsets3d = (x, y, z)
            scatters[i]._facecolor3d[0] = [1., 0., 0., 1.]
        



# Plots
ts_i = 1570665600
scale = 1 / 3000000

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max - xs_min) / 0.0254 * 1.1
height_in_inches = (ys_max - ys_min) / 0.0254 * 1.1

fig = plt.figure(figsize=(height_in_inches*scale, width_in_inches*scale))

ax = p3.Axes3D(fig)

ax.set_xlim3d([xs_min, xs_max])
ax.set_xlabel('X')

ax.set_ylim3d([ys_min, ys_max])
ax.set_ylabel('Y')

ax.set_zlim3d([0, 100])
ax.set_zlabel('Probabilidade de Infeção')

ax.set_title('3D Animated Scatter Example')

# Provide starting angle for the view.
ax.view_init(0, 5)

x, y, z = [], [], []
for i in range(offsets[0].shape[0]):
   x.append(offsets[0][i,0:1])
   y.append(offsets[0][i,1:2])
   z.append(offsets[0][i,2:])
# Initialize scatters
scatters = [ ax.scatter(x[i], y[i], z[i], color = "Green")  for i in range(offsets[0].shape[0])]

iterations = len(offsets)
anim = FuncAnimation(fig, animate, iterations, fargs=(offsets, scatters, colors),
                                       interval=10, blit=False, repeat=False)

# save to video
rcParams['animation.ffmpeg_path'] =r'C:\Users\Fernando Nogueira\Desktop\PythonApplication1\PythonApplication1\ffmpeg-20200628-4cfcfb3-win64-static\bin\ffmpeg.exe'
writer = FFMpegWriter(fps=60)
anim.save('plot3DPart2.mp4', writer=writer)

plt.draw()
plt.show()
