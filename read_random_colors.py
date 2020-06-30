import csv

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