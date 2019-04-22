import random
import numpy as np

# Each dataBuckets is an array of DataBucket (also refered to as DataSlice)
# Each dataBucket is an array of points
# Each point has attributes such as .x (x position), .y (y position), .height (height), .relf (reflectivity), .d (distance along axis of greatest variation), .n (distance perpendictular to the axis of greatest variation)
# Each particles is an array of particles
# Each particle is an array with the structure of [height, accuracy, zVel, nVel, nPos]

def get(points, key):
	return [getattr(p,key) for p in points]

def particleFilter(dataBuckets, particleCount = 1000, cullLimit = 5, terminalVel = 1):
	
	results = []
	particles = getParticleHeights(dataBuckets, particleCount, terminalVel) # This gets initial values for the particles

	for i in range(len(dataBuckets)): #This is where we sort, cull, and replace our particles
		
		for particle in particles:
			particle[1] = particleAccuracy(particle, dataBuckets[i])
		particles = particles[particles[:,0].argsort()]
		counter = len(particles)//cullLimit
		if(i != len(dataBuckets)):
			for particle in particles[:len(particles)//cullLimit,:]:
				for j in range(cullLimit-1):
					p1 = np.copy(particle)
					p1[2] -= (particle[2] * (1.5-random.random()*1))
					p1[3] -= (particle[3] * (1.5-random.random()*1))
					counter += 1
			results += [particles]

		for particle in particles: # We move the particles here
			particle[0] -= particle[2]
			particle[4] += particle[3]

	return(results)

def getParticleHeights(dataBuckets, particleCount, terminalVel):
 	
	startParticles = np.zeros((particleCount,5))   #array of particle heights & accuarcy
	initialHeights = np.zeros((len(dataBuckets[0]),1))
	initialN = np.zeros((len(dataBuckets[0]),1))

	stepVel = ((np.max([b.d for b in dataBuckets[-1]]) - np.min([b.d for b in dataBuckets[0]])))
	terminalVel = np.sqrt((np.max([b.d for b in dataBuckets[-1]]) - np.min([b.d for b in dataBuckets[0]]))**2 \
		+ (np.max([b.height for b in dataBuckets[0]]) - np.min([b.height for b in dataBuckets[-1]]))**2)

	stepVel = stepVel/len(dataBuckets)
	terminalVel = terminalVel/len(dataBuckets)


	bVel = np.sqrt(terminalVel**2- stepVel**2)
	print((terminalVel, stepVel))


	for i,point in enumerate(dataBuckets[0]):
		initialHeights[i] = point.height

	for i,point in enumerate(dataBuckets[0]):
		initialN[i] = point.n

	starterMax = max(initialHeights)
	starterMin = min(initialHeights)
	starterNMax = max(initialN)
	starterNMin = min(initialN)

	for i in range(particleCount):
		startParticles[i][0] = (random.random() * (starterMax - starterMin)) + starterMin
		startParticles[i][4] = (random.random() * (starterNMax - starterNMin)) + starterNMin


		angle = (random.random()*np.pi/4)-(np.pi/8)
		startParticles[i][2] = np.cos(angle)*bVel
		startParticles[i][3] = np.sin(angle)*bVel


	return(startParticles)

def particleAccuracy(particle, dataSlice):
	'''We check accuracy here based on aggragate distance from datapoints in the current slice weighted with our reflectivity value'''
	accuracy = 0
	for data in dataSlice:

		accuracy += np.sqrt((np.abs(particle[0] - data.height)**2 + (particle[4] - data.n)**2) * (data.refl+10.5))
	
	return (accuracy)