import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from particle_filter import *

# Number of particles to use for the simulation
# If particleCount > 10000 then only the heat map is shown
particleCount = 50

# Whether to include air resistance in the model
airResistance = False

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

def land(p):
	''' Determines landing site of a particle using numerical integration of drag
		and gravity forces, with the assumption of moving at terminal velocity
	'''
	g = 9.81/1000
	r = 0
	z = p.height
	phi = np.arctan2(-p.vz, np.sqrt(p.vx**2+p.vy**2))
	theta = np.arctan2(p.vy, p.vx)
	terminalVel = (0.003095*(z*1000)+50.797036)/1000
	vr = terminalVel*np.cos(phi)
	vz = terminalVel*np.sin(phi)
	dt = 1
	pts = []
	while z > 0:
		terminalVel = (0.003095*(z*1000)+50.797036)/1000
		phi = np.arctan2(vz, vr)
		vr = terminalVel*np.cos(phi)
		vz = terminalVel*np.sin(phi)
		drag = -g * vr / (vr**2+vz**2)
		ar = -drag*vr
		az = -drag*vz-g
		vr += ar*dt
		vz += az*dt
		r += vr*dt
		z += vz*dt
		pts += [(p.x-r*np.cos(theta), p.y-r*np.sin(theta), z)]
	return (p.x-r*np.cos(theta), p.y-r*np.sin(theta), pts)

# Load radar reflectivity data from file
# Data files were downloaded using the WCT tool
# https://data.nodc.noaa.gov/cgi-bin/iso?id=gov.noaa.ncdc:C00700
dat = pandas.read_csv('KLOT_ParkForest_Refl.csv')
N = len(dat)

# Load recovered meteor landing site data from file
# Data was transcribed from http://www.meteoriteorbits.info/
recovered = pandas.read_csv('RecoveredMeteors.csv')

# Convert landing site coordinates into x-y coordinates
actualLat = [float(recovered['lat'][i]) for i in range(len(recovered['lat']))]
actualLong = [float(recovered['long'][i]) for i in range(len(recovered['long']))]
actualX = [(actualLong[i]-dat['longitude'][0])*111*np.cos(np.radians(actualLat[i])) for i in range(len(actualLat))]
actualY = [(actualLat[i]-dat['latitude'][0])*111 for i in range(len(actualLat))]

# Parse data into list of point objects
points = []
for i in range(N):
	if dat['elevAngle'][i] < 9: # Eliminate elevations that didn't contain the meteor
		continue
	x = (dat['longitude'][i]-dat['longitude'][0])*111*np.cos(np.radians(dat['latitude'][i])) # km
	y = (dat['latitude'][i]-dat['latitude'][0])*111 # km
	p = Point(x, y, dat['heightRel'][i]/1000, dat['value'][i])
	points.append(p)

# Slice data along axis of greatest variations
slices, R, dmin, delta = slice(points, angle=np.radians(60), n_slices=6)

# Scatter plot the data slices in different colors (axis units are in km)
if particleCount < 10000:
	fig = plt.figure()
	ax = fig.add_subplot(111, aspect='equal', projection='3d')
	for data in slices:
		ax.scatter(get(data, 'x'), get(data, 'y'), get(data, 'height'))

# Predict meteor position and velocity distribution using particle filter
particles = particleFilter(slices, particleCount=particleCount, terminalVel=1)

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
		p.parent = particle[5]
		output_step += [p]
	output += [output_step]

# Plot predicted mean particle position for each slice
x = [np.mean(get(o, 'x')) for o in output]
y = [np.mean(get(o, 'y')) for o in output]
z = [np.mean(get(o, 'height')) for o in output]
if particleCount < 10000:
	ax.plot(x,y,z)

# Extrapolate landing sites from particle filter results
if airResistance:
	land = [land(p) for p in list(output[-1])]
	for p in land:
		if particleCount < 10000:
			ax.plot([l[0] for l in p[2]],[l[1] for l in p[2]],[l[2] for l in p[2]])
	landX = [l[0] for l in land]
	landY = [l[1] for l in land]
else:
	landX = [x[-1]-p.vx*p.height/p.vz for p in list(output[-1])]
	landY = [y[-1]-p.vy*p.height/p.vz for p in list(output[-1])]
landLat = [y/111+dat['latitude'][0] for y in landY]
landLon = [x/111/np.cos(np.radians(lat))+dat['longitude'][0] for x, lat in zip(landX, landLat)]
	
# Plot particle trajectories
for x, y, p in zip(landX, landY, output[-1]):
	if airResistance:
		xpath = [p.x]
		ypath = [p.y]
		zpath = [p.height]
	else:
		xpath = [x, p.x]
		ypath = [y, p.y]
		zpath = [0, p.height]
	parent = p.parent
	for bucket in output[:-1][::-1]:
		p = bucket[int(parent)]
		xpath += [p.x]
		ypath += [p.y]
		zpath += [p.height]
		parent = p.parent
	if particleCount < 10000:
		ax.plot(xpath, ypath, zpath, '.-')

# Plot landing sites on the same graph as the radar observations
if particleCount < 10000:
	ax.scatter(landX, landY, 0, c='r')
	ax.scatter(actualX, actualY, 0, c='b')
	plt.show()

# Plot heatmap of landing locations
grid, x_axis, y_axis = np.histogram2d(landLon, landLat, bins=(4*50,4*50), range=[[-87.75, -87.55], [41.4, 41.6]])
grid /= (particleCount/100)
extent = [x_axis[0], x_axis[-1], y_axis[0], y_axis[-1]]
plt.imshow(np.transpose(grid), cmap='hot', interpolation='nearest', extent=extent, origin='lower')
plt.colorbar()
plt.scatter(actualLong,actualLat,c='b',s=5)
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.title('Meteor Landing Site Probability Distribution')
plt.show()