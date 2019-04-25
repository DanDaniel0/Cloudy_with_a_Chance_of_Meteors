import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from particle_filter import *

class Point:
	''' Contains information about a single datapoint '''
	def __init__(self, x, y, height, refl=0):
		self.x = x
		self.y = y
		self.refl = refl
		self.height = height

def get(points, key):
	''' Returns the key attribute of each point as a list '''
	return [getattr(p,key) for p in points]

def slice(points, angle=np.pi/4, n_slices=5):
	''' Slices the dataset along a given direction into equally spaced groups of data'''
	# TODO: compute direction of greatest variation directly from the dataset
	R = np.array(((np.cos(angle),np.sin(angle)), (-np.sin(angle), np.cos(angle))))
	slices = [[] for n in range(n_slices)]
	new_pts = np.array([np.dot(R, np.array((p.x,p.y))) for p in points])
	d = list(new_pts[:,0])
	n = list(new_pts[:,1])
	dmin = min(d)
	dmax = max(d)
	delta = (dmax-dmin)/n_slices
	for i, point in enumerate(points):
		slices[min(int((d[i]-dmin)/delta),n_slices-1)] += [point]
		point.d = d[i]
		point.n = np.sqrt(point.x**2+point.y**2-d[i]**2)
	return (slices, R, dmin, delta)

# Load data from file
# Data files were downloaded using the WCT tool
# https://data.nodc.noaa.gov/cgi-bin/iso?id=gov.noaa.ncdc:C00700
dat = pandas.read_csv('KLOT_ParkForest_Refl.csv')
N = len(dat)

# Parse data into list of point objects
points = []
for i in range(N):
	if dat['elevAngle'][i] < 9:
		continue
	x = (dat['longitude'][i]-dat['longitude'][0])*111*np.cos(np.radians(dat['latitude'][i])) # km
	y = (dat['latitude'][i]-dat['latitude'][0])*111 # km
	p = Point(x, y, dat['heightRel'][i]/1000, dat['value'][i])
	points.append(p)

# Slice data along axis of greatest variations
slices, R, dmin, delta = slice(points, angle=np.radians(60), n_slices=6)

# Scatter plot the data slices in different colors (axis units are in km)
fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', projection='3d')
for data in slices:
	ax.scatter(get(data, 'x'), get(data, 'y'), get(data, 'height'))

# Predict meteor position and velocity distribution using particle filter
particles = particleFilter(slices, particleCount=10000, terminalVel=1)

# Convert output particles into original coordinates
R_inv = np.linalg.inv(R)
dvel = ((np.max([p.d for p in slices[-1]]) - np.min([p.d for p in slices[0]])))/len(slices)
output = []
for i, step in enumerate(particles):
	output_step = []
	for particle in step:
		d = i*delta+dmin
		n = particle[4]
		pos = np.dot(R_inv, np.array((d,-n)))
		vel = np.dot(R_inv, np.array((-dvel,particle[3])))
		p = Point(pos[0], pos[1], particle[0])
		p.vx = vel[0]
		p.vy = vel[1]
		p.vz = particle[2]
		output_step += [p]
	output += [output_step]

# Plot predicted mean particle position for each slice
x = [np.mean(get(o, 'x')) for o in output]
y = [np.mean(get(o, 'y')) for o in output]
z = [np.mean(get(o, 'height')) for o in output]
ax.plot(x,y,z)

# Extrapolate landing sites from particle filter results
landX = [x[-1]-p.vx*p.height/p.vz for p in list(output[-1])]
landY = [y[-1]-p.vy*p.height/p.vz for p in list(output[-1])]
landLat = [y/111+dat['latitude'][0] for y in landY]
landLon = [x/111/np.cos(np.radians(lat))+dat['longitude'][0] for x, lat in zip(landX, landLat)]

# Plot individual particle trajectories
for x, y, i in zip(landX, landY, range(len(landX))):
	s = [o[i] for o in output]
# Uncomment the following line to plot individual particle trajectories
# Works best with a smaller number of partices (e.g. 10)
# To change particle count edit the "particleCount" value on line 62
	# ax.plot([o.x for o in s]+[x], [o.y for o in s]+[y], [o.height for o in s]+[0])

# Plot landing sites on the same graph as the radar observations
ax.scatter(landX, landY, 0, c='r')
plt.show()

# Plot heatmap of landing locations
grid, x_axis, y_axis = np.histogram2d(landLon, landLat, bins=(30,50))
extent = [x_axis[0], x_axis[-1], y_axis[0], y_axis[-1]]
plt.imshow(grid, cmap='hot', interpolation='nearest', extent=extent, origin='lower')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.colorbar()
plt.title('Meteor Landing Site Probability Distribution')
plt.show()

# TODO: overlay the heatmap with the 3D scatter plot
# TODO: overlay actual locations of recovered meteorites
# TODO: underlay a geographic map
# TODO: look into effects of wind