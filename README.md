# LNetReduce: simplification of linear dynamic networks

Dynamic networks, represented as digraphs labeled by integer timescale orders, can describe deterministic or stochastic 
monomolecular chemical reaction networks but also random walks on weighted protein-protein interaction networks,
spreading of infectious diseases and opinion in social networks, communication in computer networks.

This tool uses graph and label rewriting rules (pruning edges, pooling and restoring cycles) to compute reduced versions of these network
which reproduces the full network dynamics with good approximation at all time scales.

Full reduction is possible when edge weight enable timescale separation for the pruning (unique minimum label at bifurcations) and pooling (unique limiting step in cycles) rules.  
Eigenvalues and eigenvectors can be computed for fully reduced models and can then be used to compute the model dynamics.

When timescale separation conditions are not fully satisfied, partial reduction may still be possible. All the glued cycles are restored in partially reduced networks. 


## Input and output files

The model is presented as a CSV table with three columns: "source" "target" "weight".
The (partially) reduced model can be saved using the same format as the input model.
* The weights must be positive integers or zero; if this is not the case, substract the lowest label from all the labels.
* The source and target nodes can be symbols (e.g. ```A;B:1``` means that the model contains an edge ```(A,B)``` of rate constant ```epsilon^1```). 
* By default epsilon = 1/10, and can not be changed in this version.



## Simulation 

* Both full and reduced models can be simulated. 
* Chose a positive integer for the timescale, e.g. timescale = 1 if you want to simulate between 0 and 10^1.
* By default, the initial conditions are one for all nodes; changing the default will be possible in future versions  
* The solution is plotted in semi-logarithmic scale starting with t=10^0.
* The code uses stiff solvers but these may fail for very stiff unreduced models; reduced models are less stiff and should pose no problems. 
* The reduced model has multi-scale validity, i.e. the solutions computed with the reduced model approximate those computed with the full model at all time scales.



## Test online

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/oradules/lnetreduce/HEAD)


## Installation

### Using conda

First install and setup a conda distribution: if you don't already have one.
See instructions on the [miniconda website](https://conda.io/miniconda).

Then create an environment for LNetreduce with all required dependencies by running the 
following command in the LNetReduce folder: ```conda env create -f environment. yml```.

### Using pip

After installing pip enter the the following command line to install all the needed packages:

```pip install --user networkx numpy scipy matplotlib ipython jupyter pandas sympy nose matplotlib```


### Manual installation on Windows

1. Install Python 
    
    1. Follow this [guide](https://docs.python.org/3/using/windows.html) with the following steps

        1. Download Python [here](https://www.python.org/downloads/)
        2. Choose "customize installation" and if you don't already have Python in your PATH, check "add Python X.X to PATH". Then choose a directory for your Python installation, it is recommended to intall it in a root to **avoid space in the path directory**. Make sure that the pip installation is checked. Check "Enable Win32 long paths".
        3. Right clic on your Python directory, go to property/security, and check that you have (at least in admin) writing and modification rights to be sure that new packages will be intalled in ./Lib/site-packages

2. Install Graphviz

    1. Download Graphviz [here](https://graphviz.org/download/) (if you are not sure about the version choose *X.XX.X EXE installer for Windows 10 (64-bit)*)
    2. Make sure you have gcc installed, else you can install it [here](https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/) *(note: if you have MinGW or visual studio installed on your computer, you should already have a C/C++ compiler)*
    3. Install Graphviz, it is recommended to intall it in a root to **avoid space in the path directory**

3. Install [nextworkx](https://networkx.org/documentation/stable/install.html) and [pygraphviz](https://pygraphviz.github.io/documentation/stable/install.html)

    1. Open a powershell (shift+right-clic on a window, or write powershell in your search space), then write **pip install numpy scipy pandas matplotlib networkx**
    2. Then, write **pip install --global-option=build_ext --global-option="-IC:\Graphviz\include" --global-option="-LC:\Graphviz\lib" pygraphviz** if **C:\\** is the root where you have installed Graphviz.

4. Install LNetReduce

    1. Download the zip file and extract it where you want.

## Usage

run ```python -m lnetreduce``` to launch the graphical interface.

A Python API is also available, see the included jupyter-notebooks for examples.

## Reference

Marion Buffard, Aurélien Desoeuvres, Aurélien Naldi, Clément Requilé, Andrei Zinovyev, Ovidiu Radulescu.
[LNetReduce: tool for reducing linear dynamic networks with separated time scales.](https://doi.org/10.1101/2021.05.11.443578)
bioRxiv 2021.05.11.443578; doi:10.1101/2021.05.11.443578

