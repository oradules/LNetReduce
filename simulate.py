import sys
import numpy as np
import pylab as plt
from scipy import integrate

def load(filename):
    return np.loadtxt(filename, skiprows=1, delimiter=';', dtype=int)

def simulate(a, timescale):
    orders=a[:,2]
    source=a[:,0]
    target=a[:,1]
    nodes = set(source).union(target)

    n=max(nodes) + 1
    nr=len(orders)
    alpha = 1.0 / 10
    k = alpha ** orders

    # matrix of reactions
    S=np.zeros( (n,nr) )
    for i in range(nr):
        S[source[i],i] = -1
        S[target[i],i] =  1

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

    t0 = 0
    tmax = 10**timescale
    steps = 100000

    t = np.linspace(t0, tmax, steps)
    return integrate.odeint(dx_dt, x0, t, mxstep=5000)


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


def simulate_and_plot(filename, timescale, save=False):
    a = load(filename)
    if not save: filename = None
    X = simulate(a, timescale)
    plot_trace(X, filename, logy=False, logx=True)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print( 'usage:' )
        print( sys.argv[0] + ' <filename> <timescale>' )
        sys.exit()
    
    filename = sys.argv[1]
    timescale = int(sys.argv[2])
    simulate_and_plot(filename, timescale, save=True)

