from . import reduction
from . import simulation
from . import gui
import sys

# Re-export the main functions

load_graph = reduction.load
reduce_graph = reduction.reduce_graph
save_graph = reduction.save_graph
plot_graph = reduction.plot_graph
save_plot_graph = reduction.save_plot_graph

simulate = simulation.simulate
simulate_and_plot = simulation.simulate_and_plot


def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    if len(argv) > 1:
        print("TODO: Add a command-line interface to reduce and simulate")
        return

    gui.launch_gui()

