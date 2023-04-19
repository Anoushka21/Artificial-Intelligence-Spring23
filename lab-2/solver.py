import re
import sys
import copy

graph=dict()                            # Stores all vertex and its adjacent vertices
colour=list()                           # List of colors                           
cnf=[]                                  # List of clauses where each clause is list where list items are literals

def dictionary_sorter(d):               # Sorts dictionary based on the keys
    dkeys=list(d.keys())
    dkeys.sort()
    dsorted={i:d[i] for i in dkeys}
    return dsorted

def isValidVertex(s):                   # Vertex name should not contain "":" , "[" , "]" , ","
    for c in s:
        if c==':' or c=='[' or c==']' or c==',':
            return False
    return True

def ReadInput(path):                    #Parses Input and creates graph
    g={}
    try:
        with open(path,'r') as f:
            lines=f.readlines()
            for line in lines:
                if line.startswith('#'):
                    continue
                if not line.strip():
                    continue
                line=(line.strip())
                line_split=re.split(' : ',line)
                if len(line_split)<2:
                    print("ERROR")
                    exit(1)
                vertex=line_split[0]
                if not isValidVertex(vertex):
                    print("Invalid vertex name")
                    exit(1)
                edge_list=line_split[1]
                edge_list=edge_list.lstrip('[')
                edge_list=edge_list.rstrip(']')
                edge_list=re.split(',| ',edge_list)
                g[vertex]=edge_list
                for e in edge_list:
                    if not isValidVertex(e):
                        print("Invalid vertex name")
                        exit(1)
                    if e=='':
                        edge_list.remove(e)
                    if e not in g.keys():
                        g[e]=[]
        for k in g.keys():
            for e in g[k]:
                if k not in g[e]:                    # check if e-->k edge exists
                    g[e].append(k)
        for k in g.keys():
            g[k]=sorted(g[k])
        k=sorted(list(g.keys()))
        for ke in k:
            if ke=='':
                k.remove(ke)
        for i in k:
            graph[i]=g[i]
        f.close()
    except FileNotFoundError:
        print("File not found. Exiting!")
        exit(1)

def clause_one():                       # Generates clauses of 'At leasst one color'
    for vertex in graph.keys():
        clause=[]
        v_="".join([vertex,'_'])
        for c in colour:
            cp="".join([v_,c])
            clause.append(cp) 
        cnf.append(clause)

def clause_two():                       # Generates clauses of 'No adjacent vertices can have same color'
    for vertex in graph.keys():
        v_=""
        v_="".join(['!',vertex,'_'])
        for c in colour:
            vp="".join([v_,c])                  # !vertex_colour    eg: !NY_R              
            for adj in graph[vertex]:
                clause=[]
                adj_="".join(['!',adj,'_',c])     # !adj_colour     eg : !NJ_R
                clause.append(vp)
                clause.append(adj_)
                cnf.append(clause)

def clause_three():                     # Generates optional clauses of 'At most one color for each vertex'
    for vertex in graph.keys():
        v_="".join(['!',vertex,'_'])
        for i in range(0,len(colour)):
            f="".join([v_,colour[i]])
            for j in range(0,len(colour)):
                if i!=j:
                    clause=[]
                    s="".join([v_,colour[j]])
                    clause.append(f)
                    clause.append(s)
                    cnf.append(clause)

def PrintCNF():                         
    print("CNF:")
    for clause in cnf:
        print(" ".join(clause))
    print()

def CreateAtoms():                      # Returns a set of all atoms
    atoms=set()
    for clause in cnf:
        for c in clause:
            if not c.startswith('!'):
                atoms.add(c)
    return atoms

def check_empty_clause(S):              # Checks if empty clauses (i.e []) exist
    for c in S:
        if c==[]:
            return True
    return False

def single_literal_clause(S):           # Returns clauses which have a single literal or []
    for clause in S:
        if len(clause)==1:
            return clause
    return []

def pure_literal(S):                    # Returns list of pure literals
    literal={}
    for clause in S:
        for l in clause:
            if l in literal.keys():
                literal[l]+=1
            else:
                literal[l]=1
    ans=[]
    for k in literal.keys():
        if not k.startswith('!'):
            neg="".join(['!',k])
            if neg not in literal.keys():
                ans.append(k)
        else:
            pos=k[1:]
            if pos not in literal.keys():
                ans.append(k)

    return ans

def obviousAssign(L,V):                 # Assigns true or false for obvious cases
    if L.startswith("!"):
        a=L[1:]
        V[a]=False
    else:
        V[L]=True
    return V

def delete_clause_containing_literal(L,S):      # deletes all clauses from S which contain literal L
    for clause in list(S):
        if L in list(clause):
            S.remove(clause)
    return S

def propogate(l,S,V):                          
    for clause in list(S):
        neg="".join(['!',l])
        if (l in clause and V[l]==True) or (neg in clause and V[l]==False):
            S.remove(clause)
        elif (l in clause and V[l]==False):
            i=S.index(clause)
            S[i].remove(l)
        elif (neg in clause and V[l]==True):
            i=S.index(clause)
            S[i].remove(neg)
    return S


def DPLL(atoms,S,V,verbose=False):              # DPLL function which computes easy and hard cases
    easy=True
    while(easy):
        if not S:                                           # bASE CASE: SUCCESS
            if verbose:
                print("Successful\n")
            for a in atoms:
                if V[a]=='Unbound':
                    V[a]=False
            return V
        elif check_empty_clause(S):                         # BASE CASE: FAILURE
            if verbose:
                print("Empty clause found.Failure\n")
            return None
        L=pure_literal(S)                            # EASY CASE: Pure Literal
        SLC=single_literal_clause(S)
        if L:
            l=L[0]
            V=obviousAssign(l,copy.deepcopy(V))
            if verbose:
                if  not l.startswith('!'):
                    print(f"Easy case:Pure literal {l}={V[l]}")
                else:
                    print(f"Easy case:Pure literal {l[1:]}={V[l[1:]]}")
            S=delete_clause_containing_literal(l,copy.deepcopy(S))
        elif SLC:                                          # EASY CASE: Singleton
            l=SLC[0]
            V=obviousAssign(l,copy.deepcopy(V))
            if verbose:
                if  not l.startswith('!'):
                    print(f"Easy case:Unit literal {l}={V[l]}")
                else:
                    print(f"Easy case:Unit literal {l[1:]}={V[l[1:]]}")
            if l.startswith('!'):
                S=propogate(l[1:],copy.deepcopy(S),copy.deepcopy(V))
            else:
                S=propogate(l,copy.deepcopy(S),copy.deepcopy(V))
        else:                                                               # No easy case found
            easy=False
            break
    V=dictionary_sorter(V)
    for k in V.keys():                                                      
        if V[k]=='Unbound':
            V[k]=True                                                       # HARD CASE: guess true
            if verbose:
                print(f"Hard case:guess {k}=True")
            S1=copy.deepcopy(S)
            S1=propogate(k,copy.deepcopy(S1),copy.deepcopy(V))
            Vnew=DPLL(atoms,copy.deepcopy(S1),copy.deepcopy(V),verbose)
            if Vnew is not None:
                return Vnew
            V[k]=False                                                              # HARD CASE: guess false
            if verbose:
                print(f"Hard case contradiction:backrack guess {k}=False")
            S1=propogate(k,copy.deepcopy(S),copy.deepcopy(V))
            return DPLL(atoms,copy.deepcopy(S1),copy.deepcopy(V),verbose)

def DPLL_Solver(atoms,S,verbose=False):                                             
    V=dict()
    for a in atoms:
        V[a]='Unbound'
    return DPLL(atoms,copy.deepcopy(S),copy.deepcopy(V),verbose)

def PrintAssignments(assignments):                                          # Prints assignments for verbose mode
    if assignments is None:
        print(f"\nNO VALID ASSIGNMENTS\n")
        exit(1)
    print("Assignments are:")
    for v in assignments.keys():
        if not v.startswith('!'):
            print(f"{v}={assignments[v]}",end=' ')
    print("\n")

def PrintMapColour(assignments,ncolor):                                    # Converts assignements to map/vertex colors
    if assignments is None:
        print(f"\nGraph/Map can't be succesfully coloured using {ncolor} colours\nNO VALID ASSIGNMENTS\n")
        exit(1)
    colour_map={"B":"Blue","R":"Red","G":"Green","Y":"Yellow"}
    for a in sorted(assignments.keys()):
        if not a.startswith('!') and assignments[a]==True:
            c=colour_map[a[-1]]
            print(f"{a[:-2]} = {c}")

def main():
    if len(sys.argv)>4 or len(sys.argv)<3:
        print("Error")
        exit(1)
    if sys.argv[1]=="-v":
        verbose=True
    else:
        verbose=False
    if len(sys.argv)==3:
        if sys.argv[1]!="2" and sys.argv[1]!="3" and sys.argv[1]!="4":
            print("Ncolor not given.Should be 2,3,or 4.Exiting!")
            exit(1)
        ncolor=int(sys.argv[1])
        input=sys.argv[2]
    else:
        if sys.argv[2]!="2" and sys.argv[2]!="3" and sys.argv[2]!="4":
            print("Ncolor not given.Should be 2,3,or 4.Exiting!")
            exit(1)
        ncolor=int(sys.argv[2])
        input=sys.argv[3]
    if ncolor>4 or ncolor<2:
        print("Number of colors should be either 2,3,or 4")
        exit(1)
    colour.append('R')
    colour.append('G')
    if ncolor>=3:
        colour.append('B')
    if ncolor==4:
        colour.append('Y')
    
    ReadInput(input)
    clause_one()
    clause_two()
    clause_three()

    if verbose:
        PrintCNF()
    atoms=CreateAtoms()
    assignments=DPLL_Solver(atoms,cnf,verbose)
    if verbose:
        PrintAssignments(assignments)
    PrintMapColour(assignments,ncolor)
    
  
   
if __name__=="__main__":
    main()

