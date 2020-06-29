import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import csv
import psycopg2
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register

## Get the match between taxi's id in the db with that taxi's column in offsets.
## Create a dict { key=taxi_id_db, value=offsets_columns}

conn = psycopg2.connect("dbname=teste2 user=postgres password='w7obbsci' ")
register(conn)
cursor_psql = conn.cursor()

sql ="""select distinct taxi from tracks order by 1"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

taxi_id_position = {}
pos = 0
for taxi_id in results:
    taxi_id_position[ int(taxi_id[0]) ] = pos
    pos += 1

## Get taxis' id from Distrito Porto and match with taxis' column in offsets

# From Distrito Porto
sql = """select distinct (tr.taxi) from cont_aad_caop2018 as caop, tracks as tr
where caop.distrito='PORTO' and  st_within(st_pointn(tr.proj_track,1), caop.proj_boundary)"""
cursor_psql.execute(sql)
results_porto = cursor_psql.fetchall()

taxi_position = []
for taxi_id in results_porto:
    taxi_position += [ taxi_id_position[ int(taxi_id[0]) ] ]

#print(taxi_position)
#print(len(taxi_position)) #647 taxis


## Read offsets file
offsets_x = []
offsets_y = []
with open('./../data/offsets3.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    i = 0
    for row in reader:
        xl = []
        yl = []
        for j in row:
            x,y = j.split()
            x = float(x)
            y = float(y)
            xl.append(x)
            yl.append(y)
        offsets_x.append(xl)
        offsets_y.append(yl)

#print (len(offsets_x[0])) #1660
#print (len(offsets_y[0])) #1660


# Open colors
colors = []
with open('./../data/random_colors.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    i = 0
    for row in reader:
        colors.append(row)

Porto_taxis_x=[]
Porto_taxis_y=[]
Porto_taxis_colors=[]

for ts in offsets_x:
    a = []
    for column in taxi_position:
        a.append(ts[column])
    Porto_taxis_x.append(a)

for ts in offsets_y:
    a = []
    for column in taxi_position:
        a.append(ts[column])
    Porto_taxis_y.append(a)

for ts in colors:
    a = []
    for column in taxi_position:
        a.append(ts[column])
    Porto_taxis_colors.append(a)


#print (len(Porto_taxis_x[0])) #647
#print (len(Porto_taxis_y[0])) #647
#print (len(Porto_taxis_colors[0]))#647

#after 9 hours: às 9h da manhã
n=9
infected_x_9h =[Porto_taxis_x[int(n*len(Porto_taxis_x)/24)][i] for i,j in enumerate(Porto_taxis_colors[int(n*len(Porto_taxis_x)/24)]) if j == 'red']
infected_y_9h =[Porto_taxis_y[int(n*len(Porto_taxis_y)/24)][i] for i,j in enumerate(Porto_taxis_colors[int(n*len(Porto_taxis_y)/24)]) if j == 'red']

#print (len(infected_x_9h)) # 211 tem de ser menor que 647 e maior que 10 (porque infecção inicial foram 10 no Porto)
#print (infected_y_9h) #ainda tem alguns na coord (0,0) que estão infectados mas que ainda não estão a contaminar...


# Define numbers of bins per axis.
N_bins = 100
# Construct 2D histogram from data using the 'plasma' colormap
plt.hist2d(infected_x_9h, infected_y_9h, bins=N_bins, normed=False, cmap='plasma', vmin=0, vmax=30)
# Plot a colorbar with label.
cb = plt.colorbar()
cb.set_label('Number of infected')
# Add title and labels to plot.
plt.title('Distribution of infected at 9 am in Distrito do Porto')
plt.xlabel('latitude no Distrito do Porto')
plt.ylabel('longitude no Distrito do Porto')
#add x and y limits
plt.ylim(150000, 180000)
plt.xlim(-47500, -30000)
# Show the plot.
plt.show()

#after 12 hours: ao meio dia
n=12
infected_x_12h =[Porto_taxis_x[int(n*len(Porto_taxis_x)/24)][i] for i,j in enumerate(Porto_taxis_colors[int(n*len(Porto_taxis_x)/24)]) if j == 'red']
infected_y_12h =[Porto_taxis_y[int(n*len(Porto_taxis_y)/24)][i] for i,j in enumerate(Porto_taxis_colors[int(n*len(Porto_taxis_y)/24)]) if j == 'red']

# Define numbers of bins per axis.
N_bins = 100
# Construct 2D histogram from data using the 'plasma' colormap

plt.hist2d(infected_x_12h, infected_y_12h, bins=N_bins, normed=False, cmap='plasma', vmin=0, vmax=30)
# Plot a colorbar with label.
cb = plt.colorbar()
cb.set_label('Number of infected')
# Add title and labels to plot.
plt.title('Distribution of infected at 12 am in Distrito do Porto')
plt.xlabel('latitude no Distrito do Porto')
plt.ylabel('longitude no Distrito do Porto')
#add x and y limits
plt.ylim(150000, 180000)
plt.xlim(-47500, -30000)
# Show the plot.
plt.show()

#after 15 hours: às 15h da tarde
n=15
infected_x_15h =[Porto_taxis_x[int(n*len(Porto_taxis_x)/24)][i] for i,j in enumerate(Porto_taxis_colors[int(n*len(Porto_taxis_x)/24)]) if j == 'red']
infected_y_15h =[Porto_taxis_y[int(n*len(Porto_taxis_y)/24)][i] for i,j in enumerate(Porto_taxis_colors[int(n*len(Porto_taxis_y)/24)]) if j == 'red']

# Define numbers of bins per axis.
N_bins = 100
# Construct 2D histogram from data using the 'plasma' colormap
plt.hist2d(infected_x_15h, infected_y_15h, bins=N_bins, normed=False, cmap='plasma', vmin=0, vmax=30)
# Plot a colorbar with label.
cb = plt.colorbar()
cb.set_label('Number of infected')
# Add title and labels to plot.
plt.title('Distribution of infected at 3 pm in Distrito do Porto')
plt.xlabel('latitude no Distrito do Porto')
plt.ylabel('longitude no Distrito do Porto')
#add x and y limits
plt.ylim(150000, 180000)
plt.xlim(-47500, -30000)
# Show the plot.
"""""
sql = "select st_astext(st_envelope(st_collect(st_simplify(proj_boundary,100,FALSE)))) from cont_aad_caop2018 where distrito='PORTO';"
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

for row in results:
    xys = pol[0].coords
    xs, ys = [],[]
    for (x,y) in xys:
        xs.append(x)
        ys.append(y)
plt.plot(xs,ys,color='red',lw='0.2')

"""""

#plt.draw()
plt.show()

