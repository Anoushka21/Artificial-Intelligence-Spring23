import argparse
import numpy as np
import pandas as pd
from collections import Counter
from fractions import Fraction
'''
python lab4.py -train file.txt -test.txt -K -C -v -d centroids
'''
train_file=None
test_file =None
K = None
algo=None
C=None
vflag=False
d=None

def e2_distance(a:np.array,b:np.array,kmeans=False):
    if kmeans:
            return np.sum((a-b)**2,axis=1)
    return np.dot((a-b).T,(a-b))

def manh_distance(a:np.array,b:np.array):
    return np.sum(np.abs(a-b),axis=1)   

class KNN():
    def __init__(self,K,train_file,test_file) :
        self.K=K
        self.train_data=[]
        self.test_data=[]
        self.train_file=train_file
        self.test_file=test_file
        self.distance_matrix=None
        self.train_gt=[]
        self.test_gt=[]
        self.pred=[]
    def read_input(self):
        try:
            with open(self.train_file,'r') as f:
                lines=f.readlines()
                for line in lines:
                    if not line.strip():
                        continue
                    line=line.strip()
                    data_ls=line.split(',')
                    category=data_ls[-1].strip()
                    pts=[float(i.strip()) for i in data_ls[0:len(data_ls)-1] ]
                    pts=np.array(pts)
                    self.train_gt.append(category)
                    self.train_data.append(pts)
        except FileNotFoundError:
            print("Train File not found")
            exit(-1)
        try:
            with open(self.test_file,'r') as f:
                lines=f.readlines()
                for line in lines:
                    if not line.strip():
                        continue
                    line=line.strip()
                    data_ls=line.split(',')
                    category=data_ls[-1].strip()
                    pts=[float(i.strip()) for i in data_ls[0:len(data_ls)-1] ]
                    pts=np.array(pts)
                    category=data_ls[-1].strip()
                    self.test_gt.append(category)
                    self.test_data.append(pts)
        except FileNotFoundError:
            print("File not found")
            exit(-1)
    def algorithm(self):
        self.read_input()
        train_len=len(self.train_data)
        test_len=len(self.test_data)
        self.distance_matrix=np.zeros((test_len,train_len))
        for i in range(test_len):
            for j in range(train_len):
                if d=='e2':
                    self.distance_matrix[i][j]=e2_distance(self.test_data[i],self.train_data[j])
                else:
                    self.distance_matrix[i][j]=manh_distance(self.test_data[i],self.train_data[j])
        for i in range(test_len):
            ls=list(self.distance_matrix[i])
            sorted_list = sorted(enumerate(ls), key=lambda x: x[1])
            sorted_list=sorted_list[:self.K]
            votes=[]
            vote_values=[]
            for idx,dist in sorted_list:
                votes.append(self.train_gt[idx])
                vote_values.append(self.distance_matrix[i][idx])
            if vote_values[0]==0.0:
                self.pred.append(votes[0])
            else:
                cw={}
                for index, c in enumerate(votes):
                    w = vote_values[index]
                    if c in cw:
                        cw[c] += 1/w
                    else:
                        cw[c] = 1/w
                sorted_class_weights = (sorted(cw.items(), key=lambda x: x[1], reverse=True))
                self.pred.append(sorted_class_weights[0][0])
            if vflag:
                print(f"want {self.test_gt[i]} got {sorted_class_weights[0][0]}")
        self.metrics()
    def metrics(self):
        classes = np.unique(self.train_gt)
        tp = np.zeros(len(classes))
        fp = np.zeros(len(classes))
        tn = np.zeros(len(classes))
        fn = np.zeros(len(classes))
        for i, c in enumerate(classes):
            tp[i] = np.sum((np.array(self.test_gt) == c) & (np.array(self.pred) == c))
            fp[i] = np.sum((np.array(self.test_gt) != c) & (np.array(self.pred) == c))
            tn[i] = np.sum((np.array(self.test_gt) != c) & (np.array(self.pred) != c))
            fn[i] = np.sum((np.array(self.test_gt) == c) & (np.array(self.pred) != c))

        for i, c in enumerate(classes):
            print(f"Label={c} Precision={int(tp[i])}/{int(tp[i]+fp[i])} Recall={int(tp[i])}/{int(tp[i]+fn[i])}")

class NaiveBayes():
    def __init__(self,train,test,C):
        self.train_file=train
        self.test_file=test
        self.train_data=np.array
        self.test_data=np.array
        self.X_train=np.array
        self.y_train=np.array
        self.X_test=np.array
        self.Y_test_gt=[]
        self.Y_test_pred=[]
        self.class_prob={}
        self.features=[]
        self.likelihoods={}
        self.pred_priors = {}
        self.C=C
    
    def read_input(self):
        self.train_data=pd.read_csv(self.train_file,header=None)
        self.test_data=pd.read_csv(self.test_file,header=None)

    def pre_process(self):
        self.X_train=self.train_data.drop([self.train_data.columns[-1]],axis=1)
        self.y_train=self.train_data[self.train_data.columns[-1]]

        self.X_test=self.test_data.drop([self.test_data.columns[-1]],axis=1)
        self.Y_test_gt=list(self.test_data[self.test_data.columns[-1]])
       
    def class_probability(self):
        for label in np.unique(self.y_train):
            label_count = sum(self.y_train == label)
            self.class_prob[label] = label_count / len(self.y_train)

    def calculate_likelihood(self):
        for feature in self.features:
            for label in np.unique(self.y_train):
                label_count=sum(self.y_train == label)
                feat_likelihood = self.X_train[feature][self.y_train[self.y_train == label].index.values.tolist()].value_counts().to_dict()
                for feat_val, count in feat_likelihood.items():
                    self.likelihoods[feature][str(feat_val) + '_' + str(label)] = (count+self.C)/(label_count+(len(self.features)*self.C))

    def metrics(self):
        classes=np.unique(self.y_train)
        tp = np.zeros(len(classes))
        fp = np.zeros(len(classes))
        tn = np.zeros(len(classes))
        fn = np.zeros(len(classes))
        for i, c in enumerate(classes):
            tp[i] = np.sum((np.array(self.Y_test_gt) == c) & (np.array(self.Y_test_pred) == c))
            fp[i] = np.sum((np.array(self.Y_test_gt) != c) & (np.array(self.Y_test_pred) == c))
            tn[i] = np.sum((np.array(self.Y_test_gt) != c) & (np.array(self.Y_test_pred) != c))
            fn[i] = np.sum((np.array(self.Y_test_gt) == c) & (np.array(self.Y_test_pred) != c))
        for i, c in enumerate(classes):
            print(f"Label={c} Precision={int(tp[i])}/{int(tp[i]+fp[i])} Recall={int(tp[i])}/{int(tp[i]+fn[i])}")


    def algorithm(self):
        self.read_input()
        self.pre_process()
        self.features=list(self.X_train.columns)
        for feature in self.features:
            self.likelihoods[feature] = {}
            for feat_val in np.unique(self.X_train[feature]):
                for outcome in np.unique(self.y_train):
                    self.likelihoods[feature].update({str(feat_val)+'_'+str(outcome):0})
                    self.class_prob.update({outcome: 0})
                                        
        self.class_probability()
        self.calculate_likelihood()
        
        for query in np.array(self.X_test):
            prob_poss={}
            for label in np.unique(self.y_train):
                label_prob=self.class_prob[label]
                p=1
                for f,val in zip(self.features,query):
                    key=str(val)+'_'+str(label)
                    p*=self.likelihoods[f][key]
                p*=label_prob
                prob_poss[label]=p
            max_value=max(prob_poss.values())
            max_key=max(prob_poss,key=lambda k: prob_poss[k])
            #print(f"For query {query} : {max_value}, {max_key}")
            self.Y_test_pred.append(max_key)
        #print(self.Y_test_pred,self.Y_test_gt)
        self.metrics()
      
class Kmeans():
    def __init__(self,train_file,c):
        self.train_file=train_file
        self.centroids=c
        self.K=len(self.centroids)
        self.X_train={}
        self.prev_centroids=None
        self.max_iter=1000
    def preprocess(self):
        cl=[]
        for c in self.centroids:
            pts=c.split(",")
            p=([float(i) for i in pts])
            cl.append(p)
        self.centroids=np.array(cl)      
    def read_input(self):
        try:
            with open(self.train_file,'r') as f:
                lines=f.readlines()
                for line in lines:
                    if not line.strip():
                        continue
                    line=line.strip()
                    line=line.split(',')
                    name=line[-1]
                    line=line[:-1]
                    pts=[float(i) for i in line]
                    pts=np.array(pts)
                    self.X_train[name]=pts
        except FileNotFoundError:
            print("File not found")
            exit(-1)
    def algorithm(self):
        self.preprocess()
        self.read_input()
        iteration=0
        while np.not_equal(self.centroids,self.prev_centroids).any() and iteration<self.max_iter:
            sorted_pts=[[] for _ in range(self.K)]
            for key in self.X_train.keys():
                if d=='e2':
                    dist=e2_distance(self.X_train[key],self.centroids,True)
                else:
                    dist=manh_distance(self.X_train[key],self.centroids)
                centroid_idx = np.argmin(dist)
                sorted_pts[centroid_idx].append(self.X_train[key])
            self.prev_centroids=np.copy(self.centroids)
            for i,cluster in enumerate(sorted_pts):
                if len(cluster)==0:
                    self.centroids[i]=self.prev_centroids[i]
                else:
                    self.centroids[i]=np.mean(cluster,axis=0)
            iteration += 1
        for i,cluster in enumerate(sorted_pts):
            print(f"C{i+1} =",end='')
            print("{",end='')
            key_list = [key for k in cluster for key, val in self.X_train.items() if np.array_equal(val, k)]
            print(", ".join(key_list),end='')
            print("}")
        
        for row in self.centroids:
            print(f"({row})")

def main():
    global train_file
    global test_file
    global K
    global algo
    global C
    global vflag
    global d
    centroids=[]
    parser = argparse.ArgumentParser()
    parser.add_argument('-train',type=str)
    parser.add_argument('-test',type=str)
    parser.add_argument('-K',type=int)
    parser.add_argument('-C',type=float)
    parser.add_argument('-v','--verbose',action='store_true',help='enable verbose mode',default=False)
    parser.add_argument('-d','--distance',type=str,default='e2')
    parser.add_argument("centroids",nargs="*",help="Initial centroids for Kmeans")
    args = parser.parse_args()
    if args.train is None:
        print("No train file given. Exiting!")
        exit(-1)
    else:
        train_file=args.train
    if args.test is None:
        test_file=None
    else:
        test_file=args.test
    if args.K is None:
        algo='Kmeans'
        K=None
        centroids=args.centroids
    elif args.K==0:
        algo='Naive'
        K=None
    elif args.K>0:
        algo='KNN'
        K=args.K
    else:
        print("K can't be negative. Exiting")
        exit(-1)
    if args.C is not None:
        C=args.C
    else:
        C=0
    if args.distance not in ['e2','manh']:
        print("Distance can be Euclidean Sq or Manhattan distance. Exiting!")
        exit(-1)
    d=args.distance
    vflag=args.verbose
    if algo=='KNN':
        kobj=KNN(K,train_file,test_file)
        kobj.algorithm()
    elif algo=='Naive':
        nobj=NaiveBayes(train_file,test_file,int(C))
        nobj.algorithm()
    else:
        kmobj=Kmeans(train_file,centroids)
        kmobj.algorithm()

if __name__=="__main__":
    main()