import random
import math
import time


people = [('Seymour','BOS'),
		  ('Franny','DAL'),
		  ('Zooey','CAK'),
		  ('Walt','MIA'),
		  ('Buddy','ORD'),
		  ('Les','OMA')]

destination = 'LGA'


def readFlights(fileName):
	f = open(fileName, 'r')
	
	flights = {}
	for line in f:
		origin,dest,deptTime,arrTime,price=line.strip().split(',')
		flights.setdefault((origin,dest), [])
						
		flights[(origin,dest)].append((deptTime,arrTime,float(price)))
	
	return flights

def getMinutes(t):
	x=time.strptime(t,'%H:%M')
	return x[3]*60+x[4]


def printSchedule(row, flights):
	for i in range(len(row)/2):
		
		person = people[i][0]
		origin = people[i][1]
		
		inboundFlight = flights[(origin,destination)][row[i*2]]
		outbountFlight = flights[(destination,origin)][row[i*2+1]]
		
		print "%10s%10s %5s-%5s $%3s %5s-%5s $%3s" % (
												person, origin, 
												inboundFlight[0],
												inboundFlight[1],
												inboundFlight[2],
												outbountFlight[0],
												outbountFlight[1],
												outbountFlight[2])
		

def scheduleCost(row, flights):
	
	travelCost = 0.0
	waitingCost = 0.0 
	lateVehicleReturnCost = 0.0
	
	latestArrival = 0
	earliestDepart = 9999 # or 24*60
	
	# travel costs
	for i in range(len(row)/2):
		origin = people[i][1]
		
		inboundFlight = flights[(origin,destination)][row[i*2]]
		outbountFlight = flights[(destination,origin)][row[i*2+1]]
		
		travelCost += inboundFlight[2]
		travelCost += outbountFlight[2]
		
		# find the earliest departure and latest arrival
		if getMinutes(inboundFlight[1]) > latestArrival: latestArrival = getMinutes(inboundFlight[1])
		if getMinutes(outbountFlight[0]) < earliestDepart: earliestDepart = getMinutes(outbountFlight[0])
	
	# cost the wait time in the airport
	for i in range(len(row)/2):
		origin = people[i][1]
		
		inboundFlight = flights[(origin,destination)][row[i*2]]
		outbountFlight = flights[(destination,origin)][row[i*2+1]]
		
		# the cost of waiting is $0.5
		waitingCost += (latestArrival - getMinutes(inboundFlight[1]))*0.5
		waitingCost += (getMinutes(outbountFlight[0]) - earliestDepart)*0.5
	
	# if they return the vehicle later than they have picked it up
	# they will be charged 50 bucks more but this could be on an hourly basis too
	# say 20 bucks an hour
	# lateVehicleReturnCost = 20*((earliestDepart-latestArrival)/60)
	if earliestDepart >  latestArrival:
		lateVehicleReturnCost = 50
		
	return lateVehicleReturnCost + waitingCost + travelCost


def randomOptimization(flights, costFunction=scheduleCost):
	
	rWithLowestCost = []
	lowestCost = 9999
	for i in range(1000):
		r = []
		for j in range(len(people)):
			r.append(random.randint(0,8))
			r.append(random.randint(0,8))
			
		cost = costFunction(r, flights)
		if cost < lowestCost: 
			lowestCost = cost
			rWithLowestCost = r[:]
	
	return (lowestCost,rWithLowestCost)


def hillClimb(flights, costFunction=scheduleCost):
	bestRow = []
	bestCost = 99999
	
	lastBestRow = []
	
	# start off with a randomly selected schedule
	for j in range(len(people)):
		bestRow.append(random.randint(0,8))
		bestRow.append(random.randint(0,8))
	
	bestCost = costFunction(bestRow, flights)
	
	# now fins the neighbour with the lowest cost  
	while 1:
		# get all neighbours
		neighbours = []
		for i in range(len(bestRow)):
			if bestRow[i] + 1 < 9:
				neighbours.append(bestRow[:i] + [bestRow[i]+1] + bestRow[i+1:])
			if bestRow[i] + 1 >= 0:
				neighbours.append(bestRow[:i] + [bestRow[i]-1] + bestRow[i+1:])
				
		for r in neighbours:
			cost = costFunction(r, flights)
			if cost < bestCost:
				bestCost = cost
				bestRow = r[:]
		
		if bestRow == lastBestRow:
			break
		
		lastBestRow = bestRow
		printSchedule(bestRow, flights)
		print "hill climb: $",bestCost
	
	return bestRow
	
				
		
def main():
	flights = readFlights('flightsFile.dat')

	r = [1,4,3,2,7,3,6,3,2,4,5,3]
	printSchedule(r, flights)
	print scheduleCost(r, flights)
	
	
	# random
	returned = randomOptimization(flights)
	printSchedule(returned[1], flights)
	print "Rand: $", returned[0]
	
	
	# hill climb
	hillClimb(flights)
	
if __name__ == '__main__':
	main()