# LNetReduce: reduction of monomolecular networks

## Test online

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/oradules/lnetreduce/HEAD)


## Installation

Windows:

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

    1. Open a powershell (shift+right-clic on a window, or write powershell in your search space), then write **pip install numpy scipy pandas matplotlib**
    2. Then, write **pip install --global-option=build_ext --global-option="-IC:\Graphviz\include" --global-option="-LC:\Graphviz\lib" pygraphviz** if **C:\\** is the root where you have installed Graphviz.

4. Install LNetReduce

    1. Download the zip file and extract it where you want.

## Usage

run ```python -m lnetreduce``` to launch the graphical interface.

A Python API is also available, see the included jupyter-notebooks for examples.

## Brief documentation 

1. Input file format

	• The model is presented as a table with three columns: "source" "target" "weight".
	• The weights must be positive integers or zero; if this is not the case, substract the lowest label from all the labels.
	• The source and target nodes can be symbols.
	• E.g. source = A0, target = A1, weight = 1 means that the model contains an edge (A0,A1) of rate constant epsilon^1. 
	• By default epsilon = 1/10, and can not be changed in this version.

2. Reduction

	• Full reduction is possible when the pruning (unique minimum label at bifurcations) and pooling (unique limiting step in cycles) conditions are 
	fulfilled.  
	• Partial reduction renders the partially reduced model at a stop step when one of the above conditions is not satisfied. All the glued cycles are 
	restored in partially reduced model. 


3. Simulation 

	• Both full and reduced models can be simulated. 
	• Chose a positive integer for the timescale, e.g. timescale = 1 if you want to simulate between 0 and 10^1. 
	• The solution is plotted in semi-logarithmic scale starting with t=10^0.
	• The code uses stiff solvers but these may fail for very stiff unreduced models; reduced models are less stiff and should pose no problems. 
	• The reduced model has multi-scale validity, i.e. the solutions computed with the reduced model approximate those computed with the full model 
	at all time scales.

4. Output files 
 
	• The (partially) reduced  model is generated using the same format as the input model. 
	• Eigenvalues and eigenvectors of the reduced models are also generated in the case of full reduction only. These can be used to compute the model dynamics.


## How to cite this tool


