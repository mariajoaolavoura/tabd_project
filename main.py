"""
Nenhum encontro com infetados. Taxi não infetado. Total de min de encontros com infetados = 0.
X encontros com infetados. Total de min < 10. Taxi não infetado. Total de min de encontro com infetados = soma dos min de cada encontro
Y encontros com infetados. Total de min >= 10. Taxi infetado. Total de min de encontro com infetados = -1

d = dictionary( key=pos_do_taxi, value=[infected, counter] ) # Flag=0? não infetado : infetado. A flag pode poupar-nos algumas comparações

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

## Imports
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
import datetime
import csv
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register

#Functions
def update_to_infected(pos):
    inf, c = taxis_info[pos]
    taxis_info[pos] = [1, c]

def distanceUnder(dist, lista, coord):
    index_coord = []
    j=0
    for i in lista:
        if(math.hypot((i[0]-coord[0]),(i[1]-coord[1])) < dist):
            index_coord.append(j)
        j+=1
    #return list(filter(lambda i: math.hypot((i[0]-coord[0]),(i[1]-coord[1])) < dist , lista))  
    return index_coord
    


conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)
cursor_psql = conn.cursor()

sql = """select distinct taxi from tracks order by 1"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

taxi_id_position = {}
pos = 0
for taxi_id in results:
    taxi_id_position[ int(taxi_id[0]) ] = pos
    pos += 1

#print(taxi_id_position)

## Read offsets file
offsets = []
"""
[
    [ [x,y], [x,y] ... ],
    [ [x,y], [x,y] ... ],
    ...
]

[
red, r, g, g, g ....
]
"""

with open('./../data/offsets3.csv', 'r') as csvFile:
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


## Initialize dictionary
#d = dictionary{ key=pos_do_taxi, value=[infected, counter] }
n_taxis = len(offsets[0])
taxis_info = {k:[0,0] for k in range(0, n_taxis)}

## 10 first infected taxis
#Porto
taxi_porto = [  20000333,
                20000450,
                20000021,
                20000850,
                20000684,
                20000199,
                20000356,
                20000474,
                20000409,
                20000598
            ]

taxi_position = []
for taxi_id in taxi_porto:
    taxi_position += [ taxi_id_position[taxi_id] ]

for pos in taxi_position:
    update_to_infected(pos)

#Lisboa
taxi_lisboa = [ 20093187,
                20092692,
                20091298,
                20090980,
                20091393,
                20093322,
                20091181,
                20092397,
                20091020,
                20090006
                ]
taxi_position = []
for taxi_id in taxi_lisboa:
    taxi_position += [ taxi_id_position[taxi_id] ]

for pos in taxi_position:
    update_to_infected(pos)


#print(taxis_info)


dummy = [0.000000, 0.000000]
colors, c = [], []
# offsets [ [ [x,y], ... ], [...]]
for row in offsets: # row [ [x,y], ... ]
    for i in range(0, len(row)):
        coord = row[i] # coord [x,y]
        if coord != dummy:
            infected, counter = taxis_info[i]
            if (infected):
                #print("pos="+str(i)+", coor="+str(coord)+", inf="+str(infected)+", counter="+str(counter)+"\n")
                # verify taxis 50m
                pos_neig_50m = distanceUnder(50, row, coord) # position in row of offsets
                #print(pos_neig_50m)
                for pos in pos_neig_50m:
                    coord = row[pos]
                    infected, counter = taxis_info[pos]
                    if (not infected) :
                        counter += 1
                        taxis_info[pos] = [infected, counter]
                        #print("counter ++")
                        #print(taxis_info[pos])
                    if (counter >= 60 and not infected) :
                        update_to_infected(pos)
                        print("update to infected")
                        print(taxis_info[pos])
        #print("\n\n")
        #c += [ "red" if taxis_info[i][0] else "green" ]
    #colors.append(c)   
    #print(colors)
    #print("")

#TODO:
# colors not correct
# 10% - 1min, 10min para infetado, 
# random(1, 10)==5

#print(len(offsets[0]))
#print(len(colors[0]))
# initialization
"""
x,y = [],[]
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])
"""

"""
def animate(i):
    d = datetime.datetime.utcfromtimestamp(ts_i+i*10)
    ax.set_title(d)
    scat.set_offsets(offsets[i])

ts_i = 1570665600
scale=1/3000000

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1

fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

scat = ax.scatter(x,y,s=2,color='orange')
anim = FuncAnimation(fig, animate, interval=10, frames=len(offsets)-1, repeat = False)

plt.draw()
plt.show()

"""