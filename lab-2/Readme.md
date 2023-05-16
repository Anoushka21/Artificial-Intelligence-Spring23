ag8733 AI Lab 2 submission

Command to run-\
  python3 solver.py [-v] ncolors input.txt

[-v] -----> optional and gives verbose output\
ncolors ----> # of colors and should be 2,3 or 4\
input.txt ----> input file containing the graph/map


This a Map/vertex coloring program based on DPLL Algorithm.
Three types of CNF clauses are generated-
1. At least one color
2. No adjacent same colors
3. At most one color for each vertex:

