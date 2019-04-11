import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

dat=pandas.read_csv('KLOT_ParkForest_Refl.csv')
# data=pandas.read_csv('KLOT_ParkForest_Rvel.csv')
N = len(dat)
dat = dat[dat['elevAngle'] > 9]
dat['x'] = pandas.Series(range(N))
dat['y'] = pandas.Series(range(N))

for i in range(2633, N-2632):
	print(dat['longitude'][:])
	dat['x'][i] = (dat['longitude'][i]-['longitude'][2633])*111*np.cosd(dat['latitude'][i]) # km
	dat['y'][i] = (dat['latitude'][i]-['latitude'][2633])*111 # km


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
ax.scatter(dat['x'], dat['y'], dat['heightRel'], c=dat['value'])

plt.show()