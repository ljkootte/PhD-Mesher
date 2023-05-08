# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 09:31:25 2019

@author: ljkootte
"""
import sys
import os


inpName = sys.argv[-1]
os.chdir(''.join(inpName.split('\\')[:-1]))

Name = inpName.split('\\')[-1]
ModelName = Name.strip('.inp')
if len(ModelName)>38: ModelName = ModelName[-38:]
mdb.ModelFromInputFile(name=ModelName,inputFileName=Name)
a = mdb.models[ModelName].rootAssembly
myViewport = session.viewports['Viewport: 1']
myViewport.setValues(displayedObject=a)
del mdb.models['Model-1']
myViewport.assemblyDisplay.setValues(optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
myViewport.view.rotate(xAngle=90,yAngle=90,zAngle=0)
myViewport.view.rotate(xAngle=90,yAngle=90,zAngle=0)
myViewport.view.rotate(xAngle=0, yAngle=0, zAngle=180)
myViewport.view.setValues(projection=PARALLEL)
