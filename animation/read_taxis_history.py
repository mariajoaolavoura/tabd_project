import csv
from taxi import Taxi


taxis_info_history = []
"""
taxis_info_history
[   
    [ Taxi, Taxi, ... ], 
    [...], 
    ...
]
"""

with open('./taxis_info_history2.csv', 'r',  newline="") as csvFile:
	reader = csv.reader(csvFile, delimiter=',')
	for row in reader:
		taxis_info_at_instant = []
		for j in row:
			taxi_id, active, district, infected, contact_time, transmission = j.split()
			active = active == "True"
			infected = infected == "True"
			taxis_info_at_instant.append(Taxi(int(taxi_id),active, district, infected, int(contact_time), int(transmission)))
			
		taxis_info_history.append(taxis_info_at_instant)