#===============================================================================
# Class Tree to initialize and save whole parsed tree
#===============================================================================
import sys

class TreeObject(object):
    nodelist = []    
    nodechild = dict()
    nodeval = dict()
    root = None
        
    def __init__(self, nodelistraw):
        self.__parseNodes(nodelistraw[0], nodelistraw[1:])
        self.root = nodelistraw[0]
    
    def appendChild(self, rnode, cnode):
        if(self.nodechild.has_key(rnode)):
            self.nodechild[rnode].append(cnode)
        else:
            self.nodechild[rnode] = [cnode]

    def addNodeVal(self, node, val):
        self.nodeval[node] = float(val)

    def getNodeVal(self, node):
        if(node in self.nodeval.keys()):
            return self.nodeval[node]
        else:
            return float("inf")

    def getChildNodes(self, node):
        
        if(node in self.nodechild.keys()):
            return self.nodechild[node]
        else:
            return []
        
    def addNode(self, node):
        if node not in self.nodelist:
            self.nodelist.append(node)
                
    def __parseNodes(self, root, nodelistraw):
        self.addNode(root)       
        if(nodelistraw is not None and len(nodelistraw) > 0):
            for j in nodelistraw:
                if(type(j) is tuple):
                    child = j[0]
                    self.addNode(child)
                    self.appendChild(root, child)
                    self.addNodeVal(child, j[1])
                else:                       
                    child = j[0]
                    self.addNode(child)
                    self.appendChild(root, child)
                    node = self.__parseNodes(child, j[1:])   
    def isTerminal(self,node):
        if(node not in self.nodechild.keys()):
            return True
        else:
            return False              
            
class Play(object):
    
    def __init__(self,playtree):
        self.playtree = playtree
        self.isTerminal = playtree.isTerminal
        self.Utility = playtree.getNodeVal
        self.getSuccessor = playtree.getChildNodes
        

    def minmax_decision(self): 
        value = self.max_value(self.playtree.root)        
        return value
    def minmax_ab_decision(self): 
        value = self.max_valueab(self.playtree.root,float("-inf"),float("+inf"))        
        return value
    
    def max_value(self, state):
        print state
        if(self.isTerminal(state) == True):
            return self.Utility(state)
        
        value = float("-inf")
        for child in self.getSuccessor(state):
            value = max(value, self.min_value(child))
        return value
    
    def min_value(self, state):
        print state
        if(self.isTerminal(state) == True):
            return self.Utility(state)
        value = float("inf")
        for child in self.getSuccessor(state):
            value = min(value, self.max_value(child))
        return value
    
    def max_valueab(self, state,alpha,beta):
        print state
        
        if(self.isTerminal(state) == True):
            return self.Utility(state)
        
        value = float("-inf")
        for child in self.getSuccessor(state):
            value = max(value, self.min_valueab(child,alpha,beta))
            if value >= beta:
                return value
            alpha=max(alpha,value)
#             print "max function " + state
#             print alpha
#             print beta
        return value
    
    def min_valueab(self, state,alpha,beta):
        print state
        if(self.isTerminal(state) == True):
            return self.Utility(state)
        value = float("inf")
        for child in self.getSuccessor(state):
            value = min(value, self.max_valueab(child,alpha,beta))
            if value <= alpha:
                return value
            beta=min(beta,value)
#             print "min function " + state
#             print alpha
#             print beta
        return value
    
if __name__ == '__main__':
    
    inputfile = sys.argv[1]
    #inputfile = "test_tree1"
    nodelistraw = []

    with open(inputfile, "r") as f:
        nodelistraw = eval(f.read())
 
    iTreeObject = TreeObject(nodelistraw)
    game = Play(iTreeObject)

    print game.minmax_decision()
    print game.minmax_ab_decision()
    