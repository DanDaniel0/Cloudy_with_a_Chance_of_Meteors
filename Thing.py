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



def particleFilter(dataBuckets, particleCount = 1000, cullLimit = 1, terminalVel = 600):
	
	results = []
	particles = getParticleHeights(dataBuckets[0], particleCount)

	for i in range(len(dataBuckets)):   # NEED TO UPDATE PARTICLES
		#main loopy thing for each step

		#particles is a 2d array[heights, accuracy (low is better)]
		for particle in particles:
			particle[1] = particleAccuracy(particle[0] - (terminalVel * random.random()), dataBuckets[i])

		particleMedian = np.median(particles[:,1])

		if(i != len(dataBuckets)):
			new_particles = np.zeros((len(particles),2))
			count = 0
			for i, particle in enumerate(particles):
				if (particle[1] < particleMedian * cullLimit): #if something is broken try reversing the greater than sign
					p1 = np.copy(particle)
					p1[0] -= (terminalVel * (1.25-random.random()*.5))
					p2 = np.copy(particle)
					p2[0] -= (terminalVel * (1.25-random.random()*.5))
					new_particles[count] =  p1
					new_particles[count+1] = p2
					count += 2
			particles = new_particles
			results += [particles]
	return(results)


def getParticleHeights(dataBucket, particleCount):

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


def particleAccuracy(height, dataSlice):

	accuracy = 0
	for data in dataSlice:
		accuracy += (np.abs(height - data.height) * (data.refl+10.5))
	
	return accuracy;