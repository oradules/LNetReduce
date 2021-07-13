import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import graphviz as gv
import pygraphviz as pgv
from IPython.display import Image as img
from PIL import Image, ImageTk
import io

def load( filename):
    "Load a weighted graph from a file where each line encodes an arc as a triplet (source;target;weight)."
    df = pd.read_csv(filename, delimiter=';')
    return nx.from_pandas_edgelist(df, edge_attr='weight', create_using=nx.DiGraph)

def save_graph(G, filename):
    "Save a graph to a file: list of edges in the format: 'source;target;weight'"
    with open(filename, 'wb') as f:
        f.write(b'source;target;weight\n')
        nx.readwrite.edgelist.write_weighted_edgelist(G, f, delimiter=';')

def prune( G, partial=False, debug=False ):
    """Given a digraph G, construct and return a pruned subgraph of G
       keeping only the single fastest out-going edge for each node.
       
       If the fastest out-going edge is not unique, this node can not be pruned. In this case
       raise an error or return a partially pruned subgraph depending on the *partial* parameter""" 
    fastest_edge_list = []
    for node in G.nodes():
        edges = G.out_edges(node,data='weight')
        if not edges: continue
        fastest = min( edges, key=lambda x:x[2] )
        if partial:
            wfast = fastest[2]
            fast_edges = [ e for e in edges if e[2] == wfast ]
            if len(fast_edges) > 1:
                print("Fastest edge is not unique for ", node)
                # FIXME: should we keep only the multiple fastest edges?
                fastest_edge_list += edges
            else:
                fastest_edge_list += fast_edges
        else:
            check_unique(edges, fastest[2], debug)
            fastest_edge_list.append(fastest)

    # If nothing is pruned, return the original graph directly
    if len(fastest_edge_list) == len(G.edges): return G

    #creates and returns the pruned graph out of the list of the fastest edges
    return G.edge_subgraph( [ e[:2] for e in fastest_edge_list ])

def reduce_graph( G, partial=False, debug=False, unglue=True, recursive=True ):
    """Reduce the graph: iteratively prune the graph and glue the resulting cycles.
    
    * After gluing, each cycle is represented by the source node of its limiting step.
    * Edges entering the glued cycle in the pruned graph are conserved.
    * Edges exiting the cycle before pruning are restored with a corrected weight.
    
    By default, aim for full reduction and raise an error if a node has multiple outgoing edges or if
    a cycle has multiple limiting steps. Enable the *partial* parameter to relax these constraints.
    
    In case of partial reduction, only terminal elementary cycles with a single limiting step are glued.
    
    Information on the glued nodes and original source of glued edges are conserved as metadata to enable the unglue step.
    """
    
    # All nodes from a glued cycle are associated to their representative, original target and weight.
    glued_nodes = {}
    
    # All representative nodes are associated to the list of nodes in the original cycle
    glued_cycles = {}
    
    # Edges entering a glued cycle in the pruned graph or exiting it in the original graph
    glued_edges = set()
    
    # Collect this information for all cycles in the pruned graph
    all_nodes = set( G.nodes )
    pruned_G = prune(G, partial=partial, debug=debug)
    for cycle in nx.simple_cycles(pruned_G):
        cycle_edges = list( pruned_G.out_edges(cycle, data='weight') )
        # Only glue cycles where all nodes have a single target (in case of partial pruning)
        if len( cycle_edges) != len(cycle):
            print("Skip non-pruned cycle: ", cycle)
            continue
        
        lim_s, _, lim_w = max( cycle_edges, key=lambda x:x[2] )
        if partial:
            if len( [ e for e in cycle_edges if e[2] == lim_w ] ) > 1:
                print("Cycle with multiple limiting steps can not be glued")
                continue
        else:
            check_unique(cycle_edges, lim_w, debug)
        
        cur_glued_nodes = { n:(lim_s,t,w) for n,t,w in cycle_edges }
        glued_nodes.update( cur_glued_nodes )
        glued_cycles[lim_s] = cycle
        
        # Collect glued edges: entering the cycle in the pruned graph or exiting it in the original graph
        other_nodes = all_nodes.difference(cur_glued_nodes)
        glued_edges.update( nx.algorithms.boundary.edge_boundary(pruned_G, other_nodes) )
        glued_edges.update( nx.algorithms.boundary.edge_boundary(G, cur_glued_nodes) )

    if len(glued_cycles) == 0:
        if debug: print("This graph has no cycle to glue!")
        if unglue: return unglue_graph(pruned_G, debug=debug)
        return pruned_G

    if debug:
        print("This graph has %s cycles to glue:" % len(glued_cycles))
        for g,c in glued_cycles.items():
            print("  *  %s: %s" % (g,c))
        print("Glued %s edges:" % len(glued_edges))
        for e in glued_edges:
            print("  *", e)


    # The glued graph contains all edges between non-glued nodes of the pruned graph
    hidden_nodes = set(glued_nodes).difference(glued_cycles)
    glued_G = pruned_G.subgraph( all_nodes.difference( hidden_nodes ) ).copy()

    # Redirect, normalize, annotate and restore glued edges
    restored_edges = {}
    for s,t in glued_edges:
        # Assume that we will copy the edge
        edge_info = G.edges[(s,t)].copy()
        
        # When the target is glued, redirect and keep track of the original one!
        if t in glued_nodes:
            if debug: print("REDIRECTING EDGE TARGET!!!")
            if "glued_target" not in edge_info: edge_info['glued_target'] = t
            t = glued_nodes.get(t)[0]

        # When the source is glued, redirect and update the weight
        if s in glued_nodes:
            s,_,w = glued_nodes[s]
            wlim = glued_nodes[s][2]
            edge_info['weight'] += wlim - w

        # Add the new edge, unless a better one already exists
        bgw = restored_edges.get( (s,t) )
        if bgw is not None and bgw['weight'] < edge_info['weight']: continue
        restored_edges[ (s,t) ] = edge_info

    # Add all glued edges
    glued_G.add_edges_from( [ (s,t,info) for (s,t),info in restored_edges.items() ] )


    # Add metadata required to restore edges in the glued cycles
    for cur_repr, cur_nodes in glued_cycles.items():
        cur_glued_cycle = []
        for src in cur_nodes:
            
            # Add existing glued cycles
            prev_glued = G.nodes[src].get('glued_cycles')
            if prev_glued:
                if debug: print('Merging %s-cycle previously glued in %s' % (len(prev_glued), src))
                cur_glued_cycle += prev_glued
            
            mrepr,tgt,w = glued_nodes[src]
            rtgt = G.edges[(src,tgt)].get('glued_target')
            if rtgt is not None and rtgt != tgt:
                if debug: print('Merging a redirected edge (%s, %s / %s, %s) !' % (src, tgt, rtgt, w))
                tgt = rtgt
            if mrepr != cur_repr:
                raise 'Mismatching representative node!'
            if src == cur_repr: continue
            cur_glued_cycle.append( (src, tgt, w) )
        glued_G.add_node(cur_repr)
        glued_G.nodes[cur_repr]['glued_cycles'] = cur_glued_cycle


    if recursive:
        return reduce_graph( glued_G, partial=partial, debug=debug, recursive=True, unglue=unglue)

    if unglue:
        return unglue_graph(glued_G, debug=debug)

    return glued_G

def unglue_graph(glued, debug=False):
    # Collect ungluing instructions
    cycles = nx.get_node_attributes( glued, 'glued_cycles' )
    gtargets = nx.get_edge_attributes( glued, 'glued_target' )

    if len(cycles) == 0 and len(gtargets) == 0:
        if debug: print("No cycle to unglue!")
        return glued

    if debug:
        print("Restoring %s cycles:" % len(cycles))
        for n,c in cycles.items():
            print("  * %s -> %s" % (n,c))
        print("Redirecting %s edges:" % len(gtargets))
        for e,i in gtargets.items():
            print("  * %s -> %s" % (e,i))

    G = glued.copy()
    
    # For each glued cycle, restore the inner edges
    for cur_cycle in cycles.values():
        G.add_weighted_edges_from(cur_cycle)

    # Redirect glued edge targets
    for (s,t),nt in gtargets.items():
        info = G.edges[(s,t)]
        G.remove_edge(s,t)
        G.add_edge(s, nt, **info)

    return G


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

#TODO : add a layout 'saved' that can be used to get the same node position between the input graph and the reduced graph.
#TODO : when splines=true will be taken into account, add it in args.

def plot_graph(G, layout='dot', saveLayout=False, notebook=True):
    format='png'
    path=None
    AG = nx.nx_agraph.to_agraph(G)
    LE = AG.edges()
    for a,b in LE:
        AG.remove_edge(u=a,v=b)
    for c,d,w in G.edges(data=True):
        AG.add_edge(u=c,v=d, label=w['weight'])
    AG.layout(layout,args="-Nheight=0.3 -Nwidth=0.3")
    if notebook:
        return img(AG.draw(path=path,format=format,args="-Nheight=0.3 -Nwidth=0.3 -Gnodesep=0.5 -Goverlap=false"))
    else:
        AGdraw = AG.draw(path=path,format=format,args="-Nheight=0.3 -Nwidth=0.3 -Gnodesep=0.5 -Goverlap=scale")
        AGdraw_io = io.BytesIO(AGdraw)
        return Image.open(AGdraw_io)

def save_plot_graph(G, path, format, layout='dot', saveLayout=False):
    AG = nx.nx_agraph.to_agraph(G)
    LE = AG.edges()
    for a,b in LE:
        AG.remove_edge(u=a,v=b)
    for c,d,w in G.edges(data=True):
        AG.add_edge(u=c,v=d, label=w['weight'])
    AG.layout(layout,args="-Nheight=0.3 -Nwidth=0.3")
    return AG.draw(path=path,format=format,args="-Nheight=0.3 -Nwidth=0.3 -Gnodesep=0.5 -Goverlap=scale")

def permute_timescales(G):
    edge_labels = nx.get_edge_attributes(G, 'weight')
    vals = list(edge_labels.values())
    perm = np.random.permutation(len(vals))
    for i,e in enumerate(edge_labels):
        edge_labels[e] = vals[perm[i]]
    nx.set_edge_attributes(G, edge_labels, 'weight')

def check_unique(edges, best, debug=False):
    count = 0
    for v in edges:
        if v[2] == best:
            if count:
                if debug:
                    print("Duplicated best edge")
                raise DuplicateMinError((best,edges))
            count += 1

class DuplicateMinError(Exception):
    def __init__(self, info):
        self.info = info


