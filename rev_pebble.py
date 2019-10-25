
from __future__ import print_function
from z3 import *
import sys
import itertools

''' Example graph
    1 -> 4
    2 -> 4
    4 -> 5
    3 -> 5
# define the graph 
g = dict()
g[3] = [0,1]
g[4] = [2,3]
g[1] = []
g[0] = []
g[2] = []

'''
''' Example 2 :
    0 -> 1
    2 -> 4
    3 -> 4
    1 -> 5
    3 -> 5
    4 -> 5
'''
g = dict()
'''g[5] = [1,3,4]
g[4] = [2,3]
g[1] = [0]
g[2] = g[3] = g[0] = []'''
g[0] = g[1] = g[2] = g[3] = []
g[4] = [0,1]
g[5] = [2]
g[6] = [3]
g[7] = [4,5,6]
T = 13 # number of cycles 
Q = 5 # number of qubits
V = 8 #number of vertices in the graph

# assignment variables assigned_v_t
assigned = [[ Bool("assigned_%s_%s" % (v+1, t+1)) for t in range(T) ] for v in range(V) ]


# qubit to vertex assignment 
qubitToV = [[ [ Bool("qv_%s_%s_%s" % (q+1, v+1, t+1)) for t in range(T) ] for v in range(V) ] for q in range(Q)]

# qubit assignment 
qubitAssign =  [ [ Bool("q_%s_%s" % (q+1, t+1)) for t in range(T) ] for q in range(Q) ]

# compute node step
computeStep = [ [ Bool("comp_%s_%s" % (v+1, t+1)) for t in range(T) ] for v in range(V) ]

# uncompute node step
uncomputeStep = [ [ Bool("uncomp_%s_%s" % (v+1, t+1)) for t in range(T) ] for v in range(V) ]

# uncomputed qubit 
uncompQ =  [ [ Bool("ucompq_%s_%s" % (q+1, t+1)) for t in range(T) ] for q in range(Q) ]

# free qubit
freeQ =  [ [ Bool("freeq_%s_%s" % (q+1, t+1)) for t in range(T) ] for q in range(Q) ]
s = Solver()

# atmost one assignment per cycle per qubit
for t in range(T):
    for q in range(Q):
        orTerm = []
        for v in range(V):
            andTerm = []
            for vi in range(V):
                if(vi == v):
                    andTerm.append(qubitToV[q][vi][t])
                else:
                    andTerm.append(Not(qubitToV[q][vi][t]))
            orTerm.append(And(andTerm))
        andTerm = []
        for v in range(V):
            andTerm.append(Not(qubitToV[q][v][t]))
        orTerm.append(And(andTerm))
        s.add(Or(orTerm))
        #if(t == 0):
        #    print('q=',q,orTerm)
# atmost one qubit assignment per vertex
for t in range(T):
    for v in range(V):
        orTerm = []
        for q in range(Q):
            andTerm = []
            for qi in range(Q):
                if(qi == q):
                    andTerm.append(qubitToV[qi][v][t])
                else:
                    andTerm.append(Not(qubitToV[qi][v][t]))
            orTerm.append(And(andTerm))
        andTerm = []
        nand = []
        for q in range(Q):
            andTerm.append(Not(qubitToV[q][v][t]))
        orTerm.append(And(andTerm))
        s.add(Or(orTerm))
        #if(t == 0):
        #    print('v=',v,orTerm)
# vertex has been assigned a qubit
for t in range(T):
    for v in range(V):
        orTerm = []
        for q in range(Q):
            orTerm.append(qubitToV[q][v][t])
        s.add(assigned[v][t] == Or(orTerm))

# free qubit 
for t in range(T):
    for q in range(Q):
        andTerm = []
        for v in range(V):
            andTerm.append(Not(qubitToV[q][v][t]))
        s.add(freeQ[q][t] == And(andTerm))
# initial configuration
for q in range(Q):
    for v in range(V):
        s.add(qubitToV[q][v][0] == False)

# final configuration
# outputs must be assigned 
s.add(assigned[V-1][T-1] == True)
# rest of the vertices must be uncomputed 
for v in range(V-1):
    s.add(Not(assigned[v][T-1]))

# compute step 
for t in range(1,T):
    for v in range(V):
        andTerm = [Not(assigned[v][t-1])]
        for p in g[v]:
            andTerm.append(assigned[p][t-1])
        s.add(If(Not(And(andTerm)), Not(computeStep[v][t]), True))
        s.add(If(computeStep[v][t], assigned[v][t],True))
        s.add(If(And(Not(computeStep[v][t]), Not(assigned[v][t-1])),
            Not(assigned[v][t]), True))

# transitive assigment 
for t in range(1,T):
    for v in range(V):
        for q in range(Q):
            s.add(If(And(Not(uncomputeStep[v][t]), qubitToV[q][v][t-1]),qubitToV[q][v][t],True))


# uncompute step 
for t in range(1,T):
    for v in range(V):
        andTerm = [assigned[v][t-1]]
        for p in g[v]:
            andTerm.append(assigned[p][t-1])
        s.add(If(Not(And(andTerm)), Not(uncomputeStep[v][t]), True))
        s.add(If(uncomputeStep[v][t], Not(assigned[v][t]),True))
# if qubit has been uncomputed -> set assign to zero
for t in range(1,T):
    for v in range(V):
        for q in range(Q):
           s.add(If(And(uncomputeStep[v][t],qubitToV[q][v][t-1]), And(Not(qubitToV[q][v][t]), freeQ[q][t]), True))

# compute and uncompute cannot happen together
for t in range(T):
    for v in range(V):
        s.add(Or(Not(computeStep[v][t]), Not(uncomputeStep[v][t])))

        #compute or uncompute cannot happen with uncompute of predecessors
        for p in g[v]:
            s.add(If(Or(computeStep[v][t], uncomputeStep[v][t]), Not(uncomputeStep[p][t]), True))
# prevent uncomputed qubit from being assigned

print(s.check())
def boolP(s):
    if(s):
        return 1
    else:
        return 0
#for c in s.assertions():
#    print(c)
def toSMT2Benchmark(f, status="unknown", name="benchmark", logic=""):
    v = (Ast * 0)()
    if isinstance(f, Solver):
        a = f.assertions()
        if len(a) == 0:
            f = BoolVal(True)
        else:
                f = And(*a)
    return Z3_benchmark_to_smtlib_string(f.ctx_ref(), name, logic, status, "", 0, v, f.as_ast())
#print(toSMT2Benchmark(s, logic="QF_LIA"))
if(s.check() == sat):
    m = s.model()
    print("Assignment q->v")
    for t in range(T):
        print("t%3d|"%(t),end="")
        for v in range(V):
            print(" %3d" % v, end="")
        print("")
        for q in range(Q):
            print("%4d|"% (q), end="")
            for v in range(V):
                print(' %3d'% ( boolP(m[qubitToV[q][v][t]])), end="")
            print("",end="\n")
        print("")
    print("Free qubits")
    print("    ",end="")
    for q in range(Q):
        print(" %3d"% q, end="")
    print("")
    for t in range(T):
        print("t%3d" % t,end="")
        for q in range(Q):
            print(" %3d" % (boolP(m[freeQ[q][t]])), end="")
        print("")
    print("Assigned vertex")
    print("    ",end="")
    for v in range(V):
        print(" %3d"% v, end="")
    print("")
    for t in range(T):
        print("t%3d" % t,end="")
        for v in range(V):
            print(" %3d" % (boolP(m[assigned[v][t]])), end="")
        print("")
    
    print("Steps :")
    for t in range(T):
        #print("Compute   %d:" % t, end = '')
        print("t%2d:" % (t) , end = "")
        for v in range(V):
            if(m[computeStep[v][t]]):
                print(" %3d" % v, end = '')
        #print('')
        #print("Uncompute %d:" % t, end = '')
        for v in range(V):
            if(m[uncomputeStep[v][t]]):
                print(" %3d^" % v, end = '')
        print('')
