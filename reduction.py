from __future__ import print_function

import sys
import csv
import networkx as nx
import numpy as np

############################### Creating the graph ############################
#Reads the content of the csv file whose name is given as a string,
#then copy it line by line into a list of weighted arcs,
#given that each line of the csv file, but the first, encodes an arc.
def arc_list_from_csv( file_name ):
    with open(file_name) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        next(csvreader) #take out the first line of the csv, which is metadata
        arc_list = []
        for row in csvreader:
            arc_list.append( map(int,row[:3]) )
    csvfile.close()
    return arc_list

#Returns a weighted digraph out of a list of weighted arcs.
def graph_from_arc_list( arc_list ):
    G = nx.DiGraph()
    G.add_weighted_edges_from(arc_list)
    return G

############################### Saving the resulting graph into a file ########
#Save a graph to a file: list of edges in the format: 'Source;Target;Weight'   
def save_graph(G, filename):
    f = open(filename, 'w')
    f.write('Source;Target;Weight\n')
    for src,target in G.edges():
        w = G.get_edge_data(src,target)['weight']
        f.write('%s;%s;%s\n' % (src, target,w))
    f.close()

############################### Pruning the graph #############################
#Given a digraph G, returns a pruned version of it, i.e. where at every node 
#remains none but the fastest out-going edge. 
def prune( G ):
    #construct the list of the fastest out-edge from each node
    fastest_edge_list = []
    for node in G.nodes():
        if G.out_edges(node) != []:
            fastest = min( G.out_edges(node,data='weight'), key=lambda x:x[2] )
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
def glue_cycle( pruned_G, restored_G, cycle ):
    #creates the in and out lists of edges of the given pruned graph's cycle
    H = pruned_G.subgraph(cycle)
    cycle_edges = H.edges(data='weight')
    out_list = cycle_out_edges( restored_G, cycle, cycle_edges )
    in_list = cycle_in_edges( restored_G, cycle, cycle_edges )
    #with the limiting step, renormalize the out edges 
    #and redirect the in edges
    lim_step = max( cycle_edges, key=lambda x:x[2] )
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
def glue_graph( pruned_G, restored_G ):
    glued_G = restored_G.copy()
    cycles_list = list( nx.simple_cycles(pruned_G) )
    for cycle in cycles_list:
        glued_G = glue_cycle( pruned_G, glued_G, cycle )
    return glued_G

#Compute the pruned graph of G then restore the out edges of its cycles,
#then glue its cycles over and over again, until the resulting graph has no
#simple cycle. Then returns the list composed of the original graph pruned
#together with all its successive glued graphs (but not pruned).
def glue( G ):
    L = []
    i = 0
    L.append(G)
    while list( nx.simple_cycles( prune(L[i]) ) ) != []:
        i += 1
        pruned_i = prune( L[i-1] )
        restored_i = restore_cycles_out_edges( L[i-1], pruned_i )
        L.append( glue_graph( pruned_i, restored_i ) )
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
def unglue_stack( stack ):
    prev = stack.pop()
    G = prev.copy()
    while stack:
        cycles = nx.get_node_attributes( prev, 'cycle' )
        incomings = nx.get_node_attributes( prev, 'glued_in' )
        outgoings = nx.get_node_attributes( prev, 'glued_out' )
        L = glued_nodes_list(prev)
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
            lim_node = lim_step[0]
            added_edges += [ e for e in cycle_edges if e != lim_step ]
            
            print('    %s (lim:%s)  ' % (i, lim_node), added_edges)
            
            # Keep the current outgoing edges (going out of the limiting node)
            # only if they do not go toward another glued cycle (avoiding duplicating it)
            cur_outgoing = [ e for e in cur_outgoing if e[1] not in L ]
            if i == lim_node:
                added_edges += cur_outgoing
            else: # should not happen: the cylce is glued on the limiting node
                print( 'REDIRECT OUTGOING' )
                for edge in cur_outgoing:
                    added_edges.append( (lim_node, edge[1], edge[2]) )
            
            # Restore incoming arcs: merge current and before gluing information
            print('    Restore incoming edges', cur_incoming, cycle_incoming)
            for e in cur_incoming:
                cur_s, cur_t, cur_w = e
                cur_w = cur_w['weight']
                for glued_s, glued_t, glued_w in cycle_incoming:
                    if glued_s == cur_s and glued_w == cur_w:
                        # FIXME: if the source is part of a glued cycle, it may be wrong
                        # in this case it should be safe to use cur_s instead of glued_s
                        # (requires updating the surrounding if and performing some extra tests)
                        added_edges.append( (cur_s, glued_t, glued_w) )
                        break
        
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
    M = np.zeros( (G.size(),G.order()), int )
    i = 0
    for e in G.edges(data='weight'):
        M[i][e[0]] = 1
        v = G.get_edge_data(*e)
        dfs = list( nx.edge_dfs(G,e) )
        L = [f for f in dfs if G.get_edge_data(*f) > v]
        if L != []:
            M[i][L[0][0]] = -1
        else:
            M[i][dfs[-1][1]] = -1
        i += 1
    return M

#The right vectors of a reduced digraph are here given in the form of a matrix,
#where the lines are the edges of the graph and the columns the veritces.
#Now, for each edge, put a one into the column indexed by its origin node, then
#via a reversed depth-first searched, find the first predecessor edge in the
#graph whose weight is strictly bigger (i.e. slower reaction speed). Then put a
#one at the column indexed by the origin node of this latter edge.
def left_vector( G ):
    M = np.zeros( (G.size(),G.order()), int )
    i = 0
    for e in G.edges(data='weight'):
        M[i][e[0]] = 1
        v = G.get_edge_data(*e)
        H = G.reverse()
        dfs = list( nx.edge_dfs(H,e[0]) )
        if dfs != []:
            for f in dfs:
                if H.get_edge_data(*f) < v:
                    M[i][f[1]] = 1
                else:
                    break
        i += 1
    return M

def show_graph(G, label=False):
    if label: print(label)
    print(G.nodes())
    for s,t,w in G.edges(data='weight'):
        print( s,t,w )
    print()

############################# Main ############################################

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print( 'usage:' )
        print( sys.argv[0] + ' <filename>' )
        sys.exit()
    filename = sys.argv[1]
    #input digraph
    arc_list = arc_list_from_csv(filename)
    input_G = graph_from_arc_list(arc_list)
    #final glued graph
    L = glue(input_G)
    print('Glued stack:')
    i = 0
    for curG in L:
        show_graph(curG, 'Step %s' % i)
        i += 1
    print()
    
    n = len(L)-1
    glued_G = L[n]
    #final unglued graph
    u_G = unglue_stack(L)
    #save u_G into file
    if validity_check(u_G):
        save_graph( u_G, '%s_reduced.tsv' % filename)
        R = right_vector(u_G)
        L = left_vector(u_G)
        print( L )
    else:
        print( "Sorry, this instance is not reducible because its reduced \
             form has non separated reaction speeds" )

