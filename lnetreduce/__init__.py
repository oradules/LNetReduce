from . import reduction
from . import simulation

# Re-export the main functions

load_graph = reduction.load
reduce_graph = reduction.reduce_graph
save_graph = reduction.save_graph

simulate = simulation.simulate
simulate_and_plot = simulation.simulate_and_plot

