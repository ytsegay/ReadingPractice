import random
import math

# assumes v1 and v2 are of the same
# length and contain numerical data
def euclideanDistance(v1, v2):
    
    sum = 0.0
    for i in range(len(v1)):
        sum += (v1[i] - v2[i])**2
    
    return math.sqrt(sum)


def gaussianWeight(d, sigma=10.0):
    return math.e**(-d**2/(2*sigma**2))


# ranks training data in decreasing order of distance
def similarityRank(rows, v1, distFunction=euclideanDistance):    
    results = []
    for i in range(len(rows)):
        d = distFunction(rows[i]['input'], v1['input'])
        results.append((d, i))
    
    results.sort()
    
    return results



def weightedOutcomes(rows, v1, k=5, distFunction=euclideanDistance, weightFunction=gaussianWeight):
    results = similarityRank(rows, v1, distFunction)
    weightsTotal = 0.0 
    sum = 0.0
    
    for i in range(k):
        weight = results[i][0]
        index = results[i][1]
        
        sum += weight*rows[index]['result']
        weightsTotal += weight
    
    return sum/weightsTotal


def divideSet(rows, testPortion=0.05):
    shuffledRows = rows[:]
    random.shuffle(shuffledRows)
    
    howmanyTestEntries = int(float(len(rows))*testPortion)
    testSet = [shuffledRows[i] for i in range(howmanyTestEntries)]
    trainSet = [shuffledRows[i] for i in range(howmanyTestEntries, len(shuffledRows))]
    
    return trainSet,testSet


def crossValidate(rows, k=5, repeatTimes=100):
    errorRate = 0.0
    
    for i in range(repeatTimes):
        trainSet,testSet = divideSet(rows)
        error = 0.0 
        for row in testSet:
            d = weightedOutcomes(trainSet, row, k)
            error += math.sqrt((row['result'] - d)**2)
        
        errorRate += (error/len(testSet))
    return (errorRate/repeatTimes)


def rescale(rows, scale):
    scaledRows = []
    for row in rows:
        r = []
        for i in range(len(scale)):
            r.append(row['input'][i]*scale[i])
        
        d = {}
        d['input'] = r[:]
        d['result'] = row['result']
        scaledRows.append(d)
        
    return scaledRows


def randomScaleOptimization(rows, domains):
    bestScale = None
    bestScaleCrossValidError = 99999.0
    
    for j in range(1000):
        # generate a random seed
        scale = []
        for i in range(len(domains)):
            scale.append(random.uniform(domains[i][0], domains[i][1]))
        

        scaledRows = rescale(rows, scale)
        ce = crossValidate(scaledRows, k=3, repeatTimes=20)
        
        if ce < bestScaleCrossValidError:
            bestScaleCrossValidError = ce
            bestScale = scale[:]
            print j,' ',bestScaleCrossValidError,' ',bestScale
    
    return bestScaleCrossValidError,bestScale



def hillClimbScaleOptimization(rows, domains):   

    prevCe = 0.0
    prevScale = None
    
    # generate a random seed
    scale = []
    step = 1.0
    for i in range(len(domains)):
        scale.append(random.uniform(domains[i][0], domains[i][1]))
        
    scaledRows = rescale(rows, scale)
    bestCe = crossValidate(scaledRows, k=3, repeatTimes=20)

    while 1:
        scales = []
        
        # create a potential set of scales with deltas
        for i in range(len(domains)):
            if (scale[i] - step) >= domains[i][0]:
                scales.append(scale[:i] + [scale[i] - step] + scale[i+1:])
            if (scale[i] + step) <= domains[i][1]:
                scales.append(scale[:i] + [(scale[i] + step)] + scale[i+1:])
        
        for s in scales:
            cce = crossValidate(rescale(rows, s), k=3, repeatTimes=20)
            
            if cce < bestCe:
                bestCe = cce
                scale = s[:]
                print 'HillClimb: ',bestCe
        
        if scale == prevScale:
            break
        
        prevCe =  bestCe
        prevScale = scale[:]
        
    return scale,bestCe




def simAnealingScaleOptimization(rows, domains, T=1000.0, cool=0.95):   
    # generate a random seed
    scale = []
    bestCe = 0.0
    
    for i in range(len(domains)):
        scale.append(random.randint(domains[i][0], domains[i][1]))
    
    while T>0.01:
    
        i = random.randint(0, len(domains)-1)
        dom = domains[i]
        step = 1.0
        direction = step #random.uniform(0, dom[2])
        
        if random.random() < 0.5:
            direction = -step
        
        modScale = scale[:]
        modScale[i] += direction
        #print modScale
        
        scaleCost = crossValidate(rescale(rows, scale), k=5, repeatTimes=10)
        modCost = crossValidate(rescale(rows, modScale), k=5, repeatTimes=10)
        
        
        p=pow(math.e,(-scaleCost-modCost)/T)
        
        if modCost < scaleCost or random.random() < p:
            scale = modScale[:]
            bestCe = modCost
            print 'SimAnealing: ',bestCe
        
        T *= cool
        
    return scale,bestCe







########################################
# wines data generation goes here
#####
def wineprice(rating,age):
    peak_age=rating-50
    
    # Calculate price based on rating
    price=rating/2
    
    if age>peak_age:
        # Past its peak, goes bad in 5 years
        price=price*(5-(age-peak_age))
    else:
        # Increases to 5x original value as it
        # approaches its peak
        price=price*(5*((age+1)/peak_age))
    if price<0: price=0
    
    return price

def wineset1( ):
    rows=[]
    for i in range(300):

        # Create a random age and rating
        rating=random.random( )*50+50
        age=random.random( )*50
        aisle=float(random.randrange(1,20))
        bottlesize=[375.0,750.0,1500.0,3000.0][random.randrange(0,3)]

        # Get reference price
        price=wineprice(rating,age)
        price*=(bottlesize/750)
        
        # Add some noise
        price*=(random.random( )*0.9+0.2)

        # Add to the dataset
        rows.append({'input':(rating,age,aisle,bottlesize), 'result':price})
    return rows

def main():
    r = wineset1()
    #for a in r:
    #    print a
    
    #print r[0]
    #print euclideanDistance(r[0]['input'], r[1]['input'])
    #print weightedOutcomes(r[1:], r[0])
    
    #for i in range(1,100):
    #    print '',i,'\t',crossValidate(r, i)

    scaleRanges = [(0,20)]*4 #[(0.0, 20.0,0.01),(0.0, 20.0,0.01),(0.0, 25.0,0.01),(0.0,20.0,0.01)]
    #randomScaleOptimization(r, scaleRanges)
    
    bestHillOutcome, bestScale = 10000.0,None
    for j in range(100):
        s,b = hillClimbScaleOptimization(r, scaleRanges)
        if b < bestHillOutcome :
            bestHillOutcome = b
            bestScale = s[:]
        print '',j,' ',bestHillOutcome,' ',bestScale
    print bestHillOutcome, bestScale
    print simAnealingScaleOptimization(r, scaleRanges)
 
if __name__ == '__main__':
    main()