# -*- coding: utf-8 -*-
"""
@author: L.J. Kootte
@email: luckootte@gmail.com
Developed for the PhD Thesis at TUDelft supervised by Prof.dr. C. Bisagni and Prof.dr. C. Kassapoglou
"""
import numpy as np
from InputVariables import *
import matplotlib.pyplot as plt
from SkinMesher import MeshskX,Stacking,lins,MeshMidY,FlangeMesh


def StringerMesher():
    # Variables
    lib_str_Mesh = {}

    for i in range (ttt['Stringer']+1):
        pos = Thickness['Stringer']*(i/(ttt['Stringer']))
        lib_str_Mesh['L'+str(i)] = {'X':MeshskX(),'Y':MeshstrY(i,pos),'Z':MeshstrZ(i,pos)}

    return lib_str_Mesh


def MeshstrY(i,pos):

    YMesh_fl_f = FlangeMesh(i)
    if Shape =='Hat':
        
        if int((radius*str_ang*np.pi/180.)/(Mesh_fla*2))<8:      
            Thetas = np.linspace(0,str_ang*np.pi/180.,8,True)-np.pi/2
        else:
            Thetas = np.linspace(0,str_ang*np.pi/180.,int((radius*str_ang*np.pi/180.)/(Mesh_fla*2)),True)-np.pi/2
        O_YRadius = (radius - pos)*np.cos(Thetas)+str_Wfla-radius/(np.tan((np.pi-str_ang*np.pi/180.)/2))
        Thetas2 = np.linspace(0,str_ang*np.pi/180.,int((radius*str_ang*np.pi/180.)/(Mesh_glo/2)),True)[::-1]+np.pi/2
        if len(Thetas2)==1: Thetas = np.array([str_ang*np.pi/180.+np.pi])/2
 
        O_YRadius2 = (radius + pos)*np.cos(Thetas2)+ (str_HalfWidth-str_Wtop/2) +radius/(np.tan((np.pi-str_ang*np.pi/180.)/2))
        O_YMesh_web  = np.linspace(O_YRadius[-1],O_YRadius2[0],int(np.sin(str_ang*np.pi/180)*str_H/Mesh_glo), endpoint = False)[1:]
        O_YMesh_top  = lins(O_YRadius2[-1],str_HalfWidth,Mesh_glo,False)[1:]
        O_YMesh_f   = Stacking([YMesh_fl_f,O_YRadius,O_YMesh_web,O_YRadius2,O_YMesh_top],str_HalfWidth*2,-1)#O_YRadius

    if MPB=='Test': 
        YMesh_mid = MeshMidY()
        O_YMesh_f    = np.hstack([YMesh_fl_f,YMesh_mid,str_HalfWidth])   
    elif Shape == 'Doubler':
        YMesh_mid = MeshMidY()
        O_YMesh_f    = Stacking([YMesh_fl_f,YMesh_mid],str_HalfWidth*2,-1)   

    return O_YMesh_f  

def MeshstrZ(i,pos):#,Remesh=None


    ZMesh_fl_f = np.zeros(len(FlangeMesh(i)))


    O_ZMesh_fl_f = ZMesh_fl_f  +pos
    
    if Plydrop!=0 and i!=0: 
        for j in range(1,int(len(Layup['Stringer'])/ttt['Stringer'])):
            if ElPlyDrop>0:
                O_ZMesh_fl_f[:j*(ElPlyDrop)] -= Lamina.loc[Material['Stringer'],'t']
            elif ElPlyDrop<0 and (j/ElPlyDrop).is_integer():
                O_ZMesh_fl_f[:int(-j/ElPlyDrop)] += ElPlyDrop* Lamina.loc[Material['Stringer'],'t']

    if Shape =='Hat':

    
        if int((radius*str_ang*np.pi/180.)/(Mesh_fla*2))<8:      
            Thetas = np.linspace(0,str_ang*np.pi/180.,8,True)-np.pi/2
        else:
            Thetas = np.linspace(0,str_ang*np.pi/180.,int((radius*str_ang*np.pi/180.)/(Mesh_fla*2)),True)-np.pi/2
            
        
        O_ZRadius = (radius - pos)*(np.sin(Thetas)+1) +pos

        Thetas2 = np.linspace(0,str_ang*np.pi/180.,int((radius*str_ang*np.pi/180.)/(Mesh_glo/2)),True)[::-1]+np.pi/2
        if len(Thetas2)==1: Thetas = np.array([str_ang*np.pi/180.+np.pi])/2

        O_ZRadius2 = (radius + pos)*(np.sin(Thetas2)-1) +pos + str_H
        O_YRadius2 = (radius + pos)*np.cos(Thetas2)+ (str_HalfWidth-str_Wtop/2) +radius/(np.tan((np.pi-str_ang*np.pi/180.)/2))
        

        O_ZMesh_web  =  np.linspace(O_ZRadius[-1],O_ZRadius2[0],int(np.sin(str_ang*np.pi/180)*str_H/Mesh_glo), endpoint=False)[1:]
        ZMesh_top    =  np.zeros(int((str_HalfWidth-O_YRadius2[-1])/Mesh_glo))+str_H

        O_ZMesh_top  = ZMesh_top    + pos
        
        O_ZMesh_f    = Stacking([O_ZMesh_fl_f,O_ZRadius,O_ZMesh_web,O_ZRadius2,O_ZMesh_top],str_H+pos,1)#,O_ZRadius+pos
        
        
    elif MPB=='Test': 
        ZMesh_mid  =  np.zeros(len(MeshMidY()))        
        O_ZMesh_f    = np.hstack([O_ZMesh_fl_f,ZMesh_mid+pos,pos])   
    elif Shape == 'Doubler':
        ZMesh_mid  =  np.zeros(len(MeshMidY()))
        O_ZMesh_f  = Stacking([O_ZMesh_fl_f,ZMesh_mid+pos],pos,1)

    return O_ZMesh_f+Thickness['Skin']

