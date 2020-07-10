import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib import rcParams
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable, get_cmap
import psycopg2
from postgis import psycopg, Polygon, MultiPolygon
from datetime import datetime
import csv
from taxi import Taxi

ZOOM = 10000
def get_city_limits(center_lon, center_lat, ZOOM):
    xlim = (center_lon - ZOOM, center_lon + ZOOM)
    ylim = (center_lat - ZOOM, center_lat + ZOOM)
    return xlim, ylim

# limits of
DISTRICTS = ['BRAGA','PORTO','AVEIRO','COIMBRA','LISBOA']
X_BRAGA, Y_BRAGA = (-42618, -3999), (185175, 232998)
X_PORTO, Y_PORTO = get_city_limits(-41601.3030699869, 165663.59287178, ZOOM)
X_AVEIRO, Y_AVEIRO = (-55299, -26326), (80718, 128542)
X_COIMBRA, Y_COIMBRA = get_city_limits(-23602.1779130802, 59444.2411470825, ZOOM)
X_LISBON, Y_LISBON = get_city_limits(-90973.4688070632, -103263.891293955, ZOOM*2.5)

XS_MIN, XS_MAX, YS_MIN, YS_MAX = -120000, 165000, -310000, 285000
X_ORIGIN = (XS_MIN, XS_MAX)
Y_ORIGIN = (YS_MIN, YS_MAX)
SCALE = 1/3000000
WIDTH = (XS_MAX - XS_MIN) / 0.0254 * 1.1 # in inches
HEIGHT = (YS_MAX - YS_MIN) / 0.0254 * 1.1 # in inches
TS_I = 1570665600 # timestamp of day from which data was taken
OFFSETS_FILEPATH = './../../data/offsets3.csv'
COLORS_FILEPATH = './colors2.csv'
TAXIS_INFO_HISTORY_FILEPATH = './taxis_info_history2.csv'

class CsvChunkReader:
	def __init__(self, filename, parser):
		self.file = open(filename, 'r')
		self.reader = csv.reader(self.file)
		self.parser = parser

	def read_next(self):
		try:
			row = next(self.reader)
		except StopIteration:
			return None

		l = []

		for j in row:
			l.append(self.parser(j))

		return l

class TaxiAnimation:
	def __init__(self, fig, ax_map, ax_graph, ax_bar, scat_map, scat_graph, bar, cb):
		self.fig = fig
		self.ax_map = ax_map
		self.ax_graph = ax_graph
		self.ax_bar = ax_bar
		self.scat_map = scat_map
		self.scat_graph = scat_graph
		self.bar = bar
		self.cb = cb #colorbar

		self.offsets = CsvChunkReader(OFFSETS_FILEPATH, TaxiAnimation._parse_offset)
		self.colors = CsvChunkReader(COLORS_FILEPATH, TaxiAnimation._parse_color)
		self.taxis_info_history = CsvChunkReader(TAXIS_INFO_HISTORY_FILEPATH, TaxiAnimation._parse_taxis_info_history)
		
		self.zoom_counter = 0
		self.anim = None
		self.ZOOM_STEP = 0.01

		self.current_offset_data = None
		self.current_color_data = None
		self.current_taxis_info_history_data = None
		self.total_n_infected_history = [] # [ [hour, total_n_infected_at_hour], [] ]
		self.n_infected_by_district = { d:0 for d in DISTRICTS } # { BRAGA: total_n_infected_at_hour, PORTO: ...}

	@staticmethod
	def _parse_offset(j):
		x, y = j.split()
		return [float(x), float(y)]

	@staticmethod
	def _parse_color(j):
		r, g, b = j.split()
		return [float(r), float(g), float(b)]
		
	@staticmethod
	def _parse_taxis_info_history(j):
		taxi_id, active, district, infected, contact_time, transmission = j.split()
		active = active == "True"
		infected = infected == "True"
		return Taxi(int(taxi_id), active, district, infected, int(contact_time), int(transmission))

	def _generator(self):
		i = 0

		while True:
			self.current_offset_data = self.offsets.read_next()
			self.current_color_data = self.colors.read_next()
			self.current_taxis_info_history_data = self.taxis_info_history.read_next()

			if self.current_offset_data is not None and \
				self.current_color_data is not None and \
				self.current_taxis_info_history_data is not None:
				yield i
				i += 1
			else:
				break

	def _get_zoom_limits(self, x_initial, y_initial, x_final, y_final):
		xlim_min = (1-self.zoom_counter)*x_initial[0] + self.zoom_counter*x_final[0]
		xlim_max = (1-self.zoom_counter)*x_initial[1] + self.zoom_counter*x_final[1]
		ylim_min = (1-self.zoom_counter)*y_initial[0] + self.zoom_counter*y_final[0]
		ylim_max = (1-self.zoom_counter)*y_initial[1] + self.zoom_counter*y_final[1]
		return (xlim_min, xlim_max), (ylim_min, ylim_max)

	def _do_zoom(self, d):
		# zoom in Lisbon
		if d.hour >= 1 and d.hour < 2 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_ORIGIN, Y_ORIGIN, X_LISBON, Y_LISBON)
			ax_map.set(xlim=xlim, ylim=ylim)
			
		# zoom out
		elif d.hour >= 2 and d.hour < 3 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_ORIGIN, Y_ORIGIN, X_LISBON, Y_LISBON)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Porto
		elif d.hour >= 3 and d.hour < 4 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_ORIGIN, Y_ORIGIN, X_PORTO, Y_PORTO)
			ax_map.set(xlim=xlim, ylim=ylim)
			
		# zoom in Aveiro 
		elif d.hour >= 4 and d.hour < 5 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_AVEIRO, Y_AVEIRO, X_PORTO, Y_PORTO)
			ax_map.set(xlim=xlim, ylim=ylim)
		
		# zoom in Coimbra
		elif d.hour >= 5 and d.hour < 6 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_AVEIRO, Y_AVEIRO, X_COIMBRA, Y_COIMBRA)
			ax_map.set(xlim=xlim, ylim=ylim)
			
		# zoom in Lisbon
		elif d.hour >= 6 and d.hour < 7 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_LISBON, Y_LISBON, X_COIMBRA, Y_COIMBRA)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom out
		elif d.hour >= 7 and d.hour < 10 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_LISBON, Y_LISBON, X_ORIGIN, Y_ORIGIN)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Braga
		elif d.hour >= 10 and d.hour < 11 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_BRAGA, Y_BRAGA, X_ORIGIN, Y_ORIGIN)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Porto
		elif d.hour >= 11 and d.hour < 12 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_BRAGA, Y_BRAGA, X_PORTO, Y_PORTO)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Aveiro
		elif d.hour >= 12 and d.hour < 13 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_AVEIRO, Y_AVEIRO, X_PORTO, Y_PORTO)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Lisbon
		elif d.hour >= 13 and d.hour < 14 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_AVEIRO, Y_AVEIRO, X_LISBON, Y_LISBON)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom out
		elif d.hour >= 14 and d.hour < 15 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_ORIGIN, Y_ORIGIN, X_LISBON, Y_LISBON)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Porto
		elif d.hour >= 15 and d.hour < 16 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_ORIGIN, Y_ORIGIN, X_PORTO, Y_PORTO)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Lisbon
		elif d.hour >= 16 and d.hour < 17 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_LISBON, Y_LISBON, X_PORTO, Y_PORTO)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Aveiro
		elif d.hour >= 17 and d.hour < 20 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_LISBON, Y_LISBON, X_AVEIRO, Y_AVEIRO)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom in Braga
		elif d.hour >= 20 and d.hour < 21 and self.zoom_counter > 0:
			self.zoom_counter -= self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_BRAGA, Y_BRAGA, X_AVEIRO, Y_AVEIRO)
			ax_map.set(xlim=xlim, ylim=ylim)

		# zoom out
		elif d.hour >= 21 and d.hour < 24 and self.zoom_counter < 1:
			self.zoom_counter += self.ZOOM_STEP
			xlim, ylim = self._get_zoom_limits(X_BRAGA, Y_BRAGA, X_ORIGIN, Y_ORIGIN)
			ax_map.set(xlim=xlim, ylim=ylim)

	def _update_total_number_infected_history(self, i):
		d = datetime.utcfromtimestamp(TS_I+i*10)
		n_infected_taxis = 0
		for taxi in self.current_taxis_info_history_data:
			n_infected_taxis += 1 if taxi.infected else 0

		self.total_n_infected_history.append([d.hour, n_infected_taxis])

	def _update_graph(self, d):
		n_infected_coord = [[0,0]]*24
		n_infected_coord[:d.hour] = self.total_n_infected_history
		self.scat_graph.set_offsets(n_infected_coord)

	def _update_number_infected_by_district(self):
		self.n_infected_by_district = { d:0 for d in DISTRICTS }
		for taxi in self.current_taxis_info_history_data:
			n_infected_taxis = 0
			if taxi.district in DISTRICTS:
				self.n_infected_by_district[taxi.district] += 1 if taxi.infected else 0

	def _update_bar_plot(self):
		for i,b in enumerate(self.bar):
			d = self.n_infected_by_district[DISTRICTS[i]]
			b.set_height(d)

	def _animate(self, i):
		d = datetime.utcfromtimestamp(TS_I + i*10)
		self.ax_map.set_title(d)

		self.scat_map.set_offsets(self.current_offset_data)
		self.scat_map.set_facecolor(self.current_color_data)

		self._do_zoom(d)

		if d.minute == 0 and d.second == 0:
			self._update_total_number_infected_history(i)
			self._update_graph(d)

			self._update_number_infected_by_district()
			self._update_bar_plot()

	def run(self):
		self.anim = FuncAnimation(self.fig, lambda i: self._animate(i), frames=lambda: self._generator(), interval=10, repeat=False, cache_frame_data=False)

		# save to video
		rcParams['animation.ffmpeg_path'] = r'C:\Users\mjlav\Downloads\ffmpeg-20200628-4cfcfb3-win64-static\ffmpeg-20200628-4cfcfb3-win64-static\bin\ffmpeg.exe'
		writer = FFMpegWriter(fps=60)
		self.anim.save('plot.mp4', writer=writer)


def create_basemap():
	print("Creating basemap")

	fig = plt.figure()
	fig.canvas.set_window_title('Covid spread simulation - Fernando Camilo, Lucia Brandao, Maria Lavoura - TABD')

	ax_map = plt.subplot2grid((5,5), (0,0), rowspan=5, colspan=2)
	ax_graph = plt.subplot2grid((5,5), (0,3), rowspan=2, colspan=2)
	ax_bar = plt.subplot2grid((5,5), (3,3), rowspan=2, colspan=2)

	ax_map.axis('off')
	ax_map.set(xlim=(XS_MIN, XS_MAX), ylim=(YS_MIN, YS_MAX))

	ax_graph.set(xlim=(0, 24), ylim=(0, 1700))
	ax_graph.set_xticks(np.arange(0,25,2))
	ax_graph.set_title("Scatter plot of total number of infected taxis by hour")
	ax_graph.set_xlabel("Hours")
	ax_graph.set_ylabel("Number of infected")

	ax_bar.set_ylim(0, 900)
	ax_bar.set_title("Bar plot of the number of infected taxis by district")
	ax_bar.set_xlabel("Districts")
	ax_bar.set_ylabel("Number of infected")

	return (fig, ax_map, ax_graph, ax_bar)

def plot_map_of_portugal(ax_map):
	print("Plotting map of Portugal from database data")

	conn = psycopg2.connect("dbname=TABD user=postgres password=' '")
	psycopg.register(conn)

	cursor_psql = conn.cursor()
	cursor_psql.itersize = 500
	sql = "select distrito,st_union(proj_boundary) from cont_aad_caop2018 group by distrito"
	cursor_psql.execute(sql)
	results = cursor_psql.fetchall()

	for row in results:
		geom = row[1]
		if type(geom) is MultiPolygon:
			for pol in geom:
				xys = pol[0].coords
				xs, ys = [], []
				for (x, y) in xys:
					xs.append(x)
					ys.append(y)
				ax_map.plot(xs, ys, color='black', lw='0.2')
		elif type(geom) is Polygon:
			xys = geom[0].coords
			xs, ys = [], []
			for (x, y) in xys:
				xs.append(x)
				ys.append(y)
			ax_map.plot(xs, ys, color='black', lw='0.2')

def create_taxi_position_scatter_plot(ax_map):
	print("Creating taxi position scatter plot")
	return ax_map.scatter([], [], s=4)

def create_total_infected_scatter_plot(ax_graph):
	print("Creating total infected scatter plot")
	n_infected_y = [0]*24
	n_infected_x = [0]*24
	return ax_graph.scatter(n_infected_x, n_infected_y)

def create_infected_per_district_bar_plot(ax_bar):
	print("Creating infected by district bar plot")
	xpos = np.arange(len(DISTRICTS))
	heights = [0]*len(DISTRICTS)
	bar_plot = ax_bar.bar(xpos, heights)
	ax_bar.set_xticks(xpos)
	ax_bar.set_xticklabels(DISTRICTS)
	return bar_plot

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=-1):
	if n == -1:
		n = cmap.N
	new_cmap = LinearSegmentedColormap.from_list('trunc({name},{a:.2f},{b:.2f})'.format(name=cmap.name, a=minval, b=maxval), cmap(np.linspace(minval, maxval, n)))
	return new_cmap

def create_colorbar(minColor=0.45, maxColor=1):
	print("Creating colorbar")
	cmap = truncate_colormap(plt.get_cmap("gist_heat_r"), minColor, maxColor)
	norm = BoundaryNorm(np.arange(0, 12), cmap.N)
	cb = plt.colorbar(ScalarMappable(cmap=cmap, norm=norm), ax=ax_map, fraction=0.046, pad=0.04)
	cb.set_label('Number of taxis infected')
	return cb


fig, ax_map, ax_graph, ax_bar = create_basemap()
plot_map_of_portugal(ax_map)
scat_map = create_taxi_position_scatter_plot(ax_map)
scat_graph = create_total_infected_scatter_plot(ax_graph)
bar = create_infected_per_district_bar_plot(ax_bar)
cb = create_colorbar()
anim = TaxiAnimation(fig, ax_map, ax_graph, ax_bar, scat_map, scat_graph, bar, cb)
anim.run()

mng = plt.get_current_fig_manager()
mng.window.state('zoomed')  # works fine on Windows!

# plt.show()