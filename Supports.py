# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 14:08:53 2018

@author: luuki
"""
import os
from InputVariables import *
import pandas as pd
import numpy as np
from CohTie import WriteSet
#from CreateElements import MeshgridSolid,WriteNative,CreateElements,CreateGrid,CreateNodeDf
import matplotlib.pyplot as plt
from collections import defaultdict

def DefMPB(Parts):
    global Z_str
    Z_bot = 0 ; Z_top = Thickness['Skin']
    Z_str = sum(Thickness.values())

    if MPB == '7PB':
        IndID =  np.array([
             ['Supports',sk_L/2,       sk_W/2,       Z_bot, 1],\
             ['Loads', sk_L/2,          Load_Y,      Z_top,-1],\
             ['Loads', sk_L/2,          sk_W-Load_Y, Z_top,-1],\
             ['Supports',Sup_X,      Sup_Y,          Z_bot, 1],\
             ['Supports',sk_L-Sup_X, Sup_Y,          Z_bot, 1],\
             ['Supports',sk_L-Sup_X, sk_W-Sup_Y,     Z_bot, 1],\
             ['Supports',Sup_X,      sk_W-Sup_Y,     Z_bot, 1]])      

    elif MPB == '6PB':
        IndID =  np.array([
             ['Loads', sk_L/2,          Load_Y,      Z_top,-1],\
             ['Loads', sk_L/2,          sk_W-Load_Y, Z_top,-1],\
             ['Supports',Sup_X,      Sup_Y,          Z_bot, 1],\
             ['Supports',sk_L-Sup_X, Sup_Y,          Z_bot, 1],\
             ['Supports',sk_L-Sup_X, sk_W-Sup_Y,     Z_bot, 1],\
             ['Supports',Sup_X,      sk_W-Sup_Y,     Z_bot, 1]])      
        
    elif MPB=='4PB' and (Shape=='Doubler' or Shape=='Coupon') :
        IndID =  np.array([
             ['Supports',Sup_X,       Sup_Y,          Z_bot,  1],\
             ['Loads',         Sup_X if Shape=='Coupon' else Sup_X2,  sk_W-Sup_Y if Shape=='Coupon' else Sup_Y2,  Z_str, -1],\
             ['Supports',sk_L-(Sup_X if Shape=='Coupon' else Sup_X2), sk_W-Sup_Y if Shape=='Coupon' else Sup_Y2,  Z_bot,  1],\
             ['Loads',sk_L-Sup_X,     Sup_Y,          Z_top if Shape=='Doubler' else Z_str, -1]])

    elif MPB == '4PB':
        IndID =  np.array([
             ['Supports',Sup_X,      Sup_Y,         Z_bot,  1],\
             ['Supports',sk_L-Sup_X, sk_W-Sup_Y,    Z_bot,  1],\
             ['Loads',sk_L-Sup_X,    Sup_Y,      Z_top, -1],\
             ['Loads',Sup_X,         sk_W-Sup_Y, Z_top, -1]])


#        elif MPB == '4PB':
#            IndID =  np.array([
#                 ['Loads',Sup_X,      Sup_Y,         Z_top,  -1],\
#                 ['Loads',sk_L-Sup_X, sk_W-Sup_Y,    Z_top,  -1],\
#                 ['Supports',sk_L-Sup_X,    Sup_Y,      Z_bot, 1],\
#                 ['Supports',Sup_X,         sk_W-Sup_Y, Z_bot, 1]])

    elif MPB == '3PB':
        IndID =  np.array([
             ['Supports',R_top,       Sup_Y, Z_top if (Shape=='Doubler' or Shape=='Hat') else Z_str, -1],\
             ['Loads',   R_bot,      sk_W/2-0.5,    Z_bot,  1],\
             ['Supports',R_top,  sk_W-Sup_Y, Z_top if (Shape=='Doubler' or Shape=='Hat') else Z_str, -1]])

    elif MPB == 'DCB':
        IndID =  np.array([
             ['Loads',      sk_L/2,  0, 2*Thickness['Skin'], -1],\
             ['Supports',   sk_L/2,  0,    0,  1]])

    elif MPB == 'MMB':
        IndID =  np.array([
             ['Tie',      sk_L/2,  0, Z_str, -1],\
             ['Tie',      sk_L/2,  0,    0,  1],\
             ['Surf',      R_circ,  MMB_Yup, Z_str, -1],\
             ['Surf',   R_circ,  MMB_Ydown,    0,  1],\
             ['Loads',   sk_L/2,  MMB_Yup+c ,    10+Z_str,  1]])


    
    
    index = pd.MultiIndex.from_tuples(list(zip(*[list(IndID[:,0]),list(range(len(IndID[:,0])))])), names=['Set', 'ID']) 
    IndID = pd.DataFrame(data =IndID[:,1:] ,index = index,columns = ['X','Y','Z','O'],dtype = np.float32)
    Xoff = 0 #mm
    Yoff = 0 #mm
    Rot  = 0/180*np.pi #deg
    
    if Xoff!=0: IndID['X'] += Xoff
    if Yoff!=0: IndID['Y'] += Yoff
    if Rot!=0: 
        Cent_Rot    = [(max(IndID.loc['Supports']['X'])+min(IndID.loc['Supports']['X']))/2,(max(IndID.loc['Supports']['Y'])+min(IndID.loc['Supports']['Y']))/2]
        Ang    = np.arctan2(IndID['X']-Cent_Rot[0],IndID['Y']-Cent_Rot[1])
        R      = ((IndID['X']-Cent_Rot[0])**2+(IndID['Y']-Cent_Rot[1])**2)**0.5
        Ang    += Rot
        IndID['X'] =  np.sin(Ang)*R+Cent_Rot[0]
        IndID['Y'] =  np.cos(Ang)*R+Cent_Rot[1]
    return IndID



def WriteSupports(inputfile,Df_El_loc,El_ID0,tot_Df_Nd,Nd_ID0):
    with open(inputfile, "w") as file:
        IndID = DefMPB(Df_El_loc.keys())
        if MPB == 'DCB' or MPB=='MMB':
            ClampDCB(file,tot_Df_Nd,IndID,Df_El_loc)
            if Shape=='Coupon' and sk_L <= 2:
                Mid_Nd =[]
                for i,Part in enumerate(tot_Df_Nd):
                    Mid_Nd += tot_Df_Nd[Part].index.tolist()
                file.write('*NSET, NSET = R{0}\n'.format('Symm'))
                WriteSet(file,np.array(Mid_Nd))
        else:            
            CreateSupports(file,IndID)
            CreateSurfaces(file,IndID,Df_El_loc)
            if MPB=='3PB': LockCenter(file,tot_Df_Nd)
            SupportContact(file,IndID)
    return El_ID0,Nd_ID0,IndID
        
def DrawIndSurface(file,IndID,key):
    Ind = IndID.loc[key]
    file.write('*Surface, type = REVOLUTION, name = Indenter{}'.format(key[1])+'\n')
    file.write('{0:8.3f},{1:8.3f},{2:8.3f},{0:8.3f},{1:8.3f}, {3} '.format(Ind['X'],Ind['Y'],Ind['Z'],Ind['O'])+'\n')
    file.write('START,     0.,   0.'+'\n')
    file.write('CIRCL,   {0},  {1},  0.,  {2}'.format(ind_ra*4/5,(np.cos(np.arcsin(4/5))-1)*ind_ra,-1*ind_ra)+'\n')
    file.write('LINE,    {0},  {1}'.format(ind_ra*4/5,(np.cos(np.arcsin(4/5))-1)*ind_ra-ind_L)+'\n')
    return

def DrawCircSurface(file,IndID,key):
    Ind = IndID.loc[key]
    file.write('*surface, type=CYLINDER, name=Indenter{}'.format(key[1])+'\n')
    file.write('{0:8.3f},{1:8.3f},{2:8.3f},{0:8.3f},{3:8.3f},{2:8.3f}'.format(sk_L/2,Ind['Y'],-Ind['O']*Ind['X']+Ind['Z'],Ind['Y']+Ind['X'])+'\n')
    file.write('{0:8.3f},{1:8.3f},{2:8.3f}'.format((sk_L/2+1)*Ind['O'],Ind['Y'],-Ind['O']*+Ind['X']+Ind['Z'])+'\n')
    file.write('START, {0}, 0.0'.format(Ind['X'])+'\n')
    file.write('CIRCL, 0.0, {0}'.format(-1*Ind['X'])+'\n')
    file.write('CIRCL, {0}, 0.0'.format(-1*Ind['X'])+'\n')
    return


def CreateSupports(file,IndID):
    NodeID0 = 9900001
    enter = lambda : file.write('**\n')
    file.write('** PART: Indenter\n**\n*Node\n')
    
    for i,key in enumerate(IndID.index): 
        file.write('{:10d},{:8.3f},{:8.3f},{:8.3f} '.format(NodeID0+key[1],IndID.loc[key,'X'],IndID.loc[key,'Y'],IndID.loc[key,'Z'])+'\n')
    enter()
    for i,key in enumerate(IndID.index): 
        if MPB == '3PB':  DrawCircSurface(file,IndID,key)
        else:             DrawIndSurface(file,IndID,key)
    enter()
    for i,key in enumerate(IndID.index.get_level_values('ID')): 
        file.write('*Nset, nset=R{0}'.format(key)+'\n')
        file.write(str(NodeID0+key)+'\n')
        file.write('*Rigid Body, ref node=R{0}, analytical surface=Indenter{0}'.format(key)+'\n')
        
    for i, key in enumerate(list(set(IndID.index.get_level_values('Set')))):
        file.write('*Nset, nset={}\n'.format(key))
        for j, key2 in enumerate(IndID.loc[key].index): 
            file.write(str(NodeID0+key2)+',')
        file.write('\n')        
    enter()    


def CreateSurfaces(file,IndID,Df_El_loc):
    file.write('** Indenter skin surfaces\n')
    for i,key in enumerate(IndID.index): 
        if Z_str-0.01<IndID.loc[key,'Z'] < Z_str+0.01: 
            Part ='Stringer0' ; Z = Thickness['Skin']+Thickness['Stringer']*(1-1/(2*ttt['Stringer']))
        else:  
            Part = 'Skin'    ; Z = Thickness['Skin']*((1-IndID.loc[key,'O'])/2 +IndID.loc[key,'O']*1/(2*ttt['Skin']))

        El_list = FindSurface(Df_El_loc[Part],IndID.loc[key],Z)

        file.write('*ELSET, ELSET = IND{0}_S{1:1d}\n'.format(key[1],int((3-IndID.loc[key,'O'])/2)))
        WriteSet(file,El_list)

        file.write('*Surface, type=ELEMENT, name=Ind{}'.format(key[1])+'\n')
        file.write('IND{0}_S{1:1d},S{1:1d}'.format(key[1],int((3-IndID.loc[key,'O'])/2))+'\n')


def SupportContact(file,IndID):
    for i,key in enumerate(IndID.index): 
        WriteContactPair(file,'IND{0},Indenter{0}'.format(key[1]))
    return

def WriteContactPair(file,Pair):
    file.write('*Contact Pair, interaction=SURFS, type=SURFACE TO SURFACE, no thickness, TRACKING=STATE\n')
    file.write(Pair+'\n')
    return 

def FindSurface(Df,Ind,Z):

    if MPB == '3PB' or MPB=='MMB': Xstart,Xend = 0, sk_L
    else:            Xstart,Xend = Ind['X']-Surf_sq/2, Ind['X']+Surf_sq/2
    Ystart,Yend = Ind['Y']-Surf_sq/2, Ind['Y']+Surf_sq/2
    TieEl = '(({0} <=X<= {1})  & ({2} <= Y <= {3}) & ({4}-.01)<Z<=({4}+.01))'.format(Xstart,Xend,Ystart,Yend,Z)

    return np.array(Df.query(TieEl).index.tolist())


def LockCenter(file,tot_Df_Nd):
    Center  = tot_Df_Nd['Skin'].query('({0}-0.01<=Y<={0}+0.01 & -0.01<Z<=0.01)'.format(sk_W/2))
    
    file.write('*Nset, nset=Center\n')
    WriteSet(file,np.array(Center.index.tolist()))
    file.write('*Nset, nset=CNode\n')
    file.write('{:10d}'.format(Center.index.tolist()[0])+'\n')
    return


def TieClamp(file,tot_Df_Nd,IndID,key):
    Name = 'Skin' if IndID.loc[key,'Z']==0 else 'Stringer0'
    Nodes = tot_Df_Nd[Name].query('(Y==0 & {0}-0.01<Z<{0}+0.01)'.format(IndID.loc[key,'Z']))
    file.write('*NSET, NSET={}TieNodes\n'.format(Name))
    WriteSet(file,np.array(Nodes.index.tolist()))
    file.write('*Rigid Body, ref node=R{0}, PIN NSET={1}TieNodes'.format(key[1],Name)+'\n')

def ClampDCB(file,tot_Df_Nd,IndID,Df_El_loc):
    NodeID0 = 9900001
    enter = lambda : file.write('**\n')
    file.write('** PART: Indenter\n**\n*Node\n')
    file.write('**\n')
    file.write('*Node\n')    
    
    for i,key in enumerate(IndID.index): 
        file.write('{:10d},{:8.3f},{:8.3f},{:8.3f} '.format(NodeID0+key[1],sk_L/2,IndID.loc[key,'Y'],IndID.loc[key,'Z'])+'\n')
    for i,key in enumerate(IndID.index): 
        file.write('*Nset, nset=R{}'.format(key[1])+'\n')
        file.write(str(NodeID0+key[1])+'\n')
        if key[0]=='Surf': 
            DrawCircSurface(file,IndID,key)
            file.write('*Rigid Body, ref node=R{0}, analytical surface=Indenter{0}'.format(key[1])+'\n')            
        elif (key[0]=='Tie' and MPB=='MMB') or MPB=='DCB':    
           TieClamp(file,tot_Df_Nd,IndID,key)
        elif key[0]=='Loads' and MPB=='MMB':
            file.write('*Nset, nset=MMB_Fixture\n')
            file.write(','.join(map(str,IndID.query('Z=={}'.format(Z_str)).index.get_level_values('ID')+NodeID0))+'\n')
            file.write('*Rigid Body, ref node=R{0},TIE NSET = MMB_Fixture'.format(key[1])+'\n')
            
    if MPB=='MMB': 
        CreateSurfaces(file,IndID.loc[pd.IndexSlice['Surf',:],:],Df_El_loc)
        SupportContact(file,IndID.loc[pd.IndexSlice['Surf',:],:])
    file.write('*Nset, nset=Loads\n')
    file.write(','.join(map(str,IndID.loc['Loads'].index+NodeID0))+'\n')
    file.write('*Nset, nset=Supports\n')
    if MPB=='DCB': file.write(','.join(map(str,IndID.loc['Supports'].index+NodeID0))+'\n')
    elif MPB=='MMB': file.write(','.join(map(str,IndID.query('Z==0').index.get_level_values('ID')+NodeID0))+'\n')
            
    enter()

def WritePanelClamp(inputfile,tot_Df_Nd):

    NRefs =  pd.DataFrame(data =  [[sk_L+50,sk_W/2,0],[-50,sk_W/2,0]],index = ['Loads','Supports'], columns =['X','Y','Z'])
    
    enter = lambda : file.write('**\n')
    
    with open(inputfile, "w") as file:
        WritePanelTieNd(file,tot_Df_Nd)
        NodeID0 = 9900001    
        enter()
        file.write('** PART: Indenter\n**\n*Node\n')#** PART: Indenter\n**\n*System\n*Node\n'
        for i,TB in enumerate(NRefs.index): 
            file.write('{:10d},{:8.3f},{:8.3f},{:8.3f} '.format(NodeID0+i,NRefs.loc[TB,'X'],NRefs.loc[TB,'Y'],NRefs.loc[TB,'Z'])+'\n')
        for i,TB in enumerate(NRefs.index): 
            file.write('*Nset, nset={}'.format(TB)+'\n')
            file.write(str(NodeID0+i)+'\n')
        for i,TB in enumerate(NRefs.index):  
            file.write('*Rigid Body, ref node={0}, tie nset=R{0}'.format(TB)+'\n')

    return

def WritePanelTieNd(file,tot_Df_Nd):
    enter = lambda a: [file.write('**\n') for i in range(a)]

    Top_Nd = [] ; Bot_Nd = []; Mid_Nd =[]
    for i,Part in enumerate(tot_Df_Nd):
        Bot_Nd += tot_Df_Nd[Part].query('X==0').index.tolist()
        Top_Nd += tot_Df_Nd[Part].query('X=={}'.format(sk_L)).index.tolist()
            
    file.write('*NSET, NSET = R{0}\n'.format('Loads'))
    WriteSet(file,np.array(Top_Nd))
    file.write('*NSET, NSET = R{0}\n'.format('Supports'))
    WriteSet(file,np.array(Bot_Nd))
    return


def WriteTestClamp(inputfile,tot_Df_Nd):
    NRefs =  pd.DataFrame(data =  [[sk_L/4,0,0],[sk_L/4,sk_W/2,0]],index = ['Loads','Supports'], columns =['X','Y','Z'])
    
    enter = lambda : file.write('**\n')
    
    with open(inputfile, "w") as file:
        WriteTestTieNd(file,tot_Df_Nd)
        NodeID0 = 9900001    
        enter()
        file.write('** PART: Indenter\n**\n*Node\n')#** PART: Indenter\n**\n*System\n*Node\n'
        for i,TB in enumerate(NRefs.index): 
            file.write('{:10d},{:8.3f},{:8.3f},{:8.3f} '.format(NodeID0+i,NRefs.loc[TB,'X'],NRefs.loc[TB,'Y'],NRefs.loc[TB,'Z'])+'\n')
        for i,TB in enumerate(NRefs.index): 
            file.write('*Nset, nset={}'.format(TB)+'\n')
            file.write(str(NodeID0+i)+'\n')
        for i,TB in enumerate(NRefs.index):  
            file.write('*Rigid Body, ref node={0}, tie nset=R{0}'.format(TB)+'\n')
    return

def WriteTestTieNd(file,tot_Df_Nd):
    enter = lambda a: [file.write('**\n') for i in range(a)]

    Top_Nd = [] ; Bot_Nd = []; Mid_Nd =[]
    for i,Part in enumerate(tot_Df_Nd):
        Top_Nd += tot_Df_Nd[Part].query('Y==0 & Z==0').index.tolist()
        Bot_Nd += tot_Df_Nd[Part].query('Y=={}'.format(sk_W/2)).index.tolist()
        Mid_Nd += tot_Df_Nd[Part].index.tolist()

    file.write('*NSET, NSET = R{0}\n'.format('Loads'))
    WriteSet(file,np.array(Top_Nd))
    file.write('*NSET, NSET = R{0}\n'.format('Supports'))
    WriteSet(file,np.array(Bot_Nd))
    file.write('*NSET, NSET = R{0}\n'.format('Symm'))
    WriteSet(file,np.array(Mid_Nd))
    return


