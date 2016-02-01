
import csv
import re
import networkx as nx

############################### Creating the graph ############################
#Reads the content of the csv file given as a string-type argument,
#then copy it line by line into a list of weighted arcs,
#given that each line of the csv file encodes an arc
def arc_list_from_csv( input_file ):
    with open( input_file, 'rb' ) as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader) #take out the first line of the csv, which is metadata
        arc_list = []
        for row in csvreader:
   	    for elem in row:
	        arc_list.append( map( int, re.findall( '\d+', elem ) ) )
    return arc_list

#Returns a weighted digraph out of a list of weighted arcs
def graph_from_arc_list( arc_list ):
    G = nx.DiGraph()
    for arc in arc_list:
        G.add_weighted_edges_from(arc_list)
    return G

############################### Pruning the graph #############################
#Given a digraph G, returns a pruned version of it, i.e. where at every node 
#remains none but the fastest out-going edge 
def prune( G ):
    #construct the list of the fastest out-edge from each node
    fastest_edge_list = []
    for node in G.nodes():
        fastest = min( G.out_edges( node, data='weight' ), key=lambda x:x[2] )
        fastest_edge_list.append( fastest )
    #creates and returns the pruned graph out of the list of the fastest edges
    pruned_G = nx.DiGraph()
    pruned_G.add_weighted_edges_from( fastest_edge_list )
    return pruned_G

############################### Gluing the graph ##############################
#Returns the list of edges going out from a cycle of the pruned graph
def cycle_out_edges( G, cycle, cycle_edges ):
    J = G.copy()
    J.remove_edges_from(cycle_edges)
    G_minus_cycle = G.copy()
    G_minus_cycle.remove_nodes_from(cycle)
    J.remove_edges_from ( G_minus_cycle.edges(data='weight') ) 
    return [ e for e in J.edges(data='weight') if e[0] in cycle ]

#Returns the list of edges going into a cycle of the pruned graph
def cycle_in_edges( G, cycle, cycle_edges ):
    J = G.copy()
    J.remove_edges_from(cycle_edges)
    G_minus_cycle = G.copy()
    G_minus_cycle.remove_nodes_from(cycle)
    J.remove_edges_from ( G_minus_cycle.edges(data='weight') ) 
    return [ e for e in J.edges(data='weight') if e[0] not in cycle ]

#Restores every edge going out of the cycles of the pruned graph
def restore_cycles_out_edges( G, pruned_G ):
    restored_G = pruned_G.copy()
    for cycle in nx.simple_cycles(pruned_G):
        H = G.subgraph(cycle)
        out_edges = cycle_out_edges( G, cycle, H.edges(data='weight') )
        restored_G.add_weighted_edges_from(out_edges)
    return restored_G
    
#Given a list and a value, selects from it a sublist for which
#the first coordinate of its elements matches the value, 
#then returns the first element of the sublist
def sel( list_l, value ):
    L = [ e for e in list_l if e[0] == value ]
    return L[0]

#Returns a renormalization of the weights of the out edges of a cycle,
#with respect to the restored graph, and connects them to the origin 
#of the limiting step.
def renorm_out_edges( cycle_edges, out_edges, value ):
    k = 0
    for e in cycle_edges:
        k = k + 1.0/e[2]
    cycle_cst = 1 / k
    out_edge_origin = [ e[0] for e in out_edges ]
    l = [ e for e in cycle_edges if e[0] in out_edge_origin ] 
    l_norm = map( lambda x:(x[0], x[1], cycle_cst/x[2]), l )
    return map( lambda x:(value, x[1], sel(l_norm,x[0])[2] * x[2]), out_edges )
    
#Connects the in edges of a cycle to a new vertex
def redirect_in_edges( in_edges, new_vertex ):
    return map( lambda x:(x[0],new_vertex,x[2]), in_edges )

#Given G and one of its cycle, returns a graph for which the cycle is glued,
#i.e. supressed and replaced by a new vertex whose label will be this of
#the limiting step (origin)
def glue_cycle( pruned_G, restored_G, cycle ):
    #creates the in and out lists of edges of the given pruned graph's cycle
    H = pruned_G.subgraph(cycle)
    cycle_edges = H.edges(data='weight')
    out_list = cycle_out_edges( restored_G, cycle, cycle_edges )
    in_list = cycle_in_edges( restored_G, cycle, cycle_edges )
    #with the limiting step, renormalize the out edges 
    #and redirect the in edges
    lim_step = max( cycle_edges, key=lambda x:x[2] )
    out_edges = renorm_out_edges( cycle_edges, out_list, lim_step[0] )
    in_edges = redirect_in_edges( in_list, lim_step[0] )
    #creates the glued graph by taking the restored graph and replacing
    #the vertices of the pruned graph's cycle by a new vertex, named
    #after the vertex at the origin of its limiting step, then
    #adding its renormalized out edges together with the redirected in edges
    glued_G = restored_G.copy()
    glued_G.remove_nodes_from(cycle)
    glued_G.add_node(lim_step[0])
    glued_G.add_weighted_edges_from(out_edges)
    glued_G.add_weighted_edges_from(in_edges)
    return glued_G
  
#Returns the glued graph obtained by gluing every cycle of the pruned graph  
def glue_graph( pruned_G, restored_G ):
    glued_G = restored_G.copy()
    for cycle in list( nx.simple_cycles(pruned_G) ):
        glued_G = glue_cycle( pruned_G, glued_G, cycle )
    return glued_G

############################### Main ##########################################
#Print the input digraph G
arc_list = arc_list_from_csv('input.csv')
G = graph_from_arc_list( arc_list )
print "Input graph is"
print G.edges(data='weight')

pruned_G = prune(G)
print "Pruned graph is"
print pruned_G.edges(data='weight')

restored_G = restore_cycles_out_edges( G, pruned_G )
print "Restored graph is"
print restored_G.edges(data='weight')

glued_G = glue_graph( pruned_G, restored_G )
print "Glued_graph is"
print glued_G.edges(data='weight')
           
    
    
    
    
    
    
