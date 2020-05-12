"""
Nenhum encontro com infetados. Taxi não infetado. Total de min de encontros com infetados = 0.
X encontros com infetados. Total de min < 10. Taxi não infetado. Total de min de encontro com infetados = soma dos min de cada encontro
Y encontros com infetados. Total de min >= 10. Taxi infetado. Total de min de encontro com infetados = -1

d = dictionary( key=pos_do_taxi, value=[flag, counter] ) # Flag=0? não infetado : infetado. A flag pode poupar-nos algumas comparações

For row in offset:
    for i in range(0, len(row)):
        coord = row[i]
        if coord != dummy:
            infected, counter = d[i]
            if (infected):
                    # verify taxis 50m
                    # sqtr( (x1-x2)^2 + (y1-y2)^2) < 50
                    neig_50m = [] # position in offsets
                    for pos in neig_50m:
                        coord = row[pos]
                        infected, counter = d[pos]
                        if ( not infected  ) :
                                counter ++
                        if ( counter >= 600 & not inflected) :
                                update neighbour state to infected 

"""
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
import datetime
import csv
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register

ts_i = 1570665600
scale=1/3000000

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1

fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))


offsets = []
"""
[
    [ [x,y], [x,y] ... ],
    [ [x,y], [x,y] ... ],
    ...
]


[
    [ [x,y], [x,y] ... ]
]


[
    [x,y], [x,y] ... 
]
"""
with open('./offsets3.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    i = 0
    for row in reader:
        l = []
        for j in row:
            x,y = j.split()
            x = float(x)
            y= float(y)
            l.append([x,y])
        offsets.append(l)
        

print(len(offsets[0]))
"""
x,y = [],[]
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])
"""
