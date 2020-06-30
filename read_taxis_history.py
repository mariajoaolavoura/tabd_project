import csv

taxis_info_history = []
"""
each dictionary 
key=taxi_column, value=[infected, contact_time, transmission]
infected=0? not infected : infected. 
contact_time - ts counter of contact time
transmission - counter of number of taxis the current taxi infected

[   
    { 0:[i,c,c], 1:[], ... }, 
    {...}, 
    ...
]
"""

with open('./../data/random_taxis_info_history2.1.csv', 'r',  newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    i = 0
    for row in reader:
        d = {}
        for j in row:
            k, v = j.split(":")
            v1, v2, v3 = v.split()
            d[int(k)] = [ int(v1), int(v2), int(v3)]
        taxis_info_history.append(d)
