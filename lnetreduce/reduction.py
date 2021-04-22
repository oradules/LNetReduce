import sys
import csv
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pygraphviz as pgv
#import pydot

def load( filename):
    "Load a weighted graph from a file where each line encodes an arc as a triplet (source;target;weight)."
    df = pd.read_csv(filename, delimiter=';')
    return nx.from_pandas_edgelist(df, edge_attr='weight', create_using=nx.DiGraph)

def save_graph(G, filename):
    "Save a graph to a file: list of edges in the format: 'source,target,weight'"
    with open(filename, 'wb') as f:
        f.write(b'source;target;weight\n')
        nx.readwrite.edgelist.write_weighted_edgelist(G, f, delimiter=';')

def prune( G, debug=False ):
    """Given a digraph G, construct and return a pruned version of G
       keeping only the single fastest out-going edge for each node""" 
    fastest_edge_list = []
    for node in G.nodes():
        edges = G.out_edges(node,data='weight')
        if edges:
            fastest = min( edges, key=lambda x:x[2] )
            check_unique(edges, fastest[2], debug)
            fastest_edge_list.append(fastest)

    #creates and returns the pruned graph out of the list of the fastest edges
    pruned_G = nx.DiGraph()
    pruned_G.add_weighted_edges_from(fastest_edge_list)
    return pruned_G

############################### Restoring the out edges #######################
#Returns the list of edges going out from a cycle of the pruned graph.
def cycle_out_edges( G, cycle, cycle_edges ):
    J = G.copy()
    J.remove_edges_from(cycle_edges)
    G_minus_cycle = G.copy()
    G_minus_cycle.remove_nodes_from(cycle)
    J.remove_edges_from ( G_minus_cycle.edges(data='weight') ) 
    return [ e for e in J.edges(data='weight') if e[0] in cycle ]

#Restores every edge going out of the cycles of the pruned graph.
def restore_cycles_out_edges( G, pruned_G ):
    restored_G = pruned_G.copy()
    for cycle in nx.simple_cycles(pruned_G):
        H = G.subgraph(cycle)
        out_edges = cycle_out_edges( G, cycle, H.edges(data='weight') )
        restored_G.add_weighted_edges_from(out_edges)
    return restored_G

############################### Gluing the graph ##############################
#Returns the list of edges going into a cycle of the pruned graph.
def cycle_in_edges( G, cycle, cycle_edges ):
    J = G.copy()
    J.remove_edges_from(cycle_edges)
    G_minus_cycle = G.copy()
    G_minus_cycle.remove_nodes_from(cycle)
    J.remove_edges_from ( G_minus_cycle.edges(data='weight') ) 
    return [e for e in J.edges(data='weight') if e[0] not in cycle]

#Connects the in edges of a cycle to a new node.
def redirect( in_list, new_node ):
    return map( lambda x:(x[0],new_node,x[2]), in_list )

#Given a list and a value, selects from it a sublist for which
#the first coordinate of its elements matches the value, 
#then returns the first element of the sublist.
def sel( liste, value ):
    L = [edge for edge in liste if edge[0] == value]
    return L[0]

#Returns a renormalization of the weights of the out edges of a cycle,
#with respect to the restored graph, and connects them to the origin 
#of the limiting step.
def renorm( cycle_edges, out_edges, lim_step ):
    return map( lambda x:( lim_step[0], x[1], x[2] + lim_step[2] \
     - sel(cycle_edges,x[0])[2] ), out_edges )

#Given G and one of its cycle, returns a graph for which the cycle is glued,
#i.e. supressed and replaced by a new vertex whose label will be this of
#the limiting step (origin).
def glue_cycle( pruned_G, restored_G, cycle, debug=False ):
    #creates the in and out lists of edges of the given pruned graph's cycle
    H = pruned_G.subgraph(cycle)
    cycle_edges = H.edges(data='weight')
    out_list = cycle_out_edges( restored_G, cycle, cycle_edges )
    in_list = cycle_in_edges( restored_G, cycle, cycle_edges )
    #with the limiting step, renormalize the out edges 
    #and redirect the in edges
    lim_step = max( cycle_edges, key=lambda x:x[2] )
    check_unique(cycle_edges, lim_step[2], debug)
    out_edges = select_unique_edges( renorm( cycle_edges, out_list, lim_step ) )
    in_edges = select_unique_edges( redirect( in_list, lim_step[0] ) )
    #creates the glued graph by taking the restored graph and replacing
    #the vertices of the pruned graph's cycle by a new vertex, named
    #after the vertex at the origin of its limiting step, then
    #adding its renormalized out edges together with the redirected in edges
    glued_G = restored_G.copy()
    glued_G.remove_nodes_from(cycle)
    glued_G.add_node( lim_step[0], cycle=cycle_edges, out_edges=in_list,
                      glued_in=in_list, glued_out=out_list )
    glued_G.add_weighted_edges_from(out_edges)
    glued_G.add_weighted_edges_from(in_edges)
    return glued_G

def select_unique_edges(edges):
    """Take a list of edges, detect multiarcs and select the one with lowest weight.
    This is useful When restoring arcs to/from a glued cycle as networkx will only keep the last one"""
    d = {}
    for s,t,w in edges:
        if (s,t) in d and d[(s,t)] < w:
            continue
        d[(s,t)] = w
    edges = []
    for s,t in d:
        edges.append( (s,t,d[(s,t)]) )
    return edges

#Returns the glued graph obtained by gluing every cycle of the pruned graph.
def glue_graph( pruned_G, restored_G, debug=False ):
    glued_G = restored_G.copy()
    cycles_list = list( nx.simple_cycles(pruned_G) )
    for cycle in cycles_list:
        glued_G = glue_cycle( pruned_G, glued_G, cycle, debug )
    return glued_G

#Compute the pruned graph of G then restore the out edges of its cycles,
#then glue its cycles over and over again, until the resulting graph has no
#simple cycle. Then returns the list composed of the original graph pruned
#together with all its successive glued graphs (but not pruned).
def glue( G, debug=False ):
    L = []
    i = 0
    L.append(G)
    while list( nx.simple_cycles( prune(L[i]) ) ) != []:
        i += 1
        pruned_i = prune( L[i-1] )
        restored_i = restore_cycles_out_edges( L[i-1], pruned_i )
        L.append( glue_graph( pruned_i, restored_i, debug=debug ) )
    L[0] = prune(G)
    return L

#Given a glued graph, returns the list of its glued nodes
def glued_nodes_list( G ):
    L = []
    for node in G.nodes(data=True):
        if node[1] != {}:
            L.append(node[0])
    return L

# Unglue a graph step by step. At each step:
# * restore cycle edges, except the limiting one (slowest, i.e. with highest weight)
# * edges going out of the unglued cycles are rerouted to go out of the limiting node
# * edges entering the cycle should enter on the same node as in the original graph
def unglue_stack( stack, debug=False ):
    prev = stack.pop()
    G = prev.copy()
    while stack:
        cycles = nx.get_node_attributes( prev, 'cycle' )
        incomings = nx.get_node_attributes( prev, 'glued_in' )
        outgoings = nx.get_node_attributes( prev, 'glued_out' )
        L = glued_nodes_list(prev)
        if debug:
            print( "ungluing:", cycles )
        prev = stack.pop()
        removed_nodes = [ n for n in L ]
        added_edges = []
        for i in L:
            # restore the glued cycle, without the limiting step
            cycle_edges = cycles[i]
            cycle_incoming = incomings[i]
            cycle_outgoing = outgoings[i]
            cur_outgoing = G.out_edges(i, data='weight')
            cur_incoming = G.in_edges(i, data='weight')
            cycle = [e[0] for e in cycle_edges]
            lim_step = max( cycle_edges, key=lambda x:x[2] )
            check_unique(cycle_edges, lim_step[2], debug)
            lim_node = lim_step[0]
            added_edges += [ e for e in cycle_edges if e != lim_step ]
            
            if debug:
                print('    %s (lim:%s)  ' % (i, lim_node), added_edges)
            
            # Keep the current outgoing edges (going out of the limiting node)
            # only if they do not go toward another glued cycle (avoiding duplicating it)
            cur_outgoing = [ e for e in cur_outgoing if e[1] not in L ]
            if i == lim_node:
                added_edges += cur_outgoing
            else: # should not happen: the cylce is glued on the limiting node
                if debug:
                    print( 'REDIRECT OUTGOING' )
                for edge in cur_outgoing:
                    added_edges.append( (lim_node, edge[1], edge[2]) )
            
            # Restore incoming arcs: merge current and before gluing information
            if debug:
                print('    Restore incoming edges', cur_incoming, cycle_incoming)
            for e in cur_incoming:
                cur_s, cur_t, cur_w = e
                for glued_s, glued_t, glued_w in cycle_incoming:
                    if glued_s == cur_s and glued_w == cur_w:
                        # FIXME: if the source is part of a glued cycle, it may be wrong
                        # in this case it should be safe to use cur_s instead of glued_s
                        # (requires updating the surrounding if and performing some extra tests)
                        added_edges.append( (cur_s, glued_t, glued_w) )
                        break
        
        if debug:
            print('    Ready to unglue:', removed_nodes, added_edges)
        G.remove_nodes_from(removed_nodes)
        G.add_weighted_edges_from( added_edges )
    
    return G

############################### Instance validity check #######################
def validity_check( G ):
    L = [e[2] for e in G.edges(data='weight')]
    return len(set(L)) == len(L)

############################### Dynamic #######################################
#The right vectors of a reduced digraph are here given in the form of a matrix,
#where the lines are the edges of the graph and the columns the veritces.
#Now, for each edge, put a one into the column indexed by its origin node, then
#via a depth-first search, find its first successor edge in the graph whose 
#weight is strictly bigger (i.e. slower reaction speed). Then put a -1 at the
#column indexed by the origin node of this latter edge.
def right_vector( G ):
    node_to_index = { n:i for i,n in enumerate(G.nodes()) }
    M = np.zeros( (G.size(),G.order()), int )
    for i,e in enumerate( G.edges(data='weight') ):
        M[i][node_to_index[e[0]]] = 1
        w = e[2]
        dfs = list( nx.edge_dfs(G,e) )
        L = [f for f in dfs if G.get_edge_data(*f)['weight'] > w]
        if L != []:
            M[i][ node_to_index[L[0][0]] ] = -1
        else:
            M[i][ node_to_index[dfs[-1][1]] ] = -1
    return M

#The right vectors of a reduced digraph are here given in the form of a matrix,
#where the lines are the edges of the graph and the columns the veritces.
#Now, for each edge, put a one into the column indexed by its origin node, then
#via a reversed depth-first searched, find the first predecessor edge in the
#graph whose weight is strictly bigger (i.e. slower reaction speed). Then put a
#one at the column indexed by the origin node of this latter edge.
def left_vector( G ):
    node_to_index = { n:i for i,n in enumerate(G.nodes()) }
    M = np.zeros( (G.size(),G.order()), int )
    for i,e in enumerate( G.edges(data='weight') ):
        M[i][ node_to_index[e[0]] ] = 1
        v = G.get_edge_data(*e)['weight']
        H = G.reverse()
        dfs = list( nx.edge_dfs(H,e[0]) )
        if dfs != []:
            for f in dfs:
                if H.get_edge_data(*f)['weight'] < v:
                    M[i][ node_to_index[f[1]] ] = 1
                else:
                    break
    return M

def reduce_graph( G, debug=False ):
    return unglue_stack( glue(G), debug )


def draw_graph( G , file, drawformat, layout):
    AG = nx.nx_agraph.to_agraph(G)
    LE = AG.edges()
    for a,b in LE:
        AG.remove_edge(u=a,v=b)
    for c,d,w in G.edges(data=True):
        AG.add_edge(u=c,v=d, label=w['weight'])
    AG.draw(path=file,format=drawformat,prog=layout,args="-Nheight=0.3 -Nwidth=0.3")


def plot_graph(G, node_color='lightgray', edge_color='black', edge_labels=None, layout='neato', curve=False, save=None):
    fig = plt.figure()
    node_names = [ n for n in G ]
    if isinstance(layout, str):
        pos = nx.nx_pydot.graphviz_layout(G, prog=layout)
    else:
        pos = layout
    params = {
        'with_labels':True,
        'node_color': node_color,
        'font_size':20, 
        'node_size':1000,
        'arrowsize':30,
        'arrowstyle':'->',
    }
    if curve:
        params['connectionstyle'] = 'arc3,rad=0.2'
    nx.draw(G, pos, **params)
    if edge_labels:
        if edge_labels is True:
            edge_labels = 'weight'
        if isinstance(edge_labels, str):
            edge_labels = nx.get_edge_attributes(G, edge_labels)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color=edge_color, label_pos=0.65, font_size=16)
    
    if save and isinstance(save, str):
        plt.savefig(save)
    return fig,pos

def check_unique(edges, best, debug=False):
    count = 0
    for v in edges:
        if v[2] == best:
            if count:
                if debug:
                    print("Duplicated best edge")
                raise DuplicateMinError()
            count += 1

class DuplicateMinError(Exception):
    def __init__(self, info):
        self.info = info


############################# Main ############################################

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print( 'usage:' )
        print( sys.argv[0] + ' <filename>' )
        sys.exit()

    filename = sys.argv[1]
    input_G = load(filename)
    draw_graph(input_G,filename+"input_graph.png",'png','dot')

    try:
        u_G = reduce_graph( input_G )
    except:
        print( "Sorry, this instance is not reducible because its reduced \
             form has non separated reaction speeds" )
        sys.exit()

    save_graph( u_G, '%s_reduced.tsv' % filename)
    draw_graph(u_G, filename+"reduced_graph.png", 'png', 'dot')

    # Compute the right and left vectors
    R = right_vector(u_G)
    L = left_vector(u_G)
    print( L )

