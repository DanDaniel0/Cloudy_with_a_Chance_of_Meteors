import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

recovered = pandas.read_csv('RecoveredMeteors.csv')
landLat = [recovered['lat'][i] for i in range(len(recovered['lat']))]
landLong = [recovered['long'][i] for i in range(len(recovered['long']))]

plt.scatter(landLong,landLat,c='b')
plt.show()