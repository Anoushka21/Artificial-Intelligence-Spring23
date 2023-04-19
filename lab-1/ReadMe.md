Minmax and Alpha-beta game tree Solver

Command to run the code-

python3 minmax.py [-v] [-ab] n max/min file.txt

[-v] --> optional argument to enable verbose mode\
[-ab] ---> optional argument to enable alpha-beta pruning\
n ---> positive integer which refers to max-value-cutoff\
max/min ---> signifies if the root player is max player or min player\
file.txt ----> input file\

Some examples :\
input-1.txt in default mode, with max-value-cutoff [-10,10] and root is the max player\
        python3 minmax.py 10 max input-1.txt

input-1.txt in verbose mode, with max-value-cutoff [-10,10] and root is the max player\

        python3 minmax.py -v 10 max input-1.txt\

input-1.txt in verbose mode with alpha-beta pruning with max-value-cutoff [-10,10] and root is the max player\

        python minmax.py -v -ab 10 max input-1.txt\


***NOTE***\
In case of a tie while choosing a max or min value, the program chooses the first node in the order in which it was defined in input file.
For example, consider:\
a: [a1,a2,a3]\
a1=2\
a2=-1\
a3=2\
max(a) has a tie between a1 and a3 and can select any. My code selects a1 since it was the node first defined as child of "a" in the inpu file\


The program also checks for the following-\
1) Presence of Cycle\
2) Presence of multiple roots- nodes with no incoming edge\
3) A leaf node being redefined as a internal node and vice-versa\
4) Node Failure --> missing leaf or internal node\
5) Node name syntax errors\
6) Invalid  no of arguments passed\
