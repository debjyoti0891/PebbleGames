
from __future__ import print_function
from z3 import *
import sys
import itertools

'''
def PbLe(args, k):
    """Create a Pseudo-Boolean inequality k constraint.
 
    >>> a, b, c = Bools('a b c')
    >>> f = PbLe(((a,1),(b,3),(c,2)), 3)
    """
    _z3_check_cint_overflow(k, "k")
    ctx, sz, _args, _coeffs = _pb_args_coeffs(args)
    return BoolRef(Z3_mk_pble(ctx.ref(), sz, _args, _coeffs, k), ctx)
   ''' 
    
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

'''Example 3 
  0>4
  1>4
  0>3
  3>5
  0>5
  2>5
'''

T = 10 # number of cycles 

N = 3  # number of registers
V = 7  #number of vertices in the graph
out = [6]
'''

N = 3
V = 4
out = [3]
'''
for v in range(V):
    g[v] = []


g[6] = [4,5]
g[5] = [2,3,0]
g[3] = [0]
g[4] = [0,1]
'''

g[3] = [0,1,2]
g[1] = [0] 
'''
succList = dict()
for v in g.keys():
    
    for p in g[v]:
        if p not in succList.keys():
            succList[p] = [v]
        else:
            succList[p].append(v)


# assignment variables assigned_v_t
assigned = [[ Bool("assigned_%s_%s" % (v, t)) for t in range(T+1) ] for v in range(V) ]

# previously assigned prev_v_t
prevAssigned = [[Bool("prev_%s_%s" % (v,t)) for t in range(T+1)] for v in range(V)]

s = Solver()
# all vertices are not assigned at the start
for v in range(V):
   s.add(assigned[v][0] == False) 

for v in range(V):
    for t in range(1,T+1):
        orTerm = []
        for oldT in range(t):
            orTerm.append(assigned[v][oldT])
        print(len(prevAssigned), len(prevAssigned[v]), v, t)
        s.add(prevAssigned[v][t] == Or(orTerm))

#final configuration 
for v in out:
    s.add(assigned[v][T] == True)

sliding = True 
if not sliding:
    # register allocation 
    for t in range(1,T+1):
        for v in range(V):
            andTerm = []
            
            for p in g[v]:
                print('T',t,'|',v,'<-',p)
                andTerm.append(assigned[p][t])
                andTerm.append(assigned[p][t-1])
            s.add(Or(Not(assigned[v][t]), Or(assigned[v][t-1],And(andTerm))))
else:
    # allocation with sliding 
    for t in range(1,T+1):
        
        for v in range(V):

            orTerm = []

            # all predecessors must be pebbled
            andTerm = []
            
            for p in g[v]:
                print('T',t,'|',v,'<-',p)
                andTerm.append(assigned[p][t])
                andTerm.append(assigned[p][t-1])
            orTerm.append(And(andTerm))
            
            # or any one pebble from a predecessor has been slided
            for p in g[v]:
                
                andTerm = []
                andTerm.append(assigned[p][t-1]) # was assigned in last cycle
                andTerm.append(Not(assigned[p][t])) # this cycle unpebbled 

                for pr in g[v]: # all the other predecessors are pebbled 
                    if pr != p:
                        andTerm.append(assigned[pr][t])
                        andTerm.append(assigned[pr][t-1])
                
                # successor must have been pebbled previously
                
                for succ in succList[p]:

                    if succ != v: 
                        andTerm.append(prevAssigned[succ][t])
                        
                
                orTerm.append(And(andTerm))
            
            s.add(Or(Not(assigned[v][t]), Or(assigned[v][t-1],Or(orTerm))))

                    

# constraint on single time computation
for v in range(V):

    for t in range(2,T+1):
        OrTerm = []
        for oldt in range(t):
            OrTerm.append(And(assigned[v][oldt], Not(assigned[v][oldt+1])))
        s.add(Or(Not(Or(OrTerm)), Not(assigned[v][t])))

# constraint on number of allocations
for t in range(1,T+1):
    alloc = []
    for v in range(V):
        alloc.append(assigned[v][t])
    #print(N,alloc)
    alloc.append(N)
    f = AtMost(*alloc)
    s.add(f)


print(s.check())

def boolP(s):
    if(s):
        return 1
    else:
        return 0

if(s.check() == sat):
    m = s.model()
    print("Assignment d->v")
    print('t   |',end='')
    for v in range(V):
        print(" %3d" % v, end="")
    print("")
    for t in range(T+1):
        print("t%3d|"%(t),end="")
        for v in range(V):
            print(' %3d'% ( boolP(m[assigned[v][t]])), end="")
        print("",end="\n")
    

    print("\n Prev Assignment d->v")
    print('t   |',end='')
    for v in range(V):
        print(" %3d" % v, end="")
    print("")
    for t in range(T+1):
        print("t%3d|"%(t),end="")
        for v in range(V):
            print(' %3d'% ( boolP(m[prevAssigned[v][t]])), end="")
        print("",end="\n")
else:
    print('Model could not be solved')

'''
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
'''
