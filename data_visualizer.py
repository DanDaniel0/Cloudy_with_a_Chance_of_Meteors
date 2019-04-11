import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math

class Point:
	def __init__(self, x, y, refl, height):
		self.x = x
		self.y = y
		self.refl = refl
		self.height = height

def get(points, key):
	return [getattr(p,key) for p in points]

dat=pandas.read_csv('KLOT_ParkForest_Refl.csv')
# data=pandas.read_csv('KLOT_ParkForest_Rvel.csv')
N = len(dat)
points = []
for i in range(N):
	if dat['elevAngle'][i] < 9:
		continue
	x = (dat['longitude'][i]-dat['longitude'][0])*111*math.cos(math.radians(dat['latitude'][i])) # km
	y = (dat['latitude'][i]-dat['latitude'][0])*111 # km
	p = Point(x, y, dat['value'][i], dat['heightRel'][i])
	points.append(p)

# data = {'refl':dat['value'], 'lat':np.zeros(N), 'lon':np.zeros(N), 'height':dat['heightRel']}
# Compute mean lat/lon of each rectangle
# for i in range(N):
# 	x1, y1 = map(float, dat['a'][i].strip('()').split())
# 	x2, y2 = map(float, dat['b'][i].strip('()').split())
# 	x3, y3 = map(float, dat['c'][i].strip('()').split())
# 	x4, y4 = map(float, dat['d'][i].strip('()').split())
# 	data['lat'][i] = (x1+x2+x3+x4)/4
# 	data['lon'][i] = (y1+y2+y3+y4)/4

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', projection='3d')
ax.scatter(get(points, 'x'), get(points, 'y'), get(points, 'height'), c=get(points, 'refl'))

plt.show()
