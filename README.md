# PhD-Mesher
This mesher is created by Luc Kootte for his dissertation which can be found at:
Some background information can be found in chapter 2, Methodology.

Use
-------------
Download and unzip the files on your computer.
The model design is defined in the file: InputVariables.py (The current variables correspond to the ones used within the thesis.)
After the variables are defined, run the MainMesher.py.
This will create three Abaqus input files. One defines the mesh, one the supports, the last one imports the two and defines the properties and the step.
It is then asked if you would like to open it directly in Abaqus to view the models.

The three input files should be kept together. To submit the model simply use: abaqus job=<main-InputFileName>
  
Citing this Python Mesher
---------------------------------------

We kindly ask you to cite this Python library properly.
Also, it would be helpful if you could cite the dissertation where this methods has been applied as well.

<to be added>
  



