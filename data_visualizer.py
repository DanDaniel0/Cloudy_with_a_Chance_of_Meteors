import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from Thing import *

class Point:
	def __init__(self, x, y, refl, height):
		self.x = x
		self.y = y
		self.refl = refl
		self.height = height

def get(points, key):
	return [getattr(p,key) for p in points]

def slice(points, angle=np.pi/4, n_slices=5):
	slices = [[] for n in range(n_slices)]
	d = [project(p.x,p.y,angle) for p in points]
	dmin = min(d)
	dmax = max(d)
	delta = (dmax-dmin)/n_slices
	for i, point in enumerate(points):
		slices[min(int((d[i]-dmin)/delta),n_slices-1)] += [point]
	return slices
		
def project(x, y, angle):
	return np.cos(angle)*x+np.sin(angle)*y

dat=pandas.read_csv('KLOT_ParkForest_Refl.csv')
N = len(dat)
points = []
for i in range(N):
	if dat['elevAngle'][i] < 9:
		continue
	x = (dat['longitude'][i]-dat['longitude'][0])*111*np.cos(np.radians(dat['latitude'][i])) # km
	y = (dat['latitude'][i]-dat['latitude'][0])*111 # km
	p = Point(x, y, dat['value'][i], dat['heightRel'][i]/1000)
	points.append(p)

slices = slice(points, n_slices=6)

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', projection='3d')
# ax.scatter(get(points, 'x'), get(points, 'y'), get(points, 'height'), c=get(points, 'refl'))
# ax.scatter(get(slices[0], 'x'), get(slices[0], 'y'), get(slices[0], 'height'), c='k')
# ax.scatter(get(slices[1], 'x'), get(slices[1], 'y'), get(slices[1], 'height'), c='b')
# ax.scatter(get(slices[2], 'x'), get(slices[2], 'y'), get(slices[2], 'height'), c='g')
for data in slices:
	ax.scatter(get(data, 'x'), get(data, 'y'), get(data, 'height'))

# plt.show()

output = particleFilter(slices, particleCount=10000, terminalVel=1)
x = []
y = []
z = []
for data, particles in zip(slices[1:], output):
	x += [np.mean(get(data, 'x'))]
	y += [np.mean(get(data, 'y'))]
	z += [np.mean(list(particles[:,0]))]
ax.plot(x,y,z)

direction = [x[-1]-x[0], y[-1]-y[0], z[-1]-z[0]]
direction = [d/direction[2] for d in direction]
landX = [x[-1]-direction[0]*h for h in list(output[-1][:,0])]
landY = [y[-1]-direction[1]*h for h in list(output[-1][:,0])]
ax.scatter(landX, landY, 0)

# plt.hist(output[0][:,0], 100)
# plt.hist(output[1][:,0], 100)
# plt.hist(output[2][:,0], 100)
# plt.legend(['1','2','3'])
plt.show()
plt.hist(landX, 100)
plt.show()