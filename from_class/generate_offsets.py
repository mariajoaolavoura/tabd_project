import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
import datetime
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register

# define the step in seconds of the animation
step = 10

conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)
cursor_psql = conn.cursor()


sql = """select distinct taxi from tracks order by 1"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

taxis_x ={}
taxis_y ={}

ts_i = 1570665600
ts_f = 1570667000

array_size = int(24*60*60/step)

for row in results:
    taxis_x[int(row[0])] = np.zeros(array_size)
    taxis_y[int(row[0])] = np.zeros(array_size)

for i in range(ts_i,ts_f,step):
    sql = "select taxi,st_pointn(proj_track," + str(i) + "-ts) from tracks where ts<" + str(i) + " and ts+st_numpoints(proj_track)>" + str(i)
    cursor_psql.execute(sql)
    results = cursor_psql.fetchall()

    for row in results:
        x,y = row[1].coords
        taxis_x[int(row[0])][int((i-ts_i)/step)] = x
        taxis_y[int(row[0])][int((i-ts_i)/step)] = y

offsets = []
for i in range(array_size):
    l = []
    for j in taxis_x:
        l.append( [taxis_x[j][i],taxis_y[j][i]])
    offsets.append(l)


for j in taxis_x:
    print("%f," %(j),end='')
for i in offsets:
    print("%f %f" %(i[0][0],i[0][1]),end='')
    for j in range(1,len(i)):
        print(",%f %f" %(i[j][0],i[j][1]),end='')
        print("")

        
conn.close()