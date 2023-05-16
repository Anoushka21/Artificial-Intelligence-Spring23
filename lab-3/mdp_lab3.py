import argparse
import copy

node_dict={}
discount=1
tolerance=0.001
iteration=100
min=False
class Node:
    def __init__(self,name:str,reward:float,edge,prob,policy,value:float):
        self.name=name
        self.reward=reward
        self.edge=edge
        self.prob=prob
        self.policy=policy
        self.value=value
    def print_node(self):
        print(f"Node:{self.name} Reward:{self.reward} Edge:{self.edge} Probabiliy:{self.prob} Policy:{self.policy} Value:{self.value}")

def read_input(path):
    nodes=set()
    reward_dict={}
    edge_dict={}
    probability_dic={}
    try:
        with open(path,'r') as f:
            lines=f.readlines()
            for line in lines:
                if line.startswith('#'):
                    continue
                if  not line.strip():
                    continue
                line=line.strip()
                if line.find('=')!=-1:
                    reward_line= line.split('=')
                    if len(reward_line)>2:
                        print("Reward invalid")
                        exit(-1)
                    node_name=reward_line[0].strip()
                    if  not node_name.isalnum():
                        print("Node name should be alpha-numeric")
                        exit(-1)
                    nodes.add(node_name)
                    reward_value=reward_line[1]
                    neg_flag=0
                    if reward_value[0]=='-':
                        neg_flag=1
                    if neg_flag:
                        reward_value=reward_value[1:]
                        if reward_value.isnumeric()==False:
                            print("Reward invalid")
                            exit(-1)
                    else:
                        if reward_value.isnumeric()==False:
                            print("Reward invalid")
                            exit(-1)
                    if neg_flag:
                        reward_dict[node_name]=-float(reward_value)
                    else:
                        reward_dict[node_name]=float(reward_value)
                elif line.find(':')!=-1:
                    edge_line= line.split(':')
                    if len(edge_line)>2:
                        print("Edges invalid")
                        exit(-1)
                    node_name=edge_line[0].strip()
                    if  not node_name.isalnum():
                        print("Node name should be alpha-numeric")
                        exit(-1)
                    nodes.add(node_name)
                    edges=edge_line[1].strip()
                    if len(edges)==0:
                        edge_dict[node_name]=[]
                        continue
                    if edges[0]!='[' and edges[-1]!=']':
                        print("Edges invalid")
                        exit(-1)
                    edges=edges[1:len(edges)-1]
                    edge_list=edges.split(',')
                    list=[]
                    for e in edge_list:
                        list.append(e.strip())
                    edge_dict[node_name]=list
                elif line.find('%')!=-1:
                    prob_line=line.split('%')
                    if len(prob_line)>2:
                        print("Probability invalid")
                        exit(-1)
                    node_name=prob_line[0].strip()
                    if  not node_name.isalnum():
                        print("Node name should be alpha-numeric")
                        exit(-1)
                    nodes.add(node_name)
                    probabilities=prob_line[1].strip()
                    probabilities=probabilities.split(' ')
                    if len(probabilities)==0:
                        print("Invalid probability")
                        exit(-1)
                    list=[]
                    for p in probabilities:
                        if p=='' or p==' ':
                            continue
                        if float(p)>1.0:
                            print("Invalid probability. Probability has to be between 0 an 1")
                            exit(-1)
                        list.append(float(p))
                    probability_dic[node_name]=list
                else:
                    print("Error")
                    exit(-1)                           
    except FileNotFoundError:
        exit(1)
    for node in nodes:
        reward=reward_dict[node] if node in reward_dict.keys() else 0.0
        prob_dict=None
        policy=None
        edges=None
        if node not in edge_dict.keys() or len(edge_dict[node])==0:
            if node in probability_dic.keys():
                print(f"Error.Exiting!")
                exit(-1)
        else:
            edges=edge_dict[node]
            if node not in probability_dic.keys():
                if len(edges) == 1:
                    prob_dict = {edges[0]: 1.0}
                else:
                    policy = [edges[0], 1.0]
            else:
                prob=probability_dic[node]
                if len(prob) == 1:
                    policy = [edges[0], prob[0]]
                else:
                    if len(prob) != len(edges):
                        print(f"Error at {node}")
                        exit(-1)
                    prob_dict = dict(zip(edges, prob))
        node_dict[node]=Node(node,reward,edges,prob_dict,policy,reward)


def calculate_new_values(t:Node):
    sum=0.0
    if t.edge is None:
        return t.reward
    if t.policy is None:
        for e in t.edge:
            sum+=node_dict[e].value * t.prob[e]
    else:
        policy_edge= t.policy[0]
        policy_prob=t.policy[1]
        for e in t.edge:
            if e==policy_edge:
                sum+=policy_prob*node_dict[e].value
            else:
                sum+= ((1-policy_prob)/(len(t.edge)-1))*node_dict[e].value
    new_val=t.reward+ (discount*sum)
    return new_val

def value_iteration():
    for i in range(0,iteration):
        mdif=0.0
        for node in node_dict.keys():
            cnode=copy.deepcopy(node_dict[node])
            new_value=calculate_new_values(cnode)
            cnode.value=new_value
            dif = abs(node_dict[node].value -cnode.value)
            node_dict[node]=cnode
            if dif>mdif:
                mdif=dif
        if mdif<=tolerance:
            break

def update_policy(t:Node):
    first_edge=node_dict[t].edge[0]
    first_edge_value=node_dict[first_edge].value
    for e in node_dict[t].edge:
        if e==first_edge:
            continue
        val=node_dict[e].value
        if min:
            if val<first_edge_value:
                first_edge=e
                first_edge_value=val
        if not min:
            if val>first_edge_value:
                first_edge=e
                first_edge_value=val
    if first_edge!=node_dict[t].policy[0]:
        node_dict[t].policy=[first_edge,node_dict[t].policy[1]]
    return node_dict[t].policy

def greedy_policy():
    pol=False
    for node in node_dict.keys():
        if not  node_dict[node].policy is None:
            old_pol=node_dict[node].policy
            new_pol = update_policy(node)
            if old_pol==new_pol :
                pol=False
            else:
                pol=True
    return pol

def print_policy():
    for node in sorted(node_dict.keys()):
        if not node_dict[node].policy is None:
            print(f"{node_dict[node].name} -> {node_dict[node].policy[0]}")
    print()

def print_values():
    for node in sorted(node_dict.keys()):
        print(f"{node_dict[node].name}={node_dict[node].value:0.3f} ",end='')
          
def main():
    global tolerance
    global min
    global discount
    global iteration
    parser = argparse.ArgumentParser()
    parser.add_argument('-tol',type=float)
    parser.add_argument('-iter',type=int)
    parser.add_argument('-df',type=float,required=False)
    parser.add_argument("input")
    parser.add_argument("-min",action='store_true')
    args = parser.parse_args()
    if args.tol is None:
        tolerance=0.001
    else:
        tolerance=args.tol
    if args.iter is None:
        iteration=100
    else:
        iteration=args.iter
    if args.df is None:
        discount=1
    else:
        discount=args.df
    if args.min:
        min=True
    else:
        min=False
    read_input(args.input)
    while 1:
        value_iteration()
        if not greedy_policy():
            break
    print_policy()
    print_values()   

if __name__=="__main__":
    main()