import re
import math


def getTerms(str):
    splitter = re.compile('\\W*')
    
    words = [w.lower() for w in splitter.split(str)]
    
    uniqueTerms = {}
    for w in words:
        uniqueTerms.setdefault(w, 0)
        uniqueTerms[w] += 1
    
    return uniqueTerms


class docClassifier:
    def __init__(self, getFeatures):
        # for each feature->word counts occurences
        self.featCatCounter={}
        # docs in feature counter
        self.catCounter={}
        self.getFeatures=getFeatures
    
    def incFeatureCatCount(self, feature, category):
        if feature not in self.featCatCounter:
            self.featCatCounter.setdefault(feature, {})
        
        if category not in self.featCatCounter[feature]:
            self.featCatCounter[feature].setdefault(category, 0)
        
        self.featCatCounter[feature][category] += 1
    
    def incDocsInCategory(self, category):
        if category not in self.catCounter:
            self.catCounter.setdefault(category, 0)
        
        self.catCounter[category] += 1
    
    def docsInCategory(self, category):
        if category in self.catCounter:
            return self.catCounter[category]
        
        return 0
    
    def featCatCount(self, feature, category):
        if feature in self.featCatCounter and category in self.featCatCounter[feature]:
            return self.featCatCounter[feature][category]
        
        return 0
    
    def totalDocs(self):
        return sum([self.catCounter[k] for k in self.catCounter])
    
    def totalTerms(self):
        return sum(self.featCatCounter.values())
    
    def getCategories(self):
        return self.catCounter.keys()
    
    def train(self, doc, category):
        terms = getTerms(doc)
        
        for term in terms:
            self.incFeatureCatCount(term, category)
        
        self.incDocsInCategory(category)
    
    def fProb(self, feature, category):
        
        docsInCategory = self.docsInCategory(category)        
        if docsInCategory == 0: return 0
        
        featCounter = self.featCatCount(feature, category)
        return float(featCounter)/docsInCategory
    
    def weightedProb(self, feature, category, assumedProb, weightOfAssumedProb):
        basicProb = self.fProb(feature, category)
        
        # total number of times it has appeared in both categories

        totalFeatureCount = float(sum([self.featCatCounter[feature][i] for i in self.featCatCounter[feature]]))
        
        return ((assumedProb*weightOfAssumedProb) + (totalFeatureCount*basicProb))/(totalFeatureCount + weightOfAssumedProb)


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
    
    # play
    print c1.fProb('quick','good')
    print c1.weightedProb('quick','good', 0.5, 1.0)
    
    for i in range(10000):
        sampletrain(c1)
    
    print ""
    print c1.fProb('quick','good')
    print c1.weightedProb('quick','good', 0.5, 1.0)

if __name__ == '__main__':
    main()
        
    