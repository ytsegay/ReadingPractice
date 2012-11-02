from math import sqrt,fabs
import random
from PIL import Image,ImageDraw


class bnode:
    def __init__(self, vec, title=None, left=None, right=None, distance=0.0, nId='0'):
        self.left = left
        self.vec = vec
        self.right = right
        self.distance = distance
        self.id = nId
        self.title = title


def pearson(v1,v2):
    sum1=sum(v1)
    sum2=sum(v2)

    sum1Sq=sum([pow(v,2) for v in v1])
    sum2Sq=sum([pow(v,2) for v in v2])

    pSum=sum([v1[i]*v2[i] for i in range(len(v1))])
    
    num=pSum-(sum1*sum2/len(v1))
    den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den==0: return 0
    return 1.0-num/den

# 
def tanamato(v1,v2):
    shr,c1,c2=0,0,0
        
    for i in range(len(v1)):
        if v1[i] != 0: c1 += 1
        if v2[i] != 0: c2 += 1
        if v1[i] != 0 and v2[i] != 0: shr += 1
        
        
    denom = (c1+c2-shr)
    return 1.0 - (shr/denom)


def manhattan(v1, v2):
    manhatSum = 0.0
    for i in range(len(v1)):
        manhatSum +=  fabs(v1[i]-v2[i])
    
    return manhatSum



def kMeansClustering(clusts, distance=pearson, k=4):
    centroids = []
    for i in range(k):
        randPos = random.randrange(0, len(clusts))
        
        centroids.append(bnode(clusts[randPos].vec[:], clusts[randPos].title))
        print randPos

    
    prevBestMatches = {}
    
    # repeat the process 100 times
    for f in range(100):
        bestMatches = {}
                
        print 'Iteration #',f
        
        # for each node find the cluster that is closest match to it
        for i in range(len(clusts)):
            maxMatch = distance(clusts[i].vec, centroids[0].vec)
            bestMatch = 0
            
            for j in range(1, k):
                d =  distance(clusts[i].vec, centroids[j].vec)
                centroids[j].vec
                                
                # found a better match?
                if d < maxMatch:
                    maxMatch = d
                    bestMatch = j
                
            # add the current node to the best matching cluster's
            # list of candidates
            bestMatches.setdefault(bestMatch, [])
            bestMatches[bestMatch].append(i)
        
        # if the grouping of the nodes is done ... we have not seen
        # a change in how the nodes are aligned then we are done
        if bestMatches == prevBestMatches:
            break;
        
        prevBestMatches = bestMatches
        
        # now each centroid needs to be adjusted so that it is at the center
        # of that group. This is done by averaging the values of the feat vectors
        # that a node contains        
        for i in range(k):
            # make space for the center/average centroid vec
            newVec = [0.0]*len(clusts[0].vec)
            
            bMatchPositions = bestMatches[i]
            
            for j in range(len(clusts[i].vec)):
                # for each column 
                colSum = 0.0
                # in every node add the jth column
                for s in bMatchPositions:
                    colSum += clusts[s].vec[j]
                newVec[j] = (colSum/len(bestMatches))
            
            centroids[i].vec = newVec[:]

    return bestMatches


# a special version of the kMeansClustering function to answer
# question 5 in the book
def kMeansClusteringWithWeights(clusts, distance=pearson, k=4):

    # create copies of randomly selected nodes to be the centroids
    # TODO: there is a potential here that random can select the same
    # node more than once as a centroid ... alas ... something to think
    # about
    centroids = []
    for i in range(k):
        randPos = random.randrange(0, len(clusts))
        
        centroids.append(bnode(clusts[randPos].vec[:], clusts[randPos].title))
        print randPos

    prevBestMatches = {}
    
    # repeat the process 100 times
    for f in range(100):
        bestMatches = {}
                
        print 'Iteration #',f
        
        # for each node find the cluster that is closest match to it
        for i in range(len(clusts)):
            maxMatch = distance(clusts[i].vec, centroids[0].vec)
            bestMatch = 0
            
            for j in range(1, k):
                d =  distance(clusts[i].vec, centroids[j].vec)
                centroids[j].vec
                                
                # found a better match?
                if d < maxMatch:
                    maxMatch = d
                    bestMatch = j
                
            # add the current node to the best matching cluster's
            # list of candidates
            bestMatches.setdefault(bestMatch, [])
            bestMatches[bestMatch].append((i,maxMatch))
        
        # if the grouping of the nodes is done ... we have not seen
        # a change in how the nodes are aligned then we are done
        if bestMatches == prevBestMatches:
            break;
        
        prevBestMatches = bestMatches
        
        # now each centroid needs to be adjusted so that it is at the center
        # of that group. This is done by averaging the values of the feat vectors
        # that a node contains        
        for i in range(k):
            # make space for the center/average centroid vec
            newVec = [0.0]*len(clusts[0].vec)
            
            bMatchPositions = bestMatches[i]
            
            for j in range(len(clusts[i].vec)):
                # for each column 
                colSum = 0.0
                # in every node add the jth column
                for s in bMatchPositions:
                    colSum += clusts[s[0]].vec[j]
                newVec[j] = (colSum/len(bestMatches))
            
            centroids[i].vec = newVec[:]

    return bestMatches


# hierarchical clustering 
# 1. the idea to find the nearest two nodes pair ... 
# 2. merge the pair into a new cluster node and the new node becomes the parent 
# 3. 
def hClustering(clusts, distance=pearson):

    # nodes for merged pairs will have a -ve index
    clustsId = -1
    # avoid recomputing previously computed distances
    clusterPairScore = {}

    for i in range(len(clusts)):
        clusts[i].id = i

    # while there are nodes not yet clustered
    while(len(clusts) > 1):
        
        lowestD = distance(clusts[0].vec, clusts[1].vec)
        lowest = (0,1)

        # find the pair with the lowest distance
        for i in range(len(clusts)):
            for j in range(i+1, len(clusts)):
               
                # cache pair distances 
                if (clusts[i].id, clusts[j].id) not in clusterPairScore:
                    d = distance(clusts[i].vec, clusts[j].vec)
                    clusterPairScore[(clusts[i].id, clusts[j].id)] = d

                d = clusterPairScore[(clusts[i].id, clusts[j].id)]

                if d < lowestD:
                    lowestD = d
                    lowest = (i,j)

        # get average of i and j
        averageVect = [(clusts[lowest[0]].vec[m] + clusts[lowest[1]].vec[m])/2 for m in range(len(clusts[i].vec))]
        newClust = bnode(averageVect, left = clusts[lowest[0]], right = clusts[lowest[1]], distance=d, nId=clustsId)

        # remove both entries
        del clusts[lowest[1]]
        del clusts[lowest[0]]    

        clusts.append(newClust)

        clustsId -= 1

    return clusts[0]



# prints the hierarchical tree structure 
# not that useful as the tree gets bigger
def printHClusterTree(root, n=0):
    for i in range(n): print ' ',

    if root.id < 0:
        print '-'

    if root.title != None: print root.title

    if root.left != None: printHClusterTree(root.left, n+1)
    if root.right != None: printHClusterTree(root.right, n+1)





def readFeatVect(fileName):

    f = open(fileName, 'r')
    header = f.next()
    
    # feature names/ids
    featureNames = header.strip().split("\t")[1:]

    # nodes
    bNodes=[]
    for line in f:
        p = line.strip().split("\t")
        
        vect = [float(n) for n in p[1:]]
        
        if len(vect) <= 0: continue
        assert len(vect) == len(featureNames)
        
        newCt = bnode(vect, p[0])
        bNodes.append(newCt)
    f.close()

    return (bNodes, featureNames)



def hCluster(fileName, outputFileName='blogclust.jpg', distance=pearson):
    rows = readFeatVect(fileName)[0]
    root = hClustering(rows, distance)

    #printHClusterTree(root, 0)

    # TODO: clean the graphical drawing of this     
    drawdendrogram(root,jpeg=outputFileName)


# a special version of the kCluster function to answer
# question 5 in the book
def kClusterWithWeight(fileName, distance=pearson):
    rows = readFeatVect(fileName)[0]
    
    # print the original list of candidate entries to be clustered
    for i in range(len(rows)):
        print '\t',i,'\t',rows[i].title
    
    clustersCount = 4
    groups = kMeansClusteringWithWeights(rows, distance, k=clustersCount)
    
    print groups
    
    print '\n\nKMeans clustering with k=',clustersCount 
    for i,k in groups.items():
        print 'Group ', str(i+1)
        
        for j in k:
            print '\t',j[0],'\t', rows[j[0]].title,'\t',j[1]




def kCluster(fileName, distance=pearson):
    rows = readFeatVect(fileName)[0]
    
    # print the original list of candidate entries to be clustered
    for i in range(len(rows)):
        print '\t',i,'\t',rows[i].title
    
    clustersCount = 4
    groups = kMeansClustering(rows, distance, k=clustersCount)
    
    print '\n\nKMeans clustering with k=',clustersCount 
    for i,k in groups.items():
        print 'Group ', str(i+1)
        
        for j in k:
            print '\t',j,'\t', rows[j].title







def getheight(clust):
    if clust.left==None and clust.right==None: return 1
    return getheight(clust.left)+getheight(clust.right)

def getdepth(clust):
    # The distance of an endpoint is 0.0
    if clust.left==None and clust.right==None: return 0
    return max(getdepth(clust.left),getdepth(clust.right))+clust.distance


def drawdendrogram(clust,jpeg='clusters.jpg'):
    # height and width
    h=getheight(clust)*20
    w=1200
    depth=getdepth(clust)
    # width is fixed, so scale distances accordingly
    scaling=float(w-150)/depth
    # Create a new image with a white background
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    draw.line((0,h/2,10,h/2),fill=(255,0,0))
    # Draw the first node
    drawnode(draw,clust,10,(h/2),scaling)
    img.save(jpeg,'JPEG')


def drawnode(draw,clust,x,y,scaling):
    if clust.id<0:
        h1=getheight(clust.left)*20
        h2=getheight(clust.right)*20
        top=y-(h1+h2)/2
        bottom=y+(h1+h2)/2
        # Line length
        ll=clust.distance*scaling
        # Vertical line from this cluster to children
        draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))
        # Horizontal line to left item
        draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))
        # Horizontal line to right item
        draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))
       
        # Call the function to draw the left and right nodes
        drawnode(draw,clust.left,x+ll,top+h1/2,scaling)
        drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x+5,y-7),clust.title,(0,0,0))




    
    




def main():

    #hCluster('blogVect.txt', distance=tanamato, outputFileName='tanamatoBlogs.jpg')
    #hCluster('blogVect.txt', outputFileName='pearsonBlogs.jpg')
    #hCluster('blogVect.txt', distance=manhattan, outputFileName='manhattanBlogs.jpg')
    
    
    #hCluster('zebo.txt', distance=tanamato, outputFileName='tanamatoZabo.jpg')
    #hCluster('zebo.txt', outputFileName='pearsonZabo.jpg')
    kClusterWithWeight('zebo.txt')
    

if __name__ == '__main__':
    main()


