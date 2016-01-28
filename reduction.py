
import csv
import re
import networkx as nx

#################################### Extra ####################################
##Find the primitive cycles (not vertex-containing any proper subcycle) 
##of a digraph G
#def primitive_cycles( G ):
#   cycle_list = list( nx.simple_cycles(G) )
#   for c in cycle_list:
#      d_list = [d for d in cycle_list if d != c]
#      for d in d_list:
#         if set(d).issubset(c):
#            cycle_list = d_list
#   return cycle_list


############################### Functions #####################################
#Returns the input digraph G from a csv file given as a string-type argument
def create_graph( input_file ):
    #copying line by line the content of the csv file into a list of weighted
    #arcs, given that each live of the csv file encodes an arc
    with open( input_file, 'rb' ) as csvfile:
        csvreader = csv.reader(csvfile)
        #take out the first line of the csv file, which is considered as metadata
        next(csvreader)
        arc_list = []
        for row in csvreader:
   	        for elem in row:
			    arc_list.append( map( int, re.findall( '\d+', elem ) ) )
    #creates and returns a digraph G out of the list of weighted arcs
    G = nx.DiGraph()
    for arc in arc_list:
	    G.add_weighted_edges_from(arc_list)
    return G
	
#Given a digraph G, returns a pruned version of it according to rule a, 
#i.e. where at every node remains none but the fastest out-going edge 
def prune_rule_a( G ):
    #construct the list of the fastest out-edge from each node
    fastest_edge_list = []
    for node in G.nodes():
        fastest = min( G.out_edges( node, data='weight' ), key=lambda x:x[2] )
        fastest_edge_list.append( fastest )
    #creates and returns the pruned graph out of the list of the fastest edges
    pruned_G = nx.DiGraph()
    pruned_G.add_weighted_edges_from( fastest_edge_list )
    return pruned_G

def prune_rule_b( G ):
    slow_cycles_list = []
    cycles_list = nx.simple_cycles(G)
    for cycle in cycles_list:
        H = G.subgraph(cycle)
        print "H is"
        print H.nodes()
        print H.edges(data='weight')


#Given a digraph G and one of its elementary cycle, returns a digraph
#for which the cycle is glued 
def glue_cycle( G, cycle ):
    #find the limiting step of the cycle
    H = G.subgraph(cycle)
    limit_step = max( H.edges(data='weight'), key=lambda x:x[2] )
    #creates the list of edges to add to the glued graph
   
    #creates the glued_graph 
    glued_G = G.copy()
    glued_G.remove_nodes_from( cycle )
   
    glued_G.add_weighted_edges_from()
    return glued_graph    

############################### Main ##########################################
#Print the input digraph G
G = create_graph('input.csv')
print G.edges(data='weight')		

#Print the pruned graph
print "rule a: pruned G is"
pruned_G = prune_rule_a(G)
print pruned_G.edges(data='weight')

#Print the second pruned graph
print "rule b: pruned G is"
prune_rule_b(G)
