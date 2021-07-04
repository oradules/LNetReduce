import sys
import numpy as np
import pylab as plt
import networkx as nx
from scipy import integrate

def load(filename):
    a,b=np.loadtxt(filename, skiprows=1, delimiter=';', dtype=str, unpack=True, usecols=(0,1))
    c=np.loadtxt(filename, skiprows=1, delimiter=';', dtype=int, unpack=True, usecols=(2))
    return [a,b,c]

def graph_to_sim(G):
    return [ np.asarray(A) for A in zip(*[ (a,b,c) for a,b,c in G.edges(data='weight') ])]

def simulate(a, timescale, steps=1000, logx=True, method=None,initial_state=None):
    if isinstance(a, nx.Graph):
        a = graph_to_sim(a)
    elif isinstance(a, str):
        a = load(a)

    orders=a[2]#a[:,2]
    source=a[0]#[:,0]
    target=a[1]#[:,1]
    nodes = set(source).union(target)

    n=len(nodes)
    nr=len(orders)
    alpha = 1.0 / 10
    k = alpha ** orders

    index_nodes=[]
    for o in nodes:
        index_nodes.append(o)
    index_nodes.sort()

    index_source=[]
    for s in source:
        for key in range(len(index_nodes)):
            if index_nodes[key]==s:
                index_source.append(key)
    index_target=[]
    for tar in target:
        for l in range(len(index_nodes)):
            if tar==index_nodes[l]:
                index_target.append(l)

    # matrix of reactions
    S=np.zeros( (n,nr) )
    for i in range(nr):
        S[index_source[i],i] = -1
        S[index_target[i],i] =  1

    # initial state
    # initial state
    if initial_state is None:
        x0 = np.ones( (n,) )
    else:
        x0 = initial_state

    # construct the update function
    def dx_dt(t,x):
        r = np.zeros( (nr,) )
        for i in range(nr):
            for j in range(n):
                if S[j,i] == -1:
                    r[i] = x[j] * k[i]
        return np.dot(S,r)

    if logx:
        mx = timescale
        t = np.logspace(0, timescale, steps)
    else:
        mx = 10**timescale
        t = np.linspace(0, mx, steps)
    
    if method is None:
        method = 'LSODA'
    elif method == 'odeint':
        X = integrate.odeint(dx_dt, x0, t, mxstep=5000, tfirst=True).transpose()
        return MSol(X,t,index_nodes)
    
    sol = integrate.solve_ivp(dx_dt, (0,t[-1]), x0, method=method, t_eval=t)
    
    sol.labels = index_nodes
    return sol

class MSol:
    def __init__(self, y,t,labels):
        self.t = t
        self.y = y
        self.labels = labels

def plot_trace(trace, time, labels=None, logx=True, logy=False, ylabel='concentration', title=None):
    styles = ( "-","--", "-.", ":" )
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    if time is None:
        time = np.arange(len(trace))
    for idx,data in enumerate(trace):
        style = styles[ int(idx / 7) ]
        if labels: label = labels[idx]
        else: label="x%s" % (idx)
        plt.plot(time, data, label=label, linestyle=style)
        if logx:
            plt.xscale('log')
        if logy:
            plt.yscale('log')
    plt.grid()
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.subplots_adjust(right=0.7)
    plt.xlabel('time')
    plt.ylabel(ylabel)
    if title: plt.title(title)


def simulate_and_plot(a, timescale, steps=1000, save=None, method=None, title=None, initial_state=None,ylabel='concentration'):
    sol = simulate(a, timescale, steps=steps, method=method,initial_state=initial_state)
    plot_trace(sol.y, sol.t, sol.labels, title=title,ylabel=ylabel)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print( 'usage:' )
        print( sys.argv[0] + ' <filename> <timescale>' )
        sys.exit()
    
    filename = sys.argv[1]
    timescale = int(sys.argv[2])
    simulate_and_plot(filename, timescale, steps=1000, save=filename)

