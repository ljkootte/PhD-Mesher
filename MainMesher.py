# -*- coding: utf-8 -*-
"""
@author: L.J. Kootte
@email: luckootte@gmail.com
Developed for the PhD Thesis at TUDelft supervised by Prof.dr. C. Bisagni and Prof.dr. C. Kassapoglou
"""

from InputVariables import *
from Writer import WriteLayup,WriteMaterials,WriteSupsFile
from CreateElements import WriteNdEl
from Supports import WriteSupports,WritePanelClamp,WriteTestClamp
import os
import pandas as pd
import time

global enter
enter = lambda a: [file.write('**\n') for i in range(a)]

Direc = f'{Shape}_SkL{int(sk_L)}_SkW{int(sk_W)}'
if MPB=='4PB': Direc+= f'_Sx{Sup_X}_Sy{Sup_Y}'
elif MPB=='7PB': Direc+= f'_Sy{Sup_Y}_Ly{Load_Y}'
elif MPB=='MMB':  Direc +=f'_MM{int(MM*100):d}_{int(c)}c'
if Coh: Direc+='_'+Coh_mat
if superpose: Direc+='-'+Coh_Tri



Direc +=input(f'Name here: {MPB}-{Direc}')
Direc = Direc.replace('.','x')
print(MPB+'-'+Direc)


if not os.path.exists(MPB+'-'+Direc): os.makedirs(MPB+'-'+Direc)

t0 = time.time()
tot_Df_Nd ,Df_El,Df_El_loc,El_ID0,Nd_ID0 = WriteNdEl(MPB+'-'+Direc+"\{}-MESH-{}.inp".format(MPB,Direc))
t1 = time.time()

IndID=None

print ('Mesh written in {:.2f} seconds'.format(t1-t0))
if MPB=='SSCS' or MPB=='FSP': WritePanelClamp(MPB+'-'+Direc+"\{}-SUPPORTS-{}.inp".format(MPB,Direc),tot_Df_Nd)
elif MPB=='Test': WriteTestClamp(MPB+'-'+Direc+"\{}-SUPPORTS-{}.inp".format(MPB,Direc),tot_Df_Nd)
else: El_ID0,Nd_ID0,IndID = WriteSupports(MPB+'-'+Direc+"\{}-SUPPORTS-{}.inp".format(MPB,Direc),Df_El_loc,El_ID0,tot_Df_Nd,Nd_ID0) # Write Supports

print ('Supports written')

with open('{0}-{1}/{0}-{1}.inp'.format(MPB,Direc), "w") as file:
    file.write('*Include, input = {}-MESH-{}.inp\n'.format(MPB,Direc))
    file.write('*Include, input = {}-SUPPORTS-{}.inp\n'.format(MPB,Direc))
    enter(2) 
    WriteLayup(file,tot_Df_Nd.keys())
    enter(2)
    WriteMaterials(file,tot_Df_Nd.keys())
    enter(1)
    WriteSupsFile(file,IndID)
    enter(2)
print ('End')
n_Nodes = sum([len(tot_Df_Nd[key]) for key in tot_Df_Nd.keys()])
n_Elements = sum([len(Df_El[key]) for key in Df_El.keys()])
print(f'Nodes: {n_Nodes}')
print(f'Elements: {n_Elements}')

if input('open Abaqus? (y/n):')=='y':
    os.popen('abaqus cae script=OpenAbaqus.py -- {0}-{1}\{0}-{1}.inp'.format(MPB,Direc))




