import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register
import datetime
import csv

## Functions
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


## Read files
# Read offsets file
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
        

# Read colors file
colors = []
"""
[
    [ c1, c2, c3, ...],
    [...],
    ...
]
"""
with open('./../data/random_colors.csv', 'r',  newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    i = 0
    for row in reader:
        c = []
        for j in row:
            c.append(j)
        colors.append(c)


# Read taxis_info_history
taxis_info_history = []
"""
[
    { 0:[i,c,c], 1:[], ... }, 
    {...}, 
    ...
]
"""
with open('./../data/random_taxis_info_history.csv', 'r',  newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    i = 0
    for row in reader:
        d = {}
        for j in row:
            k, v = j.split(":")
            v1, v2, v3 = v.split()
            d[int(k)] = [ int(v1), int(v2), int(v3)]
        taxis_info_history.append(d)



## Plots
ts_i = 1570665600
scale=1/3000000

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1

fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))


## Draw districts
conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)

cursor_psql = conn.cursor()
sql = "select distrito,st_union(proj_boundary) from cont_aad_caop2018 group by distrito"
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

xs , ys = [],[]
for row in results:
    geom = row[1]
    if type(geom) is MultiPolygon:
        for pol in geom:
            xys = pol[0].coords
            xs, ys = [],[]
            for (x,y) in xys:
                xs.append(x)
                ys.append(y)
            ax.plot(xs,ys,color='black',lw='0.2')
    if type(geom) is Polygon:
        xys = geom[0].coords
        xs, ys = [],[]
        for (x,y) in xys:
            xs.append(x)
            ys.append(y)
        ax.plot(xs,ys,color='black',lw='0.2')


## Draw taxis
# initialization
x,y = [],[]
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])


scat = ax.scatter(x,y,s=2)
anim = FuncAnimation(fig, animate, interval=10, frames=len(offsets)-1, repeat = False)

plt.draw()
plt.show()
