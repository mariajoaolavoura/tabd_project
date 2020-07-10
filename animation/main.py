"""
Nenhum encontro com infetados. Taxi não infetado. Total de min de encontros com infetados = 0.
X encontros com infetados. Total de min < 10. Taxi não infetado. Total de min de encontro com infetados = soma dos min de cada encontro
Y encontros com infetados. Total de min >= 10. Taxi infetado. Total de min de encontro com infetados = -1

taxis_info_at_instant = dictionary( key=taxi_column, value=[infected, contact_time, transmission] ) 
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
MJ - Zooms, size da bola do taxi proporcional ao nro de infetados
"""

## Imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import random
import datetime
import csv
from copy import deepcopy
import psycopg2
from postgis.psycopg import register
from postgis import Polygon,MultiPolygon
from colorsys import hsv_to_rgb

## From files
# classes
from taxi import Taxi
#from portugal import Portugal, District
# read offsets file
from read_offsets import offsets
print("Read offsets")

## Functions
def distance_under(dist, lista, coord):
    index_coord = []
    j=0
    for i in lista:
        if(math.hypot((i[0]-coord[0]),(i[1]-coord[1])) < dist):
            index_coord.append(j)
        j+=1
    return index_coord


## Initialize dictionary
## taxis_info_at_beginning = dictionary{ key=offsets_column, value=Taxi }
n_taxis = len(offsets[0])
taxis_info_at_beginning = [Taxi() for k in range(n_taxis)]
print("Initialize dictionary")

## Update the taxis_id
from get_taxi_id_position_dict import taxi_id_position

for taxi_id, position in taxi_id_position.items():
    taxis_info_at_beginning[position].update_taxi_id(taxi_id)
print("Update taxi_id")

## Update the taxis_info_at_beginning with 10 first infected taxis
from get_10_1st_taxis_Porto_Lisbon import taxis_porto, taxis_lisbon

# From Porto
for taxi_id in taxis_porto:
    pos = taxi_id_position[taxi_id]
    taxis_info_at_beginning[pos].update_to_infected()
# From Lisboa
for taxi_id in taxis_lisbon:
    pos = taxi_id_position[taxi_id]
    taxis_info_at_beginning[pos].update_to_infected()    
print("Update 10 first taxis Porto Lisbon")

## Update taxis district
from get_taxi_id_district_dict import taxi_id_district_dict
print("get taxis district")

for taxi in taxis_info_at_beginning:
    if taxi.taxi_id in taxi_id_district_dict.keys():
        district = taxi_id_district_dict[taxi.taxi_id]
        taxi.update_district(district)
print("Update taxis district")


"""
offsets [ [ [x,y], ... ], [...], ... ]
colors [ [ c1, c2, c3, ...], [...], ... ]
taxis_info_history [ [taxi, taxi, ... ], [...], ... ]
"""

dummy = [0.000000, 0.000000]
taxis_info_history, colors = [], []

ts_to_infected = 60 # ts = 10s, 1min= 6 ts, 10min = 60 ts
infection_radius = 50

taxis_info_at_instant = taxis_info_at_beginning

print("started main logic")
for coords_at_instant in offsets: # row [ [x,y], ... ]
    c, s = [], []
    for taxi_column in range(0, len(coords_at_instant)):
        coord = coords_at_instant[taxi_column] # coord [x,y]
        taxi = taxis_info_at_instant[taxi_column]
        # update taxi active state, coord != dummy ? active : inactive
        taxi.update_active_state(coord != dummy)
        if taxi.active: 
            # if taxi is infected
            if (taxi.infected):
                # verify its neighbours taxis within 50m
                column_neig_50m = distance_under(infection_radius, coords_at_instant, coord) # column in row of offsets
                for neig_column in column_neig_50m:
                    coord = coords_at_instant[neig_column]
                    neig_taxi = taxis_info_at_instant[neig_column]
                    
                    # if its neighbour is not infected
                    if (not neig_taxi.infected):
                        # update the contact time of that neighbour
                        before = neig_taxi.contact_time
                        neig_taxi.increment_contact_time()

                    # if that neighbour is not infected and reached 1min contact
                    if (not neig_taxi.infected and neig_taxi.contact_time >= 6):
                        # guarantee that it's only 10% probability of contamination
                        if(random.randrange(0, 101 , 1)<=10):    
                            # update that neigbour to infected
                            neig_taxi.update_to_infected()
                            # update number of taxis this taxi infected
                            taxi.increment_transmission()
                        
                        # if not 10%, it's not infected and nedds to wait another minute
                        else:
                            neig_taxi.reset()

        c += [ taxi.transmission ]
    taxis_info_history.append(deepcopy(taxis_info_at_instant))
    colors.append(c)

# get colors in rgb
print("get colors in rgb")
max_n_infected = max(colors[-1])
colors = []
for taxis_info_at_instant in taxis_info_history:
    colors_at_instant = []

    for taxi in taxis_info_at_instant:
        if not taxi.active:
            colors_at_instant.append( hsv_to_rgb(0.0, 0.0, 1.0) ) # white
        elif not taxi.infected:
            colors_at_instant.append( hsv_to_rgb(120/360, 1.0, 0.5) ) # green
        else:
            value = max([(1.0 - (taxi.transmission / max_n_infected + 0.2)), 0]) # red to black, depending on transmission
            colors_at_instant.append( hsv_to_rgb( 0.0, 1.0, value) )

    colors.append(colors_at_instant)



## Save to file
print("saving files")
with open("./colors3.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for colors_at_instant in colors: 
        color = colors_at_instant[0]
        print("%s %s %s" % (color[0],color[1],color[2]), end="", file=csv_file)
        for color in colors_at_instant[1:]:
            print(",%s %s %s" % (color[0],color[1],color[2]), end="", file=csv_file)
        print("", file=csv_file)

with open("./taxis_info_history3.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for taxis_info_at_instant in taxis_info_history:
        taxi = taxis_info_at_instant[0]
        print("%s %s %s %s %s %s" % (taxi.taxi_id, taxi.active, taxi.district, taxi.infected, taxi.contact_time, taxi.transmission ), end="", file=csv_file)
        for taxi in taxis_info_at_instant[1:]:
            print(",%s %s %s %s %s %s" % (taxi.taxi_id, taxi.active, taxi.district, taxi.infected, taxi.contact_time, taxi.transmission ), end="", file=csv_file)
        print("", file=csv_file)
