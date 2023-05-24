# -*- coding: utf-8 -*-
"""
@author: L.J. Kootte
@email: luckootte@gmail.com
Developed for the PhD Thesis at TUDelft supervised by Prof.dr. C. Bisagni and Prof.dr. C. Kassapoglou
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from InputVariables import *
import time
# Elements

def lins(a,b,size,end=False):
    return(np.linspace(a,b,int(np.ceil((b-a)/size))+int(end),endpoint = end))

def myround(x, base=3):
    return base * int(np.round(x/base))


def MeshskX(): # ,Remesh=None
    # Mesh X
    sk_XMesh = np.array([])
    for i in range(len(MeshX_size)):
        sk_XMesh = np.hstack((sk_XMesh,lins(MeshX_regi[i],MeshX_regi[i+1],MeshX_size[i])))
    if MPB=='Test'or (Shape=='Coupon' and sk_L <= 2): return np.sort(np.hstack((np.array([0]),sk_L/2))) 
    return np.sort(np.hstack((sk_XMesh,sk_L/2,sk_L-sk_XMesh[::-1])))

def MeshMidY():

    Y0 = str_Wfla-(Spacing-Mesh_fla)
    if Shape !='Hat':
        YMesh_fl_mid  = np.array([])
        if MPB=='DCB' or MPB=='MMB' or (MPB=='3PB' and Shape=='Coupon') or MPB=='ENF':
            YMesh_fl_mid = lins(Y0,sk_W-25,Mesh_glo,False)
        elif MPB=='3PB':
            YMesh_fl_mid  = np.hstack((YMesh_fl_mid,lins(Y0,str_HalfWidth-Surf_sq/2,Mesh_glo,False)))
            YMesh_fl_mid  = np.hstack((YMesh_fl_mid,lins(str_HalfWidth-Surf_sq/2,str_HalfWidth,Mesh_ind,False)))
        elif MPB =='4PB':
            YMesh_fl_mid  = np.hstack((YMesh_fl_mid,lins(Y0,str_HalfWidth-15-Surf_sq/2,(Mesh_glo+Mesh_ind)/2,False)))
            if Surf_sq<15:
                YMesh_fl_mid  = np.hstack((YMesh_fl_mid,lins(str_HalfWidth-15-Surf_sq/2,str_HalfWidth-15+Surf_sq/2,Mesh_ind,False)))
                YMesh_fl_mid  = np.hstack((YMesh_fl_mid,lins(str_HalfWidth-15+Surf_sq/2,str_HalfWidth,(Mesh_glo+Mesh_ind)/2,False)))
            else:
                YMesh_fl_mid  = np.hstack((YMesh_fl_mid,lins(str_HalfWidth-15-Surf_sq/2,str_HalfWidth,Mesh_ind,False)))
        else:
            YMesh_fl_mid  = np.hstack((YMesh_fl_mid,lins(Y0,str_HalfWidth,(Mesh_glo+Mesh_fla)/2,False)))
    else:
        YMesh_fl_mid1  = lins(InnerCorner,InnerCorner+radius*np.cos(str_ang*np.pi/180.-np.pi/2),(Mesh_fla+Mesh_glo)/2,False)
        if MPB=='7PB':
            YMesh_fl_mid2 = np.hstack((lins(InnerCorner + radius*np.cos(str_ang*np.pi/180.-np.pi/2)+Mesh_glo,str_HalfWidth-Surf_sq/2,Mesh_glo,False),\
                                       lins(str_HalfWidth-Surf_sq/2,str_HalfWidth,Mesh_ind,False)))
        else:
            YMesh_fl_mid2 = lins(InnerCorner + radius*np.cos(str_ang*np.pi/180.-np.pi/2)+Mesh_glo,str_HalfWidth,Mesh_glo,False)
        
        YMesh_fl_mid  = np.hstack((YMesh_fl_mid1,YMesh_fl_mid2))
        
    return YMesh_fl_mid 

def MeshskYPlate():
    YMesh_start = np.array([])
    for i in range(len(MeshY_size)):
        YMesh_start = np.hstack((YMesh_start,lins(MeshY_regi[i],MeshY_regi[i+1],MeshY_size[i])))
    sk_YMesh   = Stacking([YMesh_start],sk_W,-1)
    if sk_W/2 not in sk_YMesh: sk_YMesh = np.hstack((sk_YMesh,sk_W/2))
    return np.sort(sk_YMesh)  
    
def MeshskY():      # Skin Mesh Y
    
    from StringerMesher import  FlangeMesh
    YMesh_fl_f = FlangeMesh()
    
    if Shape=='Coupon' or (Shape=='Doubler' and MPB == '4PB'): YMesh_fl_f += sk_W-str_HalfWidth
    else: YMesh_fl_f += sk_W/2-str_HalfWidth

      
    YMesh_start = np.array([])
    for i in range(len(MeshY_size)):
        YMesh_start = np.hstack((YMesh_start,lins(MeshY_regi[i],MeshY_regi[i+1],MeshY_size[i])))
  
    
    if MPB == 'MMB':
        Part1 = lins(Precrack+str_Wfla,MMB_Ydown-R_circ,Mesh_glo)
        Part2 = lins(MMB_Ydown-R_circ,MMB_Ydown+R_circ,Mesh_fla)
        Part3 = lins(MMB_Ydown+R_circ,sk_W,Mesh_glo)
        YMesh_fl_mid  = np.hstack((Part1,Part2,Part3))     
        sk_YMesh   = np.hstack((YMesh_start,YMesh_fl_f,YMesh_fl_mid,sk_W))
    else: 
        YMesh_fl_mid = MeshMidY() 
        YMesh_fl_mid += sk_W/(2-(Shape=='Coupon' or (Shape=='Doubler' and MPB == '4PB')))-str_HalfWidth
        if Shape=='Coupon' or (Shape=='Doubler' and MPB == '4PB'): 
            sk_YMesh   =  np.hstack((YMesh_start,YMesh_fl_f,YMesh_fl_mid,sk_W))

        if MPB=='Test': sk_YMesh   = np.hstack([YMesh_start,YMesh_fl_f,YMesh_fl_mid,sk_W/2])
        else: 
            sk_YMesh   = Stacking([YMesh_start,YMesh_fl_f,YMesh_fl_mid],sk_W,-1)
    if sk_W/2 not in sk_YMesh: sk_YMesh = np.hstack((sk_YMesh,sk_W/2))
    return np.sort(sk_YMesh)

def Stacking(YZlst,YZmid,sign):
    YZ = np.array([YZmid/((3-sign)/2)])
    for yz in YZlst[::-1]: YZ = np.hstack((yz,YZ, [] if ((Shape =='Doubler' and MPB=='4PB')or Shape=='Coupon') else YZmid*(1-sign)/2+sign*yz[::-1]))
    return YZ

def SkinMesher():

    lib_sk_Mesh = {}
    for i in range (ttt['Skin']+1): 
        if MPB=='FSP': lib_sk_Mesh['L'+str(i)] = {'X':MeshskX(),'Y':MeshskYFSP(),'Z':np.array([Thickness['Skin']*(i/(ttt['Skin']))]*len(MeshskYFSP()))}
        elif Shape=='Plate': lib_sk_Mesh['L'+str(i)] = {'X':MeshskX(),'Y':MeshskYPlate(),'Z':np.array([Thickness['Skin']*(i/(ttt['Skin']))]*len(MeshskYPlate()))}
        else: lib_sk_Mesh['L'+str(i)] = {'X':MeshskX(),'Y':MeshskY(),'Z':np.array([Thickness['Skin']*(i/(ttt['Skin']))]*len(MeshskY()))}
    return lib_sk_Mesh



def FlangeMesh(i=0):
    if Plydrop!=0:
        if i==0: minEl = 0
        elif ElPlyDrop<0: minEl = (i-1)*(int(len(Layup['Stringer'])/ttt['Stringer']))
        else: minEl = (i-1)*(ElPlyDrop*(int(len(Layup['Stringer'])/ttt['Stringer'])))
        if ElPlyDrop>0:   YTaper = np.linspace(0,Plydrop*(len(Layup['Stringer'])-1),int((len(Layup['Stringer'])-1)*ElPlyDrop+1),True)[minEl:]    
        elif ElPlyDrop<0: YTaper = np.linspace(0,Plydrop*(len(Layup['Stringer'])+ElPlyDrop),-int(len(Layup['Stringer'])/ElPlyDrop),True)[minEl:]

        YMesh_fl_f =  np.hstack((YTaper,lins(YTaper[-1],str_Wfla-Spacing,Mesh_fla, True)[1:]))        

        
    else: YMesh_fl_f =  lins(0,InnerCorner,Mesh_fla, False)
    if not Coh and El_Edge!=0:
        YMesh_fl_f = np.sort(np.hstack((YMesh_fl_f,El_Edge)))
    return YMesh_fl_f



def MeshskYFSP():      # Skin Mesh Y
    YMesh_start  = lins(0,Str_Loc[0]-str_HalfWidth,Mesh_glo,True)
    YMesh_end = lins(Str_Loc[-1]+str_HalfWidth,sk_W,Mesh_glo,True)
    YMesh_fl_f = FlangeMesh(0)

    YMesh_fl_mid = MeshMidY()
    YMesh_str    = np.hstack((YMesh_fl_f,YMesh_fl_mid,str_HalfWidth,2*str_HalfWidth-YMesh_fl_mid[::-1],str_HalfWidth*2-YMesh_fl_f[::-1]))-str_HalfWidth
   

    sk_YMesh = YMesh_start[:-1]
    for j,Loc in enumerate(Str_Loc):
        if j==len(Str_Loc)-1 :
            sk_YMesh = np.hstack((sk_YMesh,Loc+YMesh_str,YMesh_end[1:]))
        else:
            sk_YMesh_bay = inclins(Mesh_fla,Mesh_glo,Str_Loc[j]+str_HalfWidth,Str_Loc[j+1]-str_HalfWidth,double = 'double')
            sk_YMesh = np.hstack((sk_YMesh,Loc + YMesh_str ,sk_YMesh_bay))

    return np.sort(sk_YMesh)



def inclins(d0,d1,x0,x1,double = 'single'):
    L = x1-x0 if double=='single' else (x1-x0)/2
    step = int(L/((d0+d1)/2))+1
    d1 = 2*L/step-d0
    d=np.linspace(d0,d1,step,True)
    nodes = np.cumsum(d)[:-1]
    if double=='double':
        nodes = np.hstack((nodes,L,2*L-nodes[::-1]))

    return x0+nodes
