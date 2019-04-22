import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from Thing import *

class Point:
	''' Contains information about a single datapoint '''
	def __init__(self, x, y, refl, height):
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
	slices = [[] for n in range(n_slices)]
	d = [project(p.x,p.y,angle) for p in points]
	dmin = min(d)
	dmax = max(d)
	delta = (dmax-dmin)/n_slices
	for i, point in enumerate(points):
		slices[min(int((d[i]-dmin)/delta),n_slices-1)] += [point]
		point.d = d[i]
		point.n = np.sqrt(point.x**2+point.y**2-d[i]**2)
	return slices

def project(x, y, angle):
	''' Projects a point onto a direction vector '''
	return np.cos(angle)*x+np.sin(angle)*y

# Load data from file
dat = pandas.read_csv('KLOT_ParkForest_Refl.csv')
N = len(dat)

# Parse data into list of point objects
points = []
for i in range(N):
	if dat['elevAngle'][i] < 9:
		continue
	x = (dat['longitude'][i]-dat['longitude'][0])*111*np.cos(np.radians(dat['latitude'][i])) # km
	y = (dat['latitude'][i]-dat['latitude'][0])*111 # km
	p = Point(x, y, dat['value'][i], dat['heightRel'][i]/1000)
	points.append(p)

# Slice data along axis of greatest variations
slices = slice(points, n_slices=6)

# Scatter plot the data slices in different colors (axis units are in km)
fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', projection='3d')
for data in slices:
	ax.scatter(get(data, 'x'), get(data, 'y'), get(data, 'height'))

# Predict meteor position and velocity distribution using particle filter
output = particleFilter(slices, particleCount=1000, terminalVel=1)

# Plot predicted mean particle position for each slice
x = []
y = []
z = []
for data, particles in zip(slices, output):
	x += [np.mean(get(data, 'x'))]
	y += [np.mean(get(data, 'y'))]
	z += [np.mean(list(particles[:,0]))]
ax.plot(x,y,z)

# Extrapolate landing sites from particle filter results
# TODO: incorporate predicted velocities into extrapolation
direction = [x[-1]-x[0], y[-1]-y[0], z[-1]-z[0]]
direction = [d/direction[2] for d in direction]
landX = [x[-1]-direction[0]*h for h in list(output[-1][:,0])]
landY = [y[-1]-direction[1]*h for h in list(output[-1][:,0])]
ax.scatter(landX, landY, 0)
plt.show()