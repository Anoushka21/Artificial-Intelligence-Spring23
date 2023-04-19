'''
Minmax and Alpha-Beta pruning game tree solver
By- Anoushka Gupta ag8733@nyu.edu 
'''


import numpy as np
import pandas as pd
import re
import math 
import sys
from collections import defaultdict

graph=dict()                #Dictionary of nodes where each key is the node label and key value is a Node object
incomingEdgeCount=dict()    #For each node, store the number of incoming edges  

class Node:
    def __init__(self, value,isLeaf,nodeChosen,child):
        self.value = value                          
        self.isLeaf = isLeaf                        # 1 if node is leaf else 0
        self.nodeChosen= nodeChosen                 # stores the child node chosen
        self.child=child                            # list[] of children of a node
        self.parent=[]                              # list[] of parents of a node
        
    def setValue(self,v):
        self.value=v                    
    def setNode(self,name):
        self.nodeChosen=''.join(name)   
    def setChild(self,c):
        self.child=c
    def setParent(self,p):
        self.parent.append(p)

def minmax(nodename,isMax,max_value_cutoff,v=0,abd={}):             # v and abd are optional arguments
    
    if bool(abd)!=False:                                        # alpha-beta pruning enabled
        prev_alpha=abd['alpha']
        prev_beta=abd['beta']
        ab=1
    else:
        ab=0
    flag=0

    if (graph[nodename]).isLeaf :                       # If leaf node return the value of leaf
        return (graph[nodename]).value
    if isMax=="max":                                    # MAX PLAYER
        (graph[nodename]).setValue(-math.inf)
        for child in (graph[nodename]).child:
            val=minmax(child,"min",max_value_cutoff,v,abd)
            if val>=max_value_cutoff:                      # Max value cutoff- if value is >= n then we 'prune' and don't check other children
                (graph[nodename]).value=val
                (graph[nodename]).setNode(child)
                if v==1:                                    
                    print(f"max({nodename}) chooses {child} for {val}")                 # verbose mode enabled
                return val   
            if (graph[nodename]).value < val:
                (graph[nodename]).value=val
                (graph[nodename]).setNode(child)
            if ab==1:
                abd['alpha']=max(abd['alpha'],(graph[nodename]).value)
                abd['beta']=prev_beta
                if abd['beta']<=abd['alpha']:
                    flag=1
                    break  
        if v==1 and flag!=1:
            print(f"max({nodename}) chooses {(graph[nodename]).nodeChosen} for {(graph[nodename]).value}")
        return (graph[nodename]).value
    else:                                                         # MIN PLAYER
        (graph[nodename]).setValue(math.inf)
        for child in (graph[nodename]).child:
            val=minmax(child,"max",max_value_cutoff,v,abd)            # Max value cutoff- if value is <= -n then we 'prune' and don't check other children
            if val<=-(max_value_cutoff):
                (graph[nodename]).value=val
                (graph[nodename]).setNode(child)
                if v==1:
                    print(f"min({nodename}) chooses {child} for {val}")             # verbose mode enabled
                return val 
            if (graph[nodename]).value > val:
                (graph[nodename]).value=val
                (graph[nodename]).setNode(child)
            if ab==1:
                abd['beta']=min(abd['beta'],(graph[nodename]).value)
                abd['alpha']=prev_alpha
                if abd['beta']<=abd['alpha']:
                    flag=1
                    break 
        if v==1 and flag!=1:
            print(f"min({nodename}) chooses {(graph[nodename]).nodeChosen} for {(graph[nodename]).value}")         # verbode mode enabled
        return (graph[nodename]).value

def checkMultipleRoot():                # Check for multiple roots by checking if more than 1 node has 0 incoming edges
    dd = defaultdict(set)
    for k, v in incomingEdgeCount.items():
        dd[v].add(k)
    dd = { k: v for k, v in dd.items() if len(v) > 1 }
    if 0 not in dd.keys():
        return
    if len(dd[0])>1:
        s="\" and \""
        print(f"Error: multiple roots \"{s.join([k for k in dd[0]])}\"")
        exit(1)

def FindRoot():                         # Finding the root node --> node with no incoming edge
    for k in incomingEdgeCount.keys():
        if incomingEdgeCount[k]==0:
            return k
    return "$"  # No root found

def checkCycle():                       # Check for cycles--> all nodes have an incoming edge
    cfl=0
    for k in incomingEdgeCount.keys():
        if incomingEdgeCount[k]==0:
            cfl=1
    if cfl==0:
        print(f"ERROR: Cycle detected. Exiting....")
        exit(1)

def checkNodeError():                   # Check for leaf and inernal node error
    for k in graph.keys():
        if len(graph[k].child)==0 and graph[k].isLeaf!=1:
            s="\",\""
            print(f"ERROR:Child Node \"{k}\" of \"{s.join([k for k in graph[k].parent])}\" not found")
            exit(1)

def addParent():                        #add parent to check for node errors
    for k in graph.keys():          
        for child in graph[k].child:
            (graph[child]).setParent(k)
            
def Insert_Incoming_EdgeCount(key,p=0):
    if p==1:
        if key not in incomingEdgeCount.keys():
            incomingEdgeCount[key]=0
    else:
        if key in incomingEdgeCount.keys():
            incomingEdgeCount[key]+=1
        else:
            incomingEdgeCount[key]=1

def ReadInput(path):
    with open(path,'r') as f:
        lines=f.readlines()
        for line in lines:
            if not line.strip():
                    continue
            line=(line.strip())
            line_split=re.split(':|=',line)
            token=[]
            for w in line_split:
                w=w.strip()
                token.append(w)
            if len(token)!=2:
                print("ERROR: Children nodes or leaf node value expected")
                exit(1)
            else:
                ValueOrChild=token[1]
                if ValueOrChild[0]=='[':                                #its a node definition
                    ValueOrChild=ValueOrChild.lstrip('[')
                    ValueOrChild=ValueOrChild.rstrip(']')
                    ValueOrChild=re.split(',| ',ValueOrChild)               # get nodes
                    parent=(token[0])                                       # first node is the parent node
                    if parent.isalnum()==0 :
                        print(f"ERROR:Node name \"{parent}\" not alphanumeric")                     # Syntax Error
                        exit(1)
                    Insert_Incoming_EdgeCount(parent,1)
                    child_list=[]
                    for child in ValueOrChild:
                        if child=='':
                            continue
                        if child.isalnum()==0:
                            print(f"ERROR:Node name \"{child}\" not alphanumeric")                # Syntax Error
                            exit(1)
                        else:
                            if child not in graph.keys():                                         # Child node has not yet been defined as leaf
                                graph[child]=Node(0,0,"",[])
                            child_list.append(child)
                            Insert_Incoming_EdgeCount(child) 
                    if parent not in graph.keys():
                        n1=Node(0,0,"",[])
                        n1.setChild(child_list)
                        graph[parent]=n1
                    else:
                        if graph[parent].isLeaf==1:                                             # Node redefine error
                            print(f"ERROR:\"{parent}\" earlier defined as leaf and now being defined as internal node")
                            exit(1)
                        graph[parent].setChild(child_list)
                        graph[parent].setValue(0)
                else:                                                                           # Leaf definition of type x=5
                    if (token[0]).isalnum()==0:
                        print(f"ERROR:Node name \"{token[0]}\" not alphanumeric")               # SYNTAX error
                        exit(1)
                    if token[0] in graph.keys() and graph[token[0]].child!=[]:                  # Node redefine error
                        print(f"ERROR: Node \"{token[0]}\" earlier defined as internal node and now redefined as a leaf node")
                        exit(1)                                       
                    graph[token[0]]=Node(int(token[1]),1,token[0],[])
                    if token[0] not in incomingEdgeCount.keys():
                        incomingEdgeCount[token[0]]=0
    f.close()

            

def printGraph():                             # helper function to visualize graph  
    for (k,v) in graph.items():
        print(f"Node:{k} Parent:{v.parent} Value:{v.value} isLeaf:{v.isLeaf} NodeChosen:{v.nodeChosen} Children:{v.child}")
    print("\n\n")

def main():
    '''
    3 options
    sys.argv length <4  or >6  ------> Exit with eror
    sys.argv length =4 ------> n max/min input.txt
    sys.argv length =5 ------> [-v] or [-ab] n max/min input.txt
    sys.argv length =6 ------> -v -ab n max/min input.txt
    '''

    if len(sys.argv)<4 or len(sys.argv)>6:
        print("ERROR: Pass 3,4 or 5 arguments of the form [-v] [-ab] n max/min input.txt where -v and -ab are optional")
        exit(1)
    elif len(sys.argv)==4:
        max_value_cutoff=int(sys.argv[1])
        isMax=sys.argv[2]
        path=sys.argv[3]
        v=0
        ab=0
    elif len(sys.argv)==5:
        max_value_cutoff=int(sys.argv[2])
        isMax=sys.argv[3]
        path=sys.argv[4]
        if sys.argv[1]=="-v":       #use verbose mode
            v=1
            ab=0
        else:                       #use alpha beta pruning
            v=0
            ab=1
    else:
        max_value_cutoff=int(sys.argv[3])
        isMax=sys.argv[4]
        path=sys.argv[5]
        v=1
        ab=1
    ReadInput(path)
    addParent()
    checkCycle()
    checkMultipleRoot()
    checkNodeError()
    root=FindRoot()
    if root=="$":                                   # Exit if no root found
        print("Error: Root couldn't be found")
        exit(1)
    if ab==0:                                       # no alpha-beta pruning
        val=minmax(root,isMax,max_value_cutoff,v)
        if v==0:
            print(f"{isMax}({root}) chooses {(graph[root]).nodeChosen} for {val}")
    else:                                           # alpha-beta pruning enabled
        abd={'alpha':-math.inf,'beta':math.inf}
        val=minmax(root,isMax,max_value_cutoff,v,abd)
        if v==0:
            print(f"{isMax}({root}) chooses {(graph[root]).nodeChosen} for {val}")
        
if __name__ == "__main__":
    main()