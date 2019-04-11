#To Do:
#
# - Load data and get into useable fomt. (Dictionary)
# - Load Wind Data
# - Find Orentaion
# - Partilce filter for 3 space
# - Function for Landing Prediction (Kinematics)
# - Landing Visualization 2D
# - Landing Visulalaztion 3D
import random
import numpy as np



def ParticleFilter(dataBuckets, particleCount = 1000, cullLimit = .5, terminalVel = 600):
	
	particles = GetParticleHeights(dataBuckets[0], particleCount)

	for i in range(len(dataBuckets)):   # NEED TO UPDATE PARTICLES
		#main loopy thing for each step

		#particles is a 2d array[heights, accuracy (low is better)]
		for particle in particles:
			particle[1] = ParticleAccuracy(particle[0] - (terminalVel * random.random()), dataBuckets[i])

		particleMedian = np.median(particles[:,1])

		if(i == len(dataBuckets)):
			for particle in particles:
				if (particle[1] < np.median(particles) * cullLimit): #if something is broken try reversing the greater than sign
					particle[0] -= (terminalVel * (1+random.random()*.25))
				else:
					#assign new height here
					particle = np.mean(particles[:,0]) + ((.5 - random.random()) * np.std(particles[:,0] * .5))

	return(particles)


def GetParticleHeights(dataBucket, particleCount):

	startParticles = np.zeros((particleCount,2)) #array of particle heights & accuarcy
	initialHeights = np.zeros((len(dataBucket),1))

	for i,point in enumerate(dataBucket):
		initialHeights[i] = point.height

	range(1,particleCount+1)
	starterMax = max(initialHeights)
	starterMin = min(initialHeights)

	for i in range(particleCount):
		startParticles[i][0] = (random.random() * (starterMax - starterMin)) + starterMin

	return(startParticles)


def ParticleAccuracy(height, dataSlice):

	accuarcy = 0
	for data in dataSlice:
		accuarcy += (np.abs(height - data.height) * data.refl)
	
	return accuarcy;