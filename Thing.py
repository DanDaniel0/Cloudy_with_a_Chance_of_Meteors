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

def get(points, key):
	return [getattr(p,key) for p in points]

def particleFilter(dataBuckets, particleCount = 1000, cullLimit = 5, terminalVel = 1):
	
	results = []
	particles = getParticleHeights(dataBuckets, particleCount, terminalVel)

	for i in range(len(dataBuckets)):   # NEED TO UPDATE PARTICLES
		#main loopy thing for each step

		#if(i):
		#	terminalVel = (np.mean([b.height for b in dataBuckets[i-1]]) - np.mean([b.height for b in dataBuckets[i]]))
		#else:
		#	terminalVel = (np.mean([b.height for b in dataBuckets[0]]) - np.mean([b.height for b in dataBuckets[1]]))

		#particles is a 2d array[heights, accuracy (low is better)]
		for particle in particles:
			particle[1] = particleAccuracy(particle, dataBuckets[i])
		particles = particles[particles[:,0].argsort()]
		# particles = particles[:len(particles)//cullLimit,:]
		counter = len(particles)//cullLimit
		if(i != len(dataBuckets)):
			for particle in particles[:len(particles)//cullLimit,:]:
				for j in range(cullLimit-1):
					p1 = np.copy(particle)
					p1[2] -= (particle[2] * (1.5-random.random()*1))
					p1[3] -= (particle[3] * (1.5-random.random()*1))
					# particles[counter] = p1
					counter += 1
			results += [particles]
		for particle in particles: # Move the particles here
			particle[0] -= particle[2]
			particle[4] += particle[3]


	# heightPerStep = (np.mean([b.height for b in dataBuckets[0]]) - np.mean([b.height for b in dataBuckets[len(dataBuckets)-1]]))/ len(dataBuckets) #height per step
	# terminalVel = heightPerStep
	# xVel = (np.mean([b.x for b in dataBuckets[0]]) - np.mean([b.x for b in dataBuckets[len(dataBuckets)-1]]))/ len(dataBuckets)
	# yVel = (np.mean([b.x for b in dataBuckets[0]]) - np.mean([b.x for b in dataBuckets[len(dataBuckets)-1]]))/ len(dataBuckets)


	# groundPos = np.zeros((len(results[-1]),1))

	# for i,data in enumerate(results[len(results) - 1]):
	# 	stepsTillGround	= data[0]/heightPerStep
	# 	groundPosX[i] = stepsTillGround * xVel
	# 	groundPosY[i] = stepsTillGround * yVel

	
	return(results) #, (groundPosX, groundPosY))


def getParticleHeights(dataBuckets, particleCount, terminalVel):
 	
 	#height, accuracy, zVel, nVel, nPos
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

	#range(1,particleCount+1)
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

	accuracy = 0
	for data in dataSlice:

		accuracy += np.sqrt((np.abs(particle[0] - data.height)**2 + (particle[4] - data.n)**2) * (data.refl+10.5))
	
	return (accuracy)