#!/usr/bin/python3

import os 
import argparse
import datetime
from igraph import *


parser = argparse.ArgumentParser()
#parser.add_argument("square", type=int,
#                    help="display a square of a given number")
parser.add_argument("mapping", help="select type of mapping[0,1]\n \
                    0=pebble game 1=reversible pebble game", type=int, choices=[0,1])
parser.add_argument("file", help="edge list file name", type=str)
parser.add_argument("-d", "--devices", help="number of devices used for mapping", type=int)
parser.add_argument("-c", "--cycles", help="number of cycles available for mapping", type=int)
parser.add_argument("-s", "--sliding", help="allow sliding for pebble game mapping",action="store_true")
parser.add_argument("--mindev", help="determines the minimum number of devices",action="store_true")
parser.add_argument("--outdir", help="specify output file directory", type=str)
parser.add_argument("--compare", help="specify second file to check pebble equivalence", type=str)
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                    help="increase output verbosity")



args = parser.parse_args()

# read graph file 
graph = Graph(directed=True)
graph.Read_Edgelist(args.file,directed=True)



if args.mindev:
    # iterative call if mindev issued
    print('iterative variant')


else:
    # call once 

    # check type of mapping 
    if args.mapping == 0: # pebble game 
        pass 
    elif args.mapping == 1: # reversible pebble game 
        pass 


answer = args.square**2
if args.verbosity == 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)