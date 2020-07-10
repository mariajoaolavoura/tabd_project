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
        ax.set(xlim=xlim, ylim=ylim)
        
    # zoom out
    elif d.hour >= 2 and d.hour < 3 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(x_origin, y_origin, lisbon_xlim, lisbon_ylim, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)

    # zoom in Porto
    elif d.hour >= 3 and d.hour < 4 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(x_origin, y_origin, porto_xlim, porto_ylim, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)
        
    # zoom in Aveiro 
    elif d.hour >= 4 and d.hour < 5 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(aveiro_xlim, aveiro_ylim, porto_xlim, porto_ylim, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)
    
    # zoom in Coimbra
    elif d.hour >= 5 and d.hour < 6 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(aveiro_xlim, aveiro_ylim, coimbra_xlim, coimbra_ylim, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)
        
    # zoom in Lisbon
    elif d.hour >= 6 and d.hour < 7 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(lisbon_xlim, lisbon_ylim, coimbra_xlim, coimbra_ylim, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)

    # zoom out
    elif d.hour >= 7 and d.hour < 18 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(lisbon_xlim, lisbon_ylim, x_origin, y_origin, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)

    # zoom in Braga
    elif d.hour >= 18 and d.hour < 20 and perform_zoom.counter > 0:
        perform_zoom.counter -= step
        xlim, ylim = get_zoom_limits(braga_xlim, braga_ylim, x_origin, y_origin, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)

    # zoom out
    elif d.hour >= 20 and perform_zoom.counter < 1:
        perform_zoom.counter += step
        xlim, ylim = get_zoom_limits(braga_xlim, braga_ylim, x_origin, y_origin, perform_zoom.counter)
        ax.set(xlim=xlim, ylim=ylim)


def animate(i):
    d = datetime.datetime.utcfromtimestamp(ts_i+i*10)
    ax.set_title(d)
    scat.set_offsets(offsets[i])
    scat.set_facecolor(colors[i])
    perform_zoom(d)


# Variables
# to perform zoom
perform_zoom.counter = 0
step = 0.01


## Plots
ts_i = 1570665600
scale=1/3000000

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
x_origin = (xs_min, xs_max)
y_origin = (ys_min, ys_max)
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

#anim.save('plot_with_zoom.gif', writer='PillowWriter')