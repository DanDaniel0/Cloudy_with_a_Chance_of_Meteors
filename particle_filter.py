import random
import numpy as np

# Each dataBuckets is an array of DataBucket (also refered to as DataSlice)
# Each dataBucket is an array of points
# Each point has attributes such as .x (x position), .y (y position), .height (height), .relf (reflectivity),
# .d (distance along axis of greatest variation), .n (distance perpendictular to the axis of greatest variation)
# Each particles is an array of particles
# Each particle is an array with the structure of [height, accuracy, zVel, nVel, nPos]

def particleFilter(dataBuckets, particleCount = 1000, cullLimit = 5, terminalVel = "hat"):
	''' Takes in a presliced list of data points, and generates a probability distribution 
		of the meteor position and velocity in each slice using a particle filter.
		particleCount = number of particles to simulate
		cullLimit = relative number of particles to eliminate and replace between steps
		terminalVel = the estimated terminal velocity of the meteor (currently unused)
	'''
	
	results = []
	particles = getParticleHeights(dataBuckets, particleCount, terminalVel) # Randomly initialize a set of particles

	for i in range(len(dataBuckets)): # Cull, repopulate, and update the particles for each step
		
		for particle in particles:
			particle[1] = particleAccuracy(particle, dataBuckets[i]) # Compute how well each particle fits the data

		particles = particles[particles[:,1].argsort()] # Sort particles by accuracy
		counter = len(particles)//cullLimit

		if(i != len(dataBuckets)-1):
			for k, particle in enumerate(particles[:len(particles)//cullLimit,:]): # Replace the least accurate particles
				for j in range(cullLimit-1):
					vari = .35
					p1 = np.copy(particle) # Create new particles similar to the most accurate particles
					p1[2] += (1)*(random.random()-.5)#(particle[2] * ((1+vari)-random.random()*vari*2)) # Randomly vary the new particles
					p1[3] += (1)*(random.random()-.5)
					p1[5] = k
					particles[counter] = p1
					counter += 1
		else:
			particles = particles[:len(particles)//cullLimit]

		results += [[np.copy(p) for p in particles]] # Store the particle distribution at this step to return later
		
		for particle in particles: # Update particle positions using their estimated velocities
			particle[0] -= particle[2]
			particle[4] += particle[3]

	return(results) # Return a list containing the particle distribution at each step

def getParticleHeights(dataBuckets, particleCount, terminalVel):
	''' Randomly generate an initial set of particles '''

	startParticles = np.zeros((particleCount,6))   # Array of particle heights & accuracy
	initialHeights = np.zeros((len(dataBuckets[0]),1))
	initialN = np.zeros((len(dataBuckets[0]),1))

	# Compute rough velocity estimates
	stepVel = ((np.max([b.d for b in dataBuckets[-1]]) - np.min([b.d for b in dataBuckets[0]])))
	terminalVel = np.sqrt((np.max([b.d for b in dataBuckets[-1]]) - np.min([b.d for b in dataBuckets[0]]))**2 \
		+ (np.max([b.height for b in dataBuckets[0]]) - np.min([b.height for b in dataBuckets[-1]]))**2)

	stepVel = stepVel/len(dataBuckets) # Velocity in direction of slicing
	terminalVel = terminalVel/len(dataBuckets) # Total velocity
	bVel = np.sqrt(terminalVel**2- stepVel**2) # Combined vertical and slicing-direction velocity
	# print((terminalVel, stepVel))

	# Compute rough position estimates
	for i,point in enumerate(dataBuckets[0]):
		initialHeights[i] = point.height # height
	for i,point in enumerate(dataBuckets[0]):
		initialN[i] = point.n # horizontal position
	starterMax = max(initialHeights)
	starterMin = min(initialHeights)
	starterNMax = max(initialN)
	starterNMin = min(initialN)

	# Randomly generate particle positions and velocities around estimates
	for i in range(particleCount):
		startParticles[i][0] = starterMax#(random.random() * (starterMax - starterMin)) + starterMin # height
		startParticles[i][4] = (random.random() * (starterNMax - starterNMin)) + starterNMin # horizontal position

		angle = (random.random()*np.pi/4)-(np.pi/8) # angle of motion relative to the ground
		startParticles[i][2] = np.cos(angle)*bVel*((random.random()*.5)+(.75)) # vertical velocity
		startParticles[i][3] = np.sin(angle)*bVel*((random.random()*.5)+(.75)) # horizontal velocity

	return(startParticles)

def particleAccuracy(particle, dataSlice):
	'''We check accuracy here based on aggragate distance from datapoints in the current slice weighted with our reflectivity value'''
	accuracy = 0
	for data in dataSlice:
		accuracy += np.sqrt((np.abs(particle[0] - data.height)**2 + (particle[4] - data.n)**2) * (data.refl+10.5))
	
	return (accuracy)