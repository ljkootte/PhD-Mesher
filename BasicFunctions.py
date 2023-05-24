# -*- coding: utf-8 -*-
"""
@author: L.J. Kootte
@email: luckootte@gmail.com
Developed for the PhD Thesis at TUDelft supervised by Prof.dr. C. Bisagni and Prof.dr. C. Kassapoglou
"""
import numpy as np
import pandas as pd

def ABDmatrix(El,Et,vlt,Glt,thetas,thickn):
    #Total thickness of laminate
    T=np.size(thetas)*thickn
    Am = 0 ; Bm = 0 ; Dm = 0 
    #Creating z coordinates and zero matrices

    zf = np.arange(len(thetas)+1)*thickn-T/2
    #Creating ABD or C matrix, depending on thin or thick
    vtl=Et*vlt/El
    Qp=np.matrix([[El/(1-vlt*vtl),vlt*Et/(1-vlt*vtl),0],
                   [vlt*Et/(1-vlt*vtl),Et/(1-vlt*vtl),0],[0,0,Glt]])
    for i in range(0,np.size(thetas),1):
        theta2=thetas[i]/180.*np.pi
        n=np.sin(theta2)
        m=np.cos(theta2)
        #Transformation matrix
        M=np.matrix([[m**2,n**2,2*m*n],[n**2,m**2,-2*m*n],[-m*n,m*n,m**2-n**2]])
        Mt=np.transpose(M)
        #Stiffness matrix of each ply
        Cp=M*Qp*Mt
        #ABD matrix for laminate with thick laminate theory
        Am += Cp*(zf[i+1]-zf[i])
        Bm += 1/2.*Cp*(zf[i+1]**2-zf[i]**2)
        Dm += 1/3.*Cp*(zf[i+1]**3-zf[i]**3)
    #Stacking A,B and D matrix

    abdm=np.hstack((np.vstack((Am,Bm)),np.vstack((Bm,Dm))))
    abdm[abs(abdm)<10**-10]=0
    return abdm
    #Taking out values close to zero, otherwise really small values are left in
    #which are caused by roundoff errors.
def ABDcompliance(abd):
    Am = abd[:3,:3]
    Bm = abd[:3,3:]
    Dm = abd[3:,3:]
    Am_c = np.linalg.inv(Am)
    
    delta  = np.linalg.inv(Dm-Bm*Am_c*Bm)
    alpha = Am_c + Am_c*Bm*delta*Bm*Am_c
    beta  = -Am*Bm*delta
    abdc = np.hstack((np.vstack((alpha,beta)),np.vstack((beta,delta))))
    abdc[np.abs(abdc)<10**-10]=0
    return abdc


def GetMM(MM,MMB_Yup,Precrack,Lamina,Material,Layup,Thickness):
    getLam = lambda var: Lamina.loc[Material['Skin'],var]
    E11  =getLam('E1') ;E22 = getLam('E2') ; G13 = getLam('G13')
    thetas  = Layup['Skin']

    if not (np.array(thetas)==90).all():
        Glt = getLam('G12') ; vlt =  getLam('v12') ; thickn = getLam('t')
        abd = ABDmatrix(E11,E22,vlt,Glt,thetas,thickn)
        abdc = ABDcompliance(abd)
        E11 = 1/(Thickness['Skin']*abdc[1,1])
        E22 = 1/(Thickness['Skin']*abdc[0,0])
    Gamma = 1.18*np.sqrt(E11*E22)/G13
    Chi = np.sqrt(E11/(11*G13)*(3-2*(Gamma/(1+Gamma))**2))
    alpha = 1/MM-1
    Beta = (Precrack+Chi*Thickness['Skin'])/(Precrack+0.42*Chi*Thickness['Skin'])
    c = (12*Beta**2+3*alpha+8*Beta*np.sqrt(3*alpha))/(36*Beta**2-3*alpha)*MMB_Yup 
    return c

def RecalcFlangeMesh(Plydrop,Mesh_fla,Layup):
               
    ElPlyDrop =  1 #this value should be one and is recalculate in the part below.
    if Plydrop>Mesh_fla:    
        while (Mesh_fla*1.2)*ElPlyDrop <Plydrop: ElPlyDrop += 1
    elif Plydrop<Mesh_fla:
        for ElPlyDrop in range(1,len(Layup['Stringer'])):
            if len(Layup['Stringer'])%ElPlyDrop!=0: continue
            if (Mesh_fla/1.2)*(ElPlyDrop**-1) <=Plydrop: break
        ElPlyDrop*=-1
    Mesh_fla = Plydrop/(abs(ElPlyDrop)**int(np.sign(ElPlyDrop)))
    return Mesh_fla, ElPlyDrop
