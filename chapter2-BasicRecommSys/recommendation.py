from math import *
import operator

# A dictionary of movie critics and their ratings of a small
# set of movies
critics={
    'Lisa Rose': 
        {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,'The Night Listener': 3.0},
    'Gene Seymour': 
        {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 3.5},
    'Michael Phillips': 
        {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,'Superman Returns': 3.5, 'The Night Listener': 4.0},
    'Claudia Puig': 
        {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,'The Night Listener': 4.5, 'Superman Returns': 4.0,'You, Me and Dupree': 2.5},
    'Mick LaSalle': 
        {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,'You, Me and Dupree': 2.0},
    'Jack Matthews': 
        {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
    'Toby': 
        {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}
}


def simPearson(prefernce, user1, user2):
    
    common = {}
    for pref in prefernce[user1]:
        if pref in prefernce[user2]:
            common[pref] = 1
    
    n = len(common)
    
    if n == 0:
        return 0
    
    sumUser1 = sum([prefernce[user1][it] for it in common])
    sumUser2 = sum([prefernce[user2][it] for it in common])
    
    sumUserSq1 = sum([pow(prefernce[user1][it],2) for it in common])
    sumUserSq2 = sum([pow(prefernce[user2][it],2) for it in common])
    
    sumOfProducts = sum([prefernce[user1][it]*prefernce[user2][it] for it in common])
    
    num = sumOfProducts - (sumUser1*sumUser2/n)
    denum = sqrt((sumUserSq1-pow(sumUser1,2)/n)*(sumUserSq2-pow(sumUser2,2)/n))
    
    if denum == 0:
        return 0
    
    return num/denum


def simDistance(prefs, user1, user2):
    # Get the list of shared_items
    si={}
    for item in prefs[user1]:
        if item in prefs[user2]:
            si[item]=1

    if len(si)==0: 
        return 0
    
    # Add up the squares of all the differences
    sum_of_squares=sum([pow(prefs[user1][item]-prefs[user2][item],2)
                        for item in prefs[user1] if item in prefs[user2]])
    return 1/(1+sum_of_squares)




def bestMatches(pref, user1, simfunction=simPearson):
    bestMatches = [(simfunction(pref, user1, user), user) for user in pref if user != user1]
    
    bestMatches = sorted(bestMatches, reverse=True)
    return bestMatches[:5]

def findBestMovies(pref, user1):
    bestMatches = [(simPearson(pref, user1, user), user) for user in pref if user != user1]
    
    bestMatches = sorted(bestMatches, reverse=True)
    bestMatches = bestMatches[:3]
    
    print bestMatches
    
    moviesWeight = {}
    movieSimTotal = {}
    
    for simScore in bestMatches:
        (score, user) = simScore
        for movie in pref[user]:
            if movie in pref[user1]:
                continue
            
            if movie not in moviesWeight:
                moviesWeight[movie] = 0
                movieSimTotal[movie] = 0;
                
            moviesWeight[movie] += pref[user][movie]*score
            movieSimTotal[movie] += score
    
    for movie in moviesWeight:
        moviesWeight[movie] = moviesWeight[movie]/movieSimTotal[movie]
    
    moviesWeight = sorted(moviesWeight.iteritems(), key=operator.itemgetter(1), reverse=True)
    print moviesWeight
    

def transform(userMovies):
    t = {}
    for user in userMovies:
        for movie in userMovies[user]:
            if movie not in t:
                t[movie] = {}
            
            t[movie][user] = userMovies[user][movie]
        
    return t

def findMoviesBestMatches(pref):
    bestMatchingMovies = {}
    tCritics = transform(pref)
    for movie in tCritics:
        bestMatchingMovies[movie] = bestMatches(tCritics, movie, simDistance)
        
    return bestMatchingMovies

def itemBasedMatching(pref, user):
    bestMatchesList = findMoviesBestMatches(pref)   
    
    movieSim= {}
    movieSimSum = {}
    
    for movie in pref[user]:
        for matchMovie in bestMatchesList[movie]:
            (simScore, movieName) = matchMovie
            
            # movie was already rated/watched
            if movieName in pref[user]:
                continue
            
            if movieName not in movieSim:
                movieSim[movieName] = 0
                movieSimSum[movieName] = 0
                
            movieSim[movieName] += simScore*pref[user][movie]
            movieSimSum[movieName] += simScore # or pref[user][movie]
            
    weightedMovies = [(m, movieSim[m]/movieSimSum[m]) for m in movieSim]
    weightedMovies = sorted(weightedMovies, key=secondTupleKey, reverse=True)
    
    print weightedMovies
    return weightedMovies
     
def secondTupleKey(t):
    return t[1]


def readLensesData(ratingsFileName, moviesFileName):
    critics = {}
    movies = {}
    
    # read movies first
    f = open(moviesFileName, 'r')
    for line in f:
        parts = line.strip().split('::')
        title = parts[1]
        id = parts[0]
        
        movies[id] = title
        
    f.close()
    
    f = open(ratingsFileName, 'r')
    for line in f:
        parts = line.strip().split('::')
        user = parts[0]
        movieId = parts[1]
        movieTitleStr = movies[movieId]
        rating = parts[2]
        
        if user not in critics:
            critics[user] = {}
            
        critics[user][movieTitleStr] = float(rating)
            
    f.close()
    return critics

def main():
    #findBestMovies(critics, "Michael Phillips")
    #print "now recommending similar movies ... 'Superman Returns'"
    #findBestMovies(critics, 'Toby')
    #itemBasedMatching(critics, 'Toby')
    
    critics = readLensesData('groupLensData\\ml-1m\\ratings.dat', 'groupLensData\\ml-1m\\movies.dat')
    
    print critics['87']
    t = transform(critics)

    print bestMatches(t, 'Castle, The (1997)')
    #print t #critics
    
if __name__ == '__main__':
    main()
    
