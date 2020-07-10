class Taxi:

	def __init__(self, taxi_id=None, active=True, district=None, infected=False, contact_time=0, transmission=0):
		"""
		taxi_id - int - id of the taxi in the bd
		active - bool - if the taxi is active or innactive
		district - string - name of the district the taxi starts working on
		infected - bool - if the taxi has covid or not
		contact_time - int - ts counter of contact time
		transmission - int - counter of number of taxis the current taxi has infected
		"""
		self.taxi_id = taxi_id
		self.active = active
		self.district = district
		self.infected = infected
		self.contact_time = contact_time
		self.transmission = transmission

	def update_taxi_id(self, taxi_id):
		self.taxi_id = taxi_id

	def update_active_state(self, value):
		self.active = value

	def update_district(self, district):
		self.district = district

	def update_to_infected(self):
		self.infected = True

	def increment_contact_time(self):
		self.contact_time += 1

	def increment_transmission(self):
		self.transmission += 1

	def reset(self):
		self.infected = False
		self.contact_time = 0
		self.transmission = 0

	# def get_info(self):
	#     return (self.taxi_id, self.active, self.district, self.infected, self.contact_time, self.transmission)

	def __str__(self):
	    return str(self.taxi_id) + " " + str(self.active) + " " + str(self.district) + " " + str(self.infected) + " " + str(self.contact_time)  + " " + str(self.transmission)