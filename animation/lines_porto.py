import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import math
import psycopg2
from postgis import Polygon,MultiPolygon,LineString
from postgis.psycopg import register

#Coimbra
#center_lon = -23602.1779130802
#center_lat = 59444.2411470825

#Porto
center_lon = -41601.3030699869
center_lat = 165663.59287178 

#Lisboa
#center_lon = -87973.4688070632
#center_lat = -103263.891293955

#Sintra
#center_lon = -108167.564175462
#center_lat = -95655.0195241774

scale=1/30000
zoom = 10000

plt.style.use('dark_background')
xs_min, xs_max, ys_min, ys_max = center_lon - zoom, center_lon + zoom, center_lat - zoom, center_lat + zoom 
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1
fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)

cursor_psql = conn.cursor()

sql =   """ select tr.proj_track 
            from tracks as tr, cont_aad_caop2018 as caop
            where caop.concelho='PORTO' and
                    st_within(st_pointn(tr.proj_track,1), caop.proj_boundary) and
                    tr.state='BUSY'
        """

cursor_psql.execute(sql)

results = cursor_psql.fetchall()

cont = 0

for track in results:
    if type(track[0]) is LineString:
        xy = track[0].coords
        xxx = []
        yyy = []
        first = 1
        for (x,y) in xy:
            if first == 1:
                xxx.append(x)
                yyy.append(y)
                previousx=x
                previousy=y
                first = 0
            elif math.sqrt(abs(x-previousx)**2+abs(y-previousy)**2)<50:
                xxx.append(x)
                yyy.append(y)
                previousx=x
                previousy=y
        ax.plot(xxx,yyy,linewidth=0.2,color='white')


import operator
from read_taxis_history import taxis_info_history

last_line = taxis_info_history[-1]
taxis_from_porto = list(filter(lambda taxi: taxi.district=='PORTO', last_line))
max_value = max(taxis_from_porto, key=lambda taxi: taxi.transmission)
taxi_pos_that_spred_most = last_line.index(max_value)

from get_taxi_id_position_dict import taxi_id_position

taxi_id = list(taxi_id_position.keys())[list(taxi_id_position.values()).index(taxi_pos_that_spred_most)]

sql = "select proj_track from tracks where taxi='"+str(taxi_id)+"'"

cursor_psql.execute(sql)
results = cursor_psql.fetchall()
cont = 0

for track in results:
    if type(track[0]) is LineString:
        xy = track[0].coords
        xxx = []
        yyy = []
        first = 1
        for (x,y) in xy:
            if first == 1:
                xxx.append(x)
                yyy.append(y)
                previousx=x
                previousy=y
                first = 0
            elif math.sqrt(abs(x-previousx)**2+abs(y-previousy)**2)<50:
                xxx.append(x)
                yyy.append(y)
                previousx=x
                previousy=y
        ax.plot(xxx,yyy,linewidth=0.2,color='red')


plt.savefig('1.png')




