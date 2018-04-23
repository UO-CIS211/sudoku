# Sudoku

A solver for the classic puzzle, as a programming 
project for CIS 211 at University of Oregon. 

The project will have two phases.  In the first phase 
we implement constraint propagation to solve simple 
puzzles.  In the second phase we will add back-tracking
search to solve harder puzzles. 

We will use a model-view-controller organization to 
associate either a graphical display or a textual 
display with the game.

## Manifest

* sudoku.py :  Driver (main program).  Command line interface; connects view component to model component, invokes solver. 
* Model component: 
	* sdk\_board.py, sdk\_group.py, sdk\_tile.py : Core data structure of a Sudoku puzzle board containing tiles, which are grouped as 9 rows, 9 columns, 9 blocks (27 groups in all). 
	* sdk_io.py : Read and print boards in a subset of the Sadman Software .sdk format.  Handles only the core format, not the additional attributes like author. 
	* sdk_solver.py : Puzzle solving algorithms.  Constraint propagation (naked single and hidden single) and, in phase 2 of the project, a back-tracking search.  
	*  events.py : Abstract base classes for event notification in MVC and other listener-based coordination.
*  View component(s): 
	*  	sdk_display.py : The main graphical display.  Shows a board with "pencil marks"  (candidate values that have not been eliminated).  Can optionally highlight groups that are being processed (slow but useful for debugging).  
	*   sdk_debugview.py : Another alternative "view", which just prints some information that may be useful in debugging. 
*  Support libraries
	*  	graphics : An enhanced version of the Zelle graphics library, which provides a simpler and more Pythonic interface to Tcl/Tk.  Built on Tkinter, whose sole virtue is shipping with Python.  Some extensions by M Young for grid-based displays. 
*  Tests: 
	*  	test\_sdk.py : Basic test suite for sdk\_tile, sdk\_board, sdk\_solver, sdk\_io.  Includes very basic test cases for constraint propagation.  Does not include test of back-tracking search. 
	*   data/* :  A variety of sample boards useful in testing and debugging. See [data/README.md](data/README.md) for descriptions. 


