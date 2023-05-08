# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 13:26:28 2018

@author: luuki
"""
from StringerMesher import StringerMesher
from SkinMesher     import SkinMesher
from CohTie         import WriteTieEl,WriteCoh,WriteSet,CreateDelam
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from InputVariables import *
from Supports import DefMPB
import string


def MeshgridSolid(lib_Mesh,Part,Nd_ID0,El_ID0):
    Part_Mesh = lib_Mesh[Part]
    Grds, tot_Df_Nd,Nd_ID0 = MeshgridNodes(Part_Mesh,Nd_ID0)
    Df_El,Df_El_loc,El_ID0 = MeshgridEls(Part_Mesh,Grds,El_ID0)
    return tot_Df_Nd, Df_El,Df_El_loc,Grds,Nd_ID0,El_ID0

def MeshgridNodes(Part_Mesh,Nd_ID0):
    tot_Df_Nd = pd.DataFrame(data = None, columns = ['X','Y','Z'])
    Grds = {}
    for i,L in enumerate(Part_Mesh.keys()):
        PartLayer = Part_Mesh[L]
        Grds[L]  = CreateGrid(PartLayer)
        Df_Nd,Grds[L]['ID']     = CreateNodeDf(Grds[L]['X'],Grds[L]['Y'],Grds[L]['Z'],Nd_ID0)
        Nd_ID0 = Df_Nd.index[-1]+1
        
        tot_Df_Nd = pd.concat([tot_Df_Nd,Df_Nd])
        
    tot_Df_Nd[tot_Df_Nd.columns] = tot_Df_Nd[tot_Df_Nd.columns].apply(pd.to_numeric)  
    return Grds,tot_Df_Nd ,Nd_ID0 


def MeshgridEls(Part_Mesh,Grds,El_ID0):
    Df_El_loc = pd.DataFrame(data = None, columns = ['X','Y','Z'], dtype=np.float64)
    if len(Part_Mesh.keys())-1 ==0:
        ElID = pd.DataFrame(data = np.arange(El_ID0,El_ID0 + np.size(Grds['L0']['ID'][:-1,:-1])))
        Df_El = CreateElements(ElID,Grds['L0']['ID'],['N'+str(x) for x in range(4)])
        
        c_EL = lambda loc: Grds['L0'][loc]
        El_Xloc = ElementLocation(c_EL('X')) ; El_Yloc = ElementLocation(c_EL('Y')) ; El_Zloc = ElementLocation(c_EL('Z'))
        Df_El_loc = pd.concat([Df_El_loc,pd.DataFrame(data = np.array([El_Xloc,El_Yloc,El_Zloc]).T,index = ElID[0].tolist(),columns = ['X','Y','Z'])])
        
        El_ID0 = Df_El.index[-1]+1        
        
    else:
        Df_El     = pd.DataFrame(data = None, columns = ['N'+str(x) for x in range(8)], dtype=np.int64)    
        for i in range(len(Part_Mesh.keys())-1):
            # Skin Elements
            Diff_size = np.shape(Grds['L'+str(i)]['ID'])[0]-np.shape(Grds['L'+str(i+1)]['ID'])[0] 
            Half_size1 = int(Diff_size/2) if Diff_size!=0 else None ; Half_size2 = -int(Diff_size/2) if Diff_size!=0 else None
    
            for key in Grds['L'+str(i)].keys():
                Grds['L'+str(i)][key] = Grds['L'+str(i)][key][Diff_size:,:] if (MPB=='4PB' and Shape=='Doubler') else Grds['L'+str(i)][key][Half_size1:Half_size2,:]
    
            ElID = pd.DataFrame(data = np.arange(El_ID0,El_ID0 + np.size(Grds['L'+str(i)]['ID'][:-1,:-1])))
            El_Node_Df = CreateElements(ElID,Grds['L'+str(i)]['ID'],['N'+str(x) for x in range(4)])
            
            O_El_Node_Df = CreateElements(ElID,Grds['L'+str(i+1)]['ID'],['N'+str(x) for x in range(4,8)])
            Df_El = pd.concat([Df_El,pd.concat([El_Node_Df, O_El_Node_Df], axis=1)])
            
            c_EL = lambda loc: (Grds['L'+str(i)][loc]+Grds['L'+str(i+1)][loc])/2
            El_Xloc = ElementLocation(c_EL('X')) ; El_Yloc = ElementLocation(c_EL('Y')) ; El_Zloc = ElementLocation(c_EL('Z'))
            Df_El_loc = pd.concat([Df_El_loc,pd.DataFrame(data = np.array([El_Xloc,El_Yloc,El_Zloc]).T,index = ElID[0].tolist(),columns = ['X','Y','Z'])])
            
            El_ID0 = Df_El.index[-1]+1
    return Df_El,Df_El_loc,El_ID0

def CreateNodeDf(x,y,z,ID0):
    NodeID = np.arange(ID0,ID0+np.size(x)).reshape(np.shape(x)[0],np.shape(x)[1])
    Df = pd.DataFrame(data = np.vstack((x.reshape(-1),y.reshape(-1),z.reshape(-1))).T, index = NodeID.reshape(-1), columns = ['X','Y','Z'])
    return Df,NodeID


def CreateGrid(PartLayer):
    MeshgridXY = np.meshgrid(PartLayer['X'],PartLayer['Y'])
    MeshgridXZ = np.meshgrid(PartLayer['X'],PartLayer['Z'])
    return {'X':MeshgridXY[0], 'Y':MeshgridXY[1], 'Z':MeshgridXZ[1]} 

def CreateElements(ElID,Grid,col):
    add = lambda a,b,c,d: Grid[a:b,c:d].reshape(-1)
    El_Node_Df = pd.DataFrame(data = np.array([add(0,-1,0,-1),  add(0,-1,1,None),  add(1,None,1,None),  add(1,None,0,-1)]).T,\
                                    index = ElID[0].tolist(), columns=col, dtype=np.int64)    
    return El_Node_Df

# Elements
def ElementLocation(LocGrid):
    add = lambda a,b,c,d: LocGrid[a:b,c:d].reshape(-1)
    Nodes   = (add(0,-1,0,-1) + add(0,-1,1,None) + add(1,None,1,None)+ add(1,None,0,-1))/4
    return Nodes


def WriteNdEl(file):
    lib_Mesh= {}
    lib_Mesh['Skin']     = SkinMesher()
    if Shape=='Plate': next
    elif Shape=='Coupon':
        lib_Mesh['Stringer0'] = SkinMesher()        
        for i in range (ttt['Stringer']+1):
            pos = Thickness['Stringer']*(i/(ttt['Stringer']))
            lib_Mesh['Stringer0']['L'+str(i)]['Z']*=0
            lib_Mesh['Stringer0']['L'+str(i)]['Z'] += Thickness['Skin']+pos
    
    else:
        for j,Loc in enumerate(Str_Loc):
            lib_Mesh['Stringer'+str(j)] = StringerMesher()
            for i, key in enumerate(lib_Mesh['Stringer'+str(j)].keys()):
                lib_Mesh['Stringer'+str(j)][key]['Y'] += Loc-str_HalfWidth


    El_ID0 = 1 ; Nd_ID0 = 1
    tot_Df_Nd = {};  Df_El= {}; Df_El_loc= {}
    for Part in lib_Mesh.keys():
        tot_Df_Nd[Part],Df_El[Part],Df_El_loc[Part],Grds,Nd_ID0,El_ID0 = MeshgridSolid(lib_Mesh,Part,Nd_ID0,El_ID0)
        
    with open(file, "w") as file:
        WriteNative(file,tot_Df_Nd,Df_El,ElType)
        if Shape !='Plate':
            if Coh: El_ID0 = WriteCoh(file,tot_Df_Nd,El_ID0)
            WriteTieEl(file,Df_El_loc)
            if Plydrop!=0: TaperEls(file,Df_El_loc)
            if Shape!='Coupon': WriteFlangeSets(file,Df_El_loc)
            # else: CreateDelam(file,Df_El_loc)
        file.write('*Elset, elset=ALLELEMENTS, generate\n')
        file.write('{:9d},{:9d},{:9d}'.format(1,El_ID0,1)+'\n')
    return tot_Df_Nd ,Df_El,Df_El_loc,El_ID0,Nd_ID0

def WriteNdsEls(file,Nds,Els,Type):
    file.write('*Node'+'\n')
    for Part in Nds:
        Nds[Part].to_csv(file, float_format = '%8.3f',header=False,sep=',',index=True,mode='a', line_terminator='\n')

    file.write('*Element, type={}'.format(Type)+'\n')
    for Part in Els:
        Els[Part].to_csv(file, float_format = '%8d',header=False,sep=',',index=True,mode='a', line_terminator='\n')

def WritePartsSets(file,Df_El):
    for Part in Df_El:
        El_list = np.array(Df_El[Part].index.tolist())
        file.write('*Elset, elset={}_El'.format(Part)+'\n')
        WriteSet(file,El_list)    
        

def WriteNative(file,tot_Df_Nd,Df_El,Type):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    enter(2)
    file.write('** PART MESH'+'\n')
    WriteNdsEls(file,tot_Df_Nd,Df_El,Type)
    WritePartsSets(file,Df_El)
    
    ttt_list = {}  
    for Part in Df_El:
        El_start = Df_El[Part].index[0] ; El_stop = Df_El[Part].index[-1]
        
        Part = Part.rstrip(string.digits)
        if (Part=='Stringer' and Plydrop!=0): continue

        for i in range(ttt[Part]):
            if Part=='Stringer':
                if str(i) not in ttt_list:
                    ttt_list[str(i)] = ''
                ttt_list[str(i)] +='{:9d},{:9d},1\n'.format(int(El_start+ int(i!=0) +i/ttt[Part]*(El_stop-El_start)),int(El_start+(i+1)/ttt[Part]*(El_stop-El_start)))
            else:
                file.write('*Elset, elset={}_L{}, generate'.format(Part,i)+'\n')
                file.write('{:9d},{:9d},1\n'.format(int(El_start+ int(i!=0) +i/ttt[Part]*(El_stop-El_start)),int(El_start+(i+1)/ttt[Part]*(El_stop-El_start))))

    for key in ttt_list.keys():        
        file.write('*Elset, elset={}_L{}, generate'.format('Stringer',key)+'\n')
        file.write(ttt_list[key])
        
    enter(2)    
    return

    
def TaperEls(file,Df_El_loc):
    file.write('** taper layups\n')
    El_list = {}
    
    for Part in Df_El_loc.keys():
        if Part.rstrip(string.digits)=='Stringer':
            Df_tap = Df_El_loc[Part]
            Y = Str_Loc[int(Part.replace('Stringer',''))]
                
            lLay = len(Layup['Stringer'])
        
            for i in range(lLay):
                if str(i) not in El_list:
                    El_list[str(i)] = np.array([],dtype=np.int64)
                    
                if i==lLay-1:
                    # El_list = np.array(Df_tap.index.tolist())
                    El_list[str(i)] = np.hstack((El_list[str(i)],Df_tap.index.tolist()))
                else:
                    if ElPlyDrop>0 or ((i+1)/ElPlyDrop).is_integer():next
                    else: continue
                    Tap_Str = '(Y<={0}-{1} | Y>={0}+{1})'.format(Y,(str_HalfWidth-Plydrop*(i+1)))
                    El_list[str(i)] = np.hstack((El_list[str(i)],np.array(Df_tap.query(Tap_Str).index.tolist())))
                    Df_tap  = Df_tap.query('~'+Tap_Str)
                
    for key in El_list.keys():             
        file.write('*ELSET, ELSET = {}_L{}\n'.format('Stringer',key))
        WriteSet(file,El_list[key])
                
    return



def WriteFlangeSets(file,Df_El_loc):
    Y = np.sort(list(set(Df_El_loc['Skin']['Y'])))
    
    Y0 = Str_Loc[2]-str_HalfWidth if MPB=='FSP' else Str_Loc[0]-str_HalfWidth
    
    Yflange= min( Y[(Y-Y0)>0])
    Yflange2= min( Y[(Y-Y0)>0])+Mesh_fla
    Yskin= max( Y[(Y-Y0)<0])

    El_lst = lambda Part, Yi : np.array(Df_El_loc[Part][np.logical_and((Yi-0.01)<Df_El_loc[Part]['Y'],Df_El_loc[Part]['Y']<(Yi+0.01))].index.tolist())

    file.write('*ELSET, ELSET = FI_Skin\n')
    WriteSet(file,El_lst('Skin',Yskin))
    file.write('*ELSET, ELSET = FI_Bot\n')
    WriteSet(file,El_lst('Skin',Yflange))
    file.write('*ELSET, ELSET = FI_Top\n')
    WriteSet(file,El_lst('Stringer2' if MPB=='FSP' else 'Stringer0',Yflange))
    return 

