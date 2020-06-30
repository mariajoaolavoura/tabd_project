import csv
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