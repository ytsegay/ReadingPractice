class decisionTree:
    def __init__(self, rows, colNo=None, colValue=None, outcomes=None, trueBranch=None, falseBranch=None):
        self.colNo = colNo
        self.colValue = colValue
        self.outcomes = outcomes
        self.trueBranch = trueBranch
        self.falseBranch = falseBranch
    
    
    
    def divideRows(self, rows, colNo, partitionValue):
        if colNo < 0 or colNo >= len(rows[0])-1 or len(rows) == 0 or len(rows[0]) == 0:
            return ([], [])
        
        partition = None
        if isinstance(partitionValue, int) or isinstance(partitionValue, float):
            partition = lambda x: x >= partitionValue
        else:
            partition = lambda x: x == partitionValue
        
        subset1 = [row for row in rows if partition(row[colNo])]
        subset2 = [row for row in rows if not partition(row[colNo])]
        
        return (subset1, subset2)
    
    
    def entropy(self, rows, predictCol):
        import math
        
        # step 1 get the predictor column
        # and count each category/outcome frequency
        countOfPredictorColValues = {}
        for row in rows:
            countOfPredictorColValues.setdefault(row[predictCol], 0)
            countOfPredictorColValues[row[predictCol]] += 1
        
        e = 0.0 # e is for entropy :)
        
        # calculate entropy
        for r in countOfPredictorColValues.keys():
            p = float(countOfPredictorColValues[r])/len(rows)
            e = e - p*math.log(p)
        
        return e
    
    
    # computes the current full list's entropy
    # divides the list using each column's values
    # compute information gain .... 
    def constructTree(self, rows, colsVisited):

        bestInfoGain = 0.0
        bestS1,bestS2 = None,None
        bestCol = None
        bestSplitValue = None
        
        predictorCol = len(rows[0])-1
        rowsEntropy = self.entropy(rows, predictorCol)
        
        # try each column
        for col in range(len(rows[0])):
            if col in colsVisited: continue
            
            # get each column's unique and use it as a divider
            colValues = {}
            for r in rows:
                colValues[r[col]] = 1
        
            # now try and split on all col values
            for c in colValues.keys():
                (s1, s2) = self.divideRows(rows, col, c)
                
                es1 = self.entropy(s1, predictorCol)
                es2 = self.entropy(s2, predictorCol)
                
                es1Weight = float(len(s1))/len(rows)
                
                infoGain = rowsEntropy - es1Weight*es1 - (1-es1Weight)*es2
                
                if infoGain > bestInfoGain and len(s1) > 0 and len(s2) > 0:
                    bestInfoGain = infoGain
                    bestS1,bestS2 = (s1, s2)
                    bestCol = col
                    bestSplitValue = c

        if(bestInfoGain > 0.0):
            colsVisited.append(col)
            yesNode = self.constructTree(bestS1, colsVisited)
            noNode = self.constructTree(bestS2, colsVisited)
            return decisionTree(s1, colNo=bestCol, colValue=bestSplitValue, trueBranch=yesNode, falseBranch=noNode)
        else:
            # no gain was made on entropy
            # so use the current rows outcomes as
            results = {}
            for r in rows:
                results.setdefault(r[len(r)-1], 0)
                results[r[len(r)-1]] += 1
            
            return decisionTree(s1, outcomes=results)
    
    
    def printtree2(self, tree,indent=''):
        # Is this a leaf node?
        if tree.outcomes!=None:
            print str(tree.outcomes)
        else:
            # Print the criteria
            print str(tree.colNo)+':'+str(tree.colValue)+'? '
            # Print the branches
            print indent+'T->',
            self.printtree2(tree.trueBranch,indent+'   ')
            print indent+'F->',
            self.printtree2(tree.falseBranch,indent+'   ')

    def classify(self, row, root):
        
        if root.outcomes != None:
            return root.outcomes
        
        value = row[root.colNo]
        
        trueBranch = False
        if isinstance(value, int) or isinstance(value, float):
            if value >= root.colValue:
                trueBranch = True
        else:
            if value == root.colValue:
                trueBranch = True
        
        if trueBranch:
            return self.classify(row, root.trueBranch)
        
        return self.classify(row, root.falseBranch)
            
    def pruneTree(self, root, minGain):
        if root.trueBranch.outcomes == None:
            self.pruneTree(root.trueBranch, minGain)
        if root.falseBranch.outcomes == None:
            self.pruneTree(root.falseBranch, minGain)
        
        if root.trueBranch.outcomes != None and root.falseBranch.outcomes != None:
            falseOutcomes,trueOutcomes = [],[]
            combinedOutcomes = []
            
            for k,v in root.trueBranch.outcomes.items():
                for i in range(v):
                    trueOutcomes.append([k])
                    combinedOutcomes.append([k])
                
            for k,v in root.falseBranch.outcomes.items():
                for i in range(v):
                    falseOutcomes.append([k])
                    combinedOutcomes.append([k])
            

            delta = self.entropy(combinedOutcomes, 0) - (self.entropy(trueOutcomes, 0) + self.entropy(falseOutcomes, 0))/2
            
            if delta < minGain:                
                root.falseBranch = None
                root.trueBranch = None
                
                results = {}
                for r in combinedOutcomes:
                    results.setdefault(r[0], 0)
                    results[r[0]] += 1
                
                root.outcomes = results 
            



class TreeDrawer:
    
    def getTreeWidth(self,root):
        if root.trueBranch == None and root.falseBranch == None:
            return 1
        
        return self.getTreeWidth(root.trueBranch) + self.getTreeWidth(root.falseBranch)
    
    def getTreeHeight(self, root):
        if root.trueBranch == None and root.falseBranch == None:
            return 0
        return max(self.getTreeWidth(root.trueBranch), self.getTreeWidth(root.falseBranch)) + 1
    
    def drawTree(self,root, featureNames, fileName='decisionTree.jpg'):
        from PIL import Image,ImageDraw
        
        w = self.getTreeWidth(root)*100 + 220
        h = self.getTreeHeight(root)*100 + 220
        
        img = Image.new('RGB', (w,h), (255,255,255))
        draw = ImageDraw.Draw(img)
        
        self.drawNode(draw, root, w/2, 20, featureNames)
        img.save(fileName, 'JPEG')
        
        
    def drawNode(self, draw, root, x, y, featureNames):
        if root.outcomes == None:
            w1 = self.getTreeWidth(root.trueBranch)*100
            w2 = self.getTreeWidth(root.falseBranch)*100 
            
            left = x - (w1+w2)/2
            right = x + (w1+w2)/2
            
            draw.text((x-20,y-10), str(featureNames[root.colNo])+':'+str(root.colValue),(0,0,0))
            
            draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
            draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))
            
            #Draw the branch nodes
            self.drawNode(draw,root.falseBranch,left+w1/2,y+100, featureNames)
            self.drawNode(draw,root.trueBranch,right-w2/2,y+100, featureNames)
 
        else:
            outcomesText = ''
            for k,v in root.outcomes.items():
                outcomesText += str(k) + ':' + str(v) + ' \n'
                
            draw.text((x,y), outcomesText, (0,0,0))
        
    
def main():
    myData=[line.strip().split('\t') for line in file('decision_tree_example.txt')]
    dt = decisionTree(myData)
    
    print myData
    
    (s1,s2) = dt.divideRows(myData, 1, 'USA')
    
    visitedColumns = []
    root = dt.constructTree(myData, visitedColumns)            
    dt.printtree2(root, '')
    
    
    t = TreeDrawer()
    featureNames = ['Referrer', 'Country', 'HasReadFAQ', 'PagesViewed', 'Outcome']
    t.drawTree(root, featureNames, fileName='original.jpg')
    
    unseenItem = ['(direct)','Canada','yes',5]
    print dt.classify(unseenItem, root)
    
    dt.pruneTree(root, 0.5)
    dt.printtree2(root, '')
    t.drawTree(root, featureNames, fileName='pruned.jpg')
    
if __name__ == '__main__':
    main()
        