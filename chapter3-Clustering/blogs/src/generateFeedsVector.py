import sys
from math import sqrt
from PIL import Image,ImageDraw

import random


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

class bnode:
    def __init__(self, vec, title=None, left=None, right=None, distance=0.0, id='0'):
        self.left = left
        self.vec = vec
        self.right = right
        self.distance = distance
        self.id = id
        self.title = title


def getBRows(fileName):

    f = open(fileName, 'r')
    header = f.next()
    lexicon = header.strip().split("\t")[1:]

    bNodes=[]

    for line in f:
        p = line.strip().split("\t")
        vect = [float(n) for n in p[1:]]

        newCt = bnode(vect, p[0])
        bNodes.append(newCt)
    f.close()

    return (bNodes, lexicon)




def hClustering(clusts, lexicon, distance=pearson):

    clustsId = -1
    clusterPairScore = {}

    for i in range(len(clusts)):
        clusts[i].id = i

    while(len(clusts) > 1):
        lowestD = distance(clusts[0].vec, clusts[1].vec)
        lowest = (0,1)

        for i in range(len(clusts)):
            for j in range(i+1, len(clusts)):
                
                if (clusts[i].id, clusts[j].id) not in clusterPairScore:
                    d = distance(clusts[i].vec, clusts[j].vec)
                    clusterPairScore[(clusts[i].id, clusts[j].id)] = d

                d = clusterPairScore[(clusts[i].id, clusts[j].id)]

                if d < lowestD:
                    lowestD = d
                    lowest = (i,j)


        # get average of i and j
        averageVect = [(clusts[lowest[0]].vec[m] + clusts[lowest[1]].vec[m])/2 for m in range(len(clusts[i].vec))]
        newClust = bnode(averageVect, left = clusts[lowest[0]], right = clusts[lowest[1]], distance=d, id=clustsId)

        #print 'poping out ', lowest[0], ' ', lowest[1], ' length ', len(clusts)

        # remove both entries
        del clusts[lowest[1]]
        del clusts[lowest[0]]    

        clusts.append(newClust)

        clustsId -= 1

    return clusts[0]


def printNodes(root, n=0):
    for i in range(n): print ' ',

    if root.id < 0:
        print '-'

    if root.title != None: print root.title

    if root.left != None: printNodes(root.left, n+1)
    if root.right != None: printNodes(root.right, n+1)





def getheight(clust):
    if clust.left==None and clust.right==None: return 1
    return getheight(clust.left)+getheight(clust.right)

def getdepth(clust):
    # The distance of an endpoint is 0.0
    if clust.left==None and clust.right==None: return 0
    return max(getdepth(clust.left),getdepth(clust.right))+clust.distance


def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
    # height and width
    h=getheight(clust)*20
    w=1200
    depth=getdepth(clust)
    # width is fixed, so scale distances accordingly
    scaling=float(w-200)/depth
    # Create a new image with a white background
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    draw.line((0,h/2,10,h/2),fill=(255,0,0))
    # Draw the first node
    drawnode(draw,clust,10,(h/2),scaling,labels)
    img.save(jpeg,'JPEG')



def drawnode(draw,clust,x,y,scaling,labels):
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
        drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
        drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x+5,y-7),clust.title,(0,0,0))





def kMeansClustering(clusts, distance=pearson, k=4):

    # create copies of randomly selected nodes to be the centroids
    # TODO: there is a potential here that random can select the same
    # node more than once as a centroid ... alas ... something to think
    # about
    centroids = []
    for i in range(k):
        randPos = random.randrange(0, len(clusts))
        centroids.append(bnode(clusts[randPos].vec[:], clusts[randPos].title))

    
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

    
    
# 



def main():
    (rows, lex) = getBRows('blogVect.txt')
    #r = hClustering(rows, lex)
    #blognames = []
    #drawdendrogram(r,blognames,jpeg='blogclust.jpg')
    #printNodes(r, 0)


    for c in range(len(rows)):
        print '\t',c,'\t',rows[c].title
    
    groups = kMeansClustering(rows)
    
    print groups 
    
    for i,k in groups.items():
        print 'Group ', str(i+1)
        
        for j in k:
            print '\t',j,'\t', rows[j].title

if __name__ == '__main__':
    main()


