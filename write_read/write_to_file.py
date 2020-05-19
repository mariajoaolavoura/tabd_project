import csv
import json

d = { 1:[0, 1, 1], 2:[1, 2, 1], 3:[1, 2, 1], 4:[1, 2, 1]}
l = [d, d, d]
# write
with open("./list_of_dict.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for dic in l:
        keys = sorted(dic.keys())
        k = keys[0]
        print("%s:%s %s %s" % (k, dic[k][0], dic[k][1], dic[k][2]), end="", file=csv_file)
        for i in range(1,len(keys)):
            k = keys[i]
            print(",%s:%s %s %s" % (k, dic[k][0], dic[k][1], dic[k][2]), end="", file=csv_file)
        print("", file=csv_file)

# read
l = []
with open('./list_of_dict.csv', 'r',  newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    i = 0
    for row in reader:
        d = {}
        for j in row:
            k, v = j.split(":")
            v1, v2, v3 = v.split()
            d[int(k)] = [ int(v1), int(v2), int(v3)]
        l.append(d)
print(l)




l = [ [1,2], [2,3] ]
ll = [ l, l, l, l ]
# write
with open("./list_of_lists.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for i in ll:
        print("%f %f" %(i[0][0],i[0][1]),end='', file=csv_file)
        for j in range(1,len(i)):
            print(",%f %f" %(i[j][0],i[j][1]),end='', file=csv_file)
        print("", file=csv_file)

# read
ll = []
with open('./list_of_lists.csv', 'r',  newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    i = 0
    for row in reader:
        l = []
        for j in row:
            x,y = j.split()
            x = float(x)
            y= float(y)
            l.append([x,y])
        ll.append(l)
print(ll)