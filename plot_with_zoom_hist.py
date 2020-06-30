# Maria Joao Lavoura 
# up201908426 
# Masters in Data Science


import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register
import datetime

## Read files
from read_offsets import offsets
from read_random_colors import colors
from read_taxis_history import taxis_info_history

## City limits
from city_limits import *

#########################################################################################
## Functions ############################################################################
def get_zoom_limits(x_initial, y_initial, x_final, y_final, counter):
    xlim_min = (1-counter)*x_initial[0] + counter*x_final[0]
    xlim_max = (1-counter)*x_initial[1] + counter*x_final[1]
    ylim_min = (1-counter)*y_initial[0] + counter*y_final[0]
    ylim_max = (1-counter)*y_initial[1] + counter*y_final[1]
    return (xlim_min, xlim_max), (ylim_min, ylim_max)


def perform_zoom(d):
    # zoom in Lisbon
    if d.hour >= 1 and d.hour < 2 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(x_origin, y_origin, lisbon_xlim, lisbon_ylim, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)
        
    # zoom out
    elif d.hour >= 2 and d.hour < 3 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(x_origin, y_origin, lisbon_xlim, lisbon_ylim, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)

    # zoom in Porto
    elif d.hour >= 3 and d.hour < 4 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(x_origin, y_origin, porto_xlim, porto_ylim, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)
        
    # zoom in Aveiro 
    elif d.hour >= 4 and d.hour < 5 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(aveiro_xlim, aveiro_ylim, porto_xlim, porto_ylim, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)
    
    # zoom in Coimbra
    elif d.hour >= 5 and d.hour < 6 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(aveiro_xlim, aveiro_ylim, coimbra_xlim, coimbra_ylim, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)
        
    # zoom in Lisbon
    elif d.hour >= 6 and d.hour < 7 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(lisbon_xlim, lisbon_ylim, coimbra_xlim, coimbra_ylim, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)

    # zoom out
    elif d.hour >= 7 and d.hour < 18 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(lisbon_xlim, lisbon_ylim, x_origin, y_origin, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)

    # zoom in Braga
    elif d.hour >= 18 and d.hour < 20 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(braga_xlim, braga_ylim, x_origin, y_origin, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)

    # zoom out
    elif d.hour >= 20 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(braga_xlim, braga_ylim, x_origin, y_origin, perform_zoom.counter)
        ax_map.set(xlim=xlim, ylim=ylim)

def get_current_number_of_infected_taxis(i):
    dic = taxis_info_history[i] # { 0:[i,c,c], 1:[], ... }
    n_infected_taxis = 0
    for value in dic.values():
        infected, _ , _ = value
        n_infected_taxis += 1 if infected else 0
    return n_infected_taxis

def animate(i):
    d = datetime.datetime.utcfromtimestamp(ts_i+i*10)
    
    ax_map.set_title(d)
    scat.set_offsets(offsets[i])
    scat.set_facecolor(colors[i])
    perform_zoom(d)

    if d.minute == 0 and d.second == 0:
        n_infected_coord = [[0,0]]*24
        n_infected_coord[:d.hour] = total_number_infected[:d.hour]
        n_infected_scat.set_offsets(n_infected_coord)


#########################################################################################
# List of lists with total number of infected taxis paired with each hour
# [ [total number of infected taxis, hour], ... ]
ts_i = 1570665600
total_number_infected = []

for i in range(0, len(offsets)):
    d = datetime.datetime.utcfromtimestamp(ts_i+i*10)
    if d.minute == 0 and d.second == 0:
        total_number_infected.append([d.hour, get_current_number_of_infected_taxis(i)])

#########################################################################################
# Variables #############################################################################
# to perform zoom
perform_zoom.counter = 0
step = 0.01


#########################################################################################
## Plots ################################################################################
#ts_i = 1570665600
scale=1/3000000

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
x_origin = (xs_min, xs_max)
y_origin = (ys_min, ys_max)
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1




#fig = plt.figure(figsize=(width_in_inches*scale, height_in_inches*scale))
fig = plt.figure()
ax_map = plt.subplot2grid((2,2), (0,0), rowspan=2, colspan=1)
ax_n_infected = plt.subplot2grid((2,2), (0,1), rowspan=1, colspan=1)

ax_map.axis('off')
ax_map.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

ax_n_infected.set(xlim=(0, 25), ylim=(0, 1500))
ax_n_infected.set_title("Graph of total number of infected by hour")
ax_n_infected.set_xlabel("Hours")
ax_n_infected.set_ylabel("Number of infected")

plt.tight_layout()



## Draw districts #######################################################################
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
            ax_map.plot(xs,ys,color='black',lw='0.2')
    if type(geom) is Polygon:
        xys = geom[0].coords
        xs, ys = [],[]
        for (x,y) in xys:
            xs.append(x)
            ys.append(y)
        ax_map.plot(xs,ys,color='black',lw='0.2')




## Draw taxis ###########################################################################

# initialization
x,y = [],[]
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])


scat = ax_map.scatter(x,y,s=2)

n_infected_y = [0]*24
n_infected_x = [0]*24
n_infected_y[0] = total_number_infected[0][1]
n_infected_x[0] = total_number_infected[0][0]
n_infected_scat = ax_n_infected.scatter(n_infected_x, n_infected_y)

anim = FuncAnimation(fig, animate, interval=10, frames=len(offsets)-1, repeat = False, cache_frame_data=False)

plt.tight_layout()
plt.draw()
plt.show()

#anim.save('plot_with_zoom.gif', writer='imagemagick')