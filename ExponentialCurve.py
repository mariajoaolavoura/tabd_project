import matplotlib.pyplot as plt
import csv

# Read colors file
colors = []
"""
[
    [ c1, c2, c3, ...]
    [...],
    ...
]
"""

with open('./../data/random_colors.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    i = 0
    for row in reader:
        colors.append(row)

infected_cum=[]
for hour in range(24):
    slice= int((hour+1)*len(colors)/24)
    #print(colors[slice])
    cum_infect = 0
    for reds in colors[slice-1]:
        if reds == 'red':
            cum_infect += 1
            #print(cum_infect)
    infected_cum.append(cum_infect)

print(infected_cum)
print(len(colors[0])) #1660 taxis
plt.scatter(range(1,25,1),infected_cum)

plt.title('National cumulative cases')
plt.xlabel('Hour of the day / h')
plt.ylabel('# of positive infections')
#add x and y limits
plt.ylim(0, 1600)
plt.xlim(0, 25)
plt.show()

"""
plt.scatter(range(1,10),infected_cum[0:9])
plt.title('National cumulative cases at 9am')
plt.xlabel('Hour of the day / h')
plt.ylabel('# of positive infections')
#add x and y limits
plt.ylim(0, 1600)
plt.xlim(0, 25)
plt.show()

plt.scatter(range(1,13),infected_cum[0:12])
plt.title('National cumulative cases at 12am')
plt.xlabel('Hour of the day / h')
plt.ylabel('# of positive infections')
#add x and y limits
plt.ylim(0, 1600)
plt.xlim(0, 25)
plt.show()

plt.scatter(range(1,16),infected_cum[0:15])
plt.title('National cumulative cases at 3pm')
plt.xlabel('Hour of the day / h')
plt.ylabel('# of positive infections')
#add x and y limits
plt.ylim(0, 1600)
plt.xlim(0, 25)
plt.show()
"""