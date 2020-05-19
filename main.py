"""
Nenhum encontro com infetados. Taxi não infetado. Total de min de encontros com infetados = 0.
X encontros com infetados. Total de min < 10. Taxi não infetado. Total de min de encontro com infetados = soma dos min de cada encontro
Y encontros com infetados. Total de min >= 10. Taxi infetado. Total de min de encontro com infetados = -1

taxis_info = dictionary( key=taxi_column, value=[infected, contact_time, transmission] ) 
# infected=0? not infected : infected. 
# contact_time - ts counter of contact time
# transmission - counter of number of taxis the current taxi infected

# Pseudo-codigo
For row in offset:
    for i in range(0, len(row)):
        coord = row[i]
        if coord != dummy:
            infected, contact_time, transmission = d[i]
            if (infected):
                # verify taxis 50m
                # sqtr( (x1-x2)^2 + (y1-y2)^2) < 50
                neig_50m = [] # position in offsets
                for pos in neig_50m:
                    coord = row[pos]
                    infected, contact_time = d[pos]
                    if ( not infected  ) :
                            contact_time ++
                    if ( contact_time >= 60 & not inflected) :
                            update neighbour state to infected 
                            transmission ++
                


"""

"""
Tasks distribution:
Fernando - Mapa, tracks
Lúcia - Histograms, grafico curva exponencial
MJ - Zooms, size
"""

## Imports
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
import datetime
import csv
import random
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register

## Functions
def update_to_infected(pos):
    inf, c, t = taxis_info[pos]
    taxis_info[pos] = [1, c, t]

def distanceUnder(dist, lista, coord):
    index_coord = []
    j=0
    for i in lista:
        if(math.hypot((i[0]-coord[0]),(i[1]-coord[1])) < dist):
            index_coord.append(j)
        j+=1
    #return list(filter(lambda i: math.hypot((i[0]-coord[0]),(i[1]-coord[1])) < dist , lista))  
    return index_coord
    

## Get the match between taxi's id in the db with that taxi's column in offsets.
## Create a dict { key=taxi_id_db, value=offsets_columns}
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


## Read offsets file
offsets = []
"""
[
    [ [x,y], [x,y] ... ],
    [ [x,y], [x,y] ... ],
    ...
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
## taxis_info = dictionary{ key=offsets_column, value=[infected, contact_time, transmission] }
n_taxis = len(offsets[0])
taxis_info = {k:[0,0,0] for k in range(0, n_taxis)}

## Update the taxis_info with 10 first infected taxis

# From Porto
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

# From Lisboa
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



"""
offsets [ [ [x,y], ... ], [...], ... ]
colors [ [ c1, c2, c3, ...], [...], ... ]
taxis_info_history [ { 0:[i,c,c], 1:[], ... }, {...}, ... ]
"""

dummy = [0.000000, 0.000000]
taxis_info_history, colors, c = [], [], []

ts_to_infected = 60 # ts = 10s, 1min= 6 ts, 10min = 60 ts
infection_radius = 50

for row in offsets: # row [ [x,y], ... ]
    for taxi_column in range(0, len(row)):
        coord = row[taxi_column] # coord [x,y]
        if coord != dummy:
            infected, contact_time, transmission = taxis_info[taxi_column]
            # if taxi is infected
            if (infected):
                # verify its neighbours taxis within 50m
                column_neig_50m = distanceUnder(infection_radius, row, coord) # column in row of offsets
                for neig_column in column_neig_50m:
                    coord = row[neig_column]
                    neig_infected, neig_contact_time, neig_transmission = taxis_info[neig_column]
                    
                    # if its neighbour is not infected
                    if (not neig_infected):
                        # update the contact time of that neighbour
                        neig_contact_time += 1
                        taxis_info[neig_column] = [neig_infected, neig_contact_time, neig_transmission]
                        #print("update neig_contact_time " + str(neig_column) + " " + str(taxis_info[neig_column]))
                
                    #if (neig_contact_time >= ts_to_infected and not neig_infected): # if that neigbour reaches the 10min contact, cumulative
                    
                    # if that neighbour is not infected and reached 1min contact
                    if (not neig_infected and neig_contact_time >= 6):
                        # guarantee that it's only 10% probability of contamination
                        if(random.randrange(1, 101 , 1)<=10):    
                            # update that neigbour to infected
                            update_to_infected(neig_column)
                            # update number of taxis this taxi infected
                            transmission += 1
                            taxis_info[taxi_column] = [infected, contact_time, transmission]
                            #print("update to infected " + str(neig_column) + " " + str(taxis_info[neig_column]))
                            #print("update transmission " + str(taxi_column) + " " + str(taxis_info[taxi_column]))
                        
                        # if not 10%, it's not infected and nedds to wait another minute
                        else:
                            taxis_info[neig_column] = [0, 0, 0]

            #print(taxis_info[taxi_column])
        infected = taxis_info[taxi_column][0]
        c += [ "red" if infected else "green" ]
    
    colors.append(c)  
    c = [] 
    print(len(colors))
    #print("\n\n")

"""
import csv
with open("./../data/colors.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(colors)

with open("./../data/taxis_info_history.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(taxis_info)
"""

# initialization
x,y = [],[]
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])


"""
prof animate:
def animate(i):
    ax.set_title(datetime.datetime.utcfromtimestamp(ts_i+i*10))
    sizes = np.random.randint(50,size=1660)
    colors = np.random.random(size=(1660,3))
    scat.set_facecolors(colors)
    scat.set_sizes(sizes)
    scat.set_offsets(offsets[i])
"""


def animate(i):
    d = datetime.datetime.utcfromtimestamp(ts_i+i*10)
    ax.set_title(d)
    scat.set_offsets(offsets[i])
    scat.set_facecolor(colors[i])
    

# Plots
ts_i = 1570665600
scale=1/3000000

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1

fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

scat = ax.scatter(x,y,s=2)
anim = FuncAnimation(fig, animate, interval=10, frames=len(offsets)-1, repeat = False)

plt.draw()
plt.show()
