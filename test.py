import numpy as np
import psycopg2
from postgis.psycopg import register
import matplotlib.pyplot as plt
#import math
from matplotlib.animation import FuncAnimation
#import datetime
from postgis import Polygon,MultiPolygon



def animate(i):
    ax.set_title(datetime.datetime.utcfromtimestamp(ts_i+i*10))
    scat.set_offsets(offsets[i])


scale=1/3000000
xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1

fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

ts_i = 1570665700
ts_f = 1570665800 #1570667000
step = 10

array_size = int(24*60*60/step)



conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)
cursor_psql = conn.cursor()

sql = """select distinct taxi from tracks order by 1"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

taxis_x ={}
taxis_y ={}

for row in results:
    taxis_x[int(row[0])] = np.zeros(array_size)
    taxis_y[int(row[0])] = np.zeros(array_size)



for i in range(ts_i,ts_f,step):
    sql =   "select tr1.taxi as taxi_1, tr2.taxi as taxi_2, tr1.ts as ts, st_distance(tr1.proj_track, tr2.proj_track) as dist, st_pointn(tr1.proj_track, " + str(i) + "-tr1.ts) from tracks as tr1, tracks as tr2 where tr1.taxi != tr2.taxi and tr1.ts = tr2.ts and st_distance(tr1.proj_track, tr2.proj_track) <= 50 and tr1.ts<" + str(i) + " and tr1.ts+st_numpoints(tr1.proj_track)> " + str(i) + " order by tr1.ts asc;"
            
    cursor_psql.execute(sql)
    results = cursor_psql.fetchall()
    #print(results)

    for row in results:
        x,y = row[4].coords
        taxis_x[int(row[0])][int((i-ts_i)/step)] = x
        taxis_y[int(row[0])][int((i-ts_i)/step)] = y
        #print(x)
        #print(y)

offsets = []
for i in range(array_size):
    l = []
    for j in taxis_x:
        l.append([taxis_x[j][i],taxis_y[j][i]])
    offsets.append(l)


x,y = [],[]
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])
scat = ax.scatter(x,y,s=2,color='orange') 
anim = FuncAnimation(fig, animate, interval=10, frames=len(offsets)-1, repeat = False)

plt.draw()
plt.show()
