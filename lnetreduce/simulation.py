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
    return [ np.asarray(a) for a in zip(*[ (a,b,c) for a,b,c in G.edges(data='weight') ])]

def from_graph(G):
    X = np.zeros((len(G.edges),3)).astype(np.int32)
    node_names = [ n for n in G ]

    for i,e  in enumerate(G.edges):
        X[i,0] = node_names.index(e[0])
        X[i,1] = node_names.index(e[1])
        X[i,2] = G.get_edge_data(e[0],e[1])['weight']

    return X

def simulate(a, timescale, steps=1000, logx=True):
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
    x0 = np.ones( (n,) )

    # construct the update function
    def dx_dt(x,t=0):
        r = np.zeros( (nr,) )
        for i in range(nr):
            for j in range(n):
                if S[j,i] == -1:
                    r[i] = x[j] * k[i]
        return np.dot(S,r)

    if logx:
        t = np.logspace(0, timescale, steps)
    else:
        t = np.linspace(0, 10**timescale, steps)
    return t,integrate.odeint(dx_dt, x0, t, mxstep=5000),index_nodes


def plot_trace(trace, name=None, time=None, labels=None, logx=False, logy=True, ylabel='concentration', title=None):
    styles = ( "-","--", "-.", ":" )
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    if time is None:
        time = np.arange(len(trace))
    trace = trace.transpose()
    f1 = plt.figure()
    idx=0
    for data in trace:
        style = styles[ int(idx / 7) ]
        if labels: label = labels[idx]
        else: label="x%s" % (idx)
        plt.plot(time, data, label=label, linestyle=style)
        if logx:
            plt.xscale('log')
        if logy:
            plt.yscale('log')
        idx += 1
    plt.grid()
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel('time')
    plt.ylabel(ylabel)
    if title: plt.title(title)
    if name:
        f1.savefig('%s.png' % name, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close(f1)
    else:
        return plt


def simulate_and_plot(a, timescale, steps=1000, save=None):
    t,X,labels = simulate(a, timescale, steps=steps)
    return plot_trace(X, save, time=t, logy=False, logx=True,labels=labels)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print( 'usage:' )
        print( sys.argv[0] + ' <filename> <timescale>' )
        sys.exit()
    
    filename = sys.argv[1]
    timescale = int(sys.argv[2])
    simulate_and_plot(filename, timescale, steps=1000, save=filename)

