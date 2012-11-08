import re
import math


def getTerms(str):
    splitter = re.compile('\\W*')
    
    words = [w.lower() for w in splitter.split(str)]
    
    uniqueTerms = {}
    for w in words:
        if len(w) < 2 or len(w) > 25: continue
        
        uniqueTerms.setdefault(w, 0)
        uniqueTerms[w] += 1
    
    return uniqueTerms




class docClassifier:
    def __init__(self, getFeatures):
        # for each feature->word counts occurances
        self.itemsInCatWithFeatCounter={}
        # docs in feature counter
        self.catCounter={}
        self.getFeatures=getFeatures
        self.thresholds = {}
        self.min = {}
    
    
    # for each feature keep track of the docs the feat is in
    # for each of the categories ...
    def incFeatureCatCount(self, feature, category):
        if feature not in self.itemsInCatWithFeatCounter:
            self.itemsInCatWithFeatCounter.setdefault(feature, {})
        
        if category not in self.itemsInCatWithFeatCounter[feature]:
            self.itemsInCatWithFeatCounter[feature].setdefault(category, 0)
        
        self.itemsInCatWithFeatCounter[feature][category] += 1
    

    
    # how many items are in each category
    def incItemsInCategory(self, category):
        if category not in self.catCounter:
            self.catCounter.setdefault(category, 0)
        
        self.catCounter[category] += 1
    
    
    def getItemsInCategory(self, category):
        if category in self.catCounter:
            return self.catCounter[category]
        
        return 0
    
    def getCountOfItemsInCatWithFeat(self, feature, category):
        if feature in self.itemsInCatWithFeatCounter and category in self.itemsInCatWithFeatCounter[feature]:
            return self.itemsInCatWithFeatCounter[feature][category]
        
        return 0
    
    
    def getTotalItems(self):
        return sum([self.catCounter[k] for k in self.catCounter])
    
    
    def getTotalFeatures(self):
        return sum(self.itemsInCatWithFeatCounter.values())
    
    
    # get a list of available categories
    def getCategories(self):
        return self.catCounter.keys()
    
    
    # Break the item into features and add each feature into our model
    def train(self, item, category, featureFunct=getTerms):
        features = featureFunct(item)
        
        for feature in features:
            self.incFeatureCatCount(feature, category)
        
        self.incItemsInCategory(category)
    
    # what is the probability that this feature belongs in the given category
    # Documents in cat with feat/all documents in category
    #
    def fProb(self, feature, category):
        docsInCategory = self.getItemsInCategory(category)
        if docsInCategory == 0: return 0
        
        docsWithFeatInCatCount = self.getCountOfItemsInCatWithFeat(feature, category)
        return float(docsWithFeatInCatCount)/docsInCategory
    
    
    def weightedProb(self, feature, category, assumedProb=0.5, weightOfAssumedProb=1.0):
        basicProb = self.fProb(feature, category)
        
        # total number of times the feature has appeared in all categories
        totalFeatureCount = float(sum([self.fProb(feature, i) for i in self.getCategories()]))
        
        return ((assumedProb*weightOfAssumedProb) + (totalFeatureCount*basicProb))/(totalFeatureCount + weightOfAssumedProb)
    
    
    def weightedProb2(self, feature, category, probFunction, assumedProb=0.5, weightOfAssumedProb=1.0):
        basicProb = probFunction(feature, category)
        
        # total number of times the feature has appeared in all categories
        totalFeatureCount = float(sum([self.fProb(feature, i) for i in self.getCategories()]))
        
        return ((assumedProb*weightOfAssumedProb) + (totalFeatureCount*basicProb))/(totalFeatureCount + weightOfAssumedProb)
    
    # likelihood that the doc belongs in the given category
    def getItemNaiveProb(self, item, category, probFunction):
        
        # P(C)
        categoryProbability = float(self.getItemsInCategory(category))/self.getTotalItems()
        
        
        # P(I|C)
        features = self.getFeatures(item)
        p = 1.0
        for f in features:
            p *= probFunction(f, category)

        
        # = P(I|C)*P(C)*P(I)
        return (p*categoryProbability)
    
    def getThreshold(self, category):
        if category in self.thresholds:
            return self.thresholds[category]
        
        return 1
    
    
    def setThreshold(self, category, catThreshold):
        self.thresholds[category] = catThreshold

    
    def getMin(self, category):
        if category in self.min:
            return self.min[category]
        
        return 0.0
    
    
    def setMin(self, category, minimum):
        self.min[category] = minimum
        
    
    def getItemClassification(self, item, defaultCat='default'):
        categories = self.getCategories()
        
        results = {}
        bestResult = 0.0
        bestCat = None
        
        # compute the sim of the doc to each category
        # and maintain results
        for cat in categories:
            results[cat] = self.getItemNaiveProb(item, cat, self.weightedProb)
            
            if results[cat] > bestResult:
                bestResult = results[cat]
                bestCat = cat
        
        # ensure that the thresholds are upheld
        bestCatWeight = 1.0
        if bestCat in self.thresholds: bestCatWeight = self.thresholds[bestCat]
        
        for r in results.keys():
            if r == bestCat: continue
            
            if bestCatWeight*results[r] > bestResult:
                return defaultCat
        
        return bestCat

    ######
    # fisher's method
    def fishersFeatureClassifier(self, feature, category):
        basicProb = self.fProb(feature, category)
        
        if basicProb == 0: return 0

        totalFeatureFreq = float(sum([self.fProb(feature, i) for i in self.itemsInCatWithFeatCounter[feature]]))
        
        return basicProb/totalFeatureFreq
    
    
    def fishersClassifier(self, item, category):
        
        features = self.getFeatures(item)
        
        p = 1.0
        for f in features:
            p *= self.weightedProb2(f, category, probFunction=self.fishersFeatureClassifier)
        
        fscore = -2*math.log(p)
        
        return self.invChi2(fscore, len(features)*2)
    
    def invChi2(self, chi, df):
        m = chi /2.0
        sm = term = math.exp(-m)
        
        for i in range(1, df//2):
            term *= m/i
            sm += term
            
        return min(sm, 1.0)


    def getItemFisherClassification(self, item, defaultCat='default'):
        categories = self.getCategories()
        
        results = {}
        bestResult = 0.0
        bestCat = None
        
        # compute the sim of the doc to each category
        # and maintain results
        for cat in categories:
            results[cat] = self.fishersClassifier(item, cat)
            
            if results[cat] > bestResult and results[cat] > self.getMin(cat):
                bestResult = results[cat]
                bestCat = cat
        
        return bestCat










def sampletrain(cl):
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')
    cl.train('the quick brown fox jumps','good')

def main():
    
    c1 = docClassifier(getTerms);
    # train
    sampletrain(c1)
    

    print c1.getItemFisherClassification('quick rabbit', defaultCat='unknown')
    
    
    print 'xxxxx'
    
    print c1.getItemNaiveProb('quick rabbit', 'good', c1.weightedProb)
    print c1.getItemNaiveProb('quick rabbit', 'bad', c1.weightedProb)
    
    print c1.getItemClassification('quick rabbit', defaultCat='unknown')
    print c1.getItemClassification('quick money', defaultCat='unknown')
    
    c1.setThreshold('bad', 3.0)
    print c1.getItemClassification('quick money', defaultCat='unknown')
    
    for i in range(10000):
        sampletrain(c1)
    
    print c1.getItemClassification('quick money', defaultCat='unknown')
    # play
    #print c1.fProb('quick','good')
    #print c1.weightedProb('quick','good', 0.5, 1.0)
    
    #for i in range(10000):
    #    sampletrain(c1)
    
    #print ""
    #print c1.fProb('quick','good')
    #print c1.weightedProb('quick','good', 0.5, 1.0)

if __name__ == '__main__':
    main()
        
    