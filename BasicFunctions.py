# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 16:17:04 2023

@author: ljkootte
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

def CalculateTauc2(Adhesive,sigc2,Coh_mat,Coh_Tri,Gss,BK_MM) :
    from scipy.optimize import curve_fit
        
    
    Adhesive.loc[Coh_Tri,'GIc'] = Adhesive.loc[Coh_Tri,'GIc']-Adhesive.loc[Coh_mat,'GIc']
    Adhesive.loc[Coh_Tri,'GIIc'] = Adhesive.loc[Coh_Tri,'GIIc']-Adhesive.loc[Coh_mat,'GIIc']

    BK = lambda M,eta:  Adhesive.loc[Coh_mat,'GIc']+(Adhesive.loc[Coh_mat,'GIIc']-Adhesive.loc[Coh_mat,'GIc'])*M**Adhesive.loc[Coh_mat,'etaBK']+ \
        Adhesive.loc[Coh_Tri,'GIc']+(Adhesive.loc[Coh_Tri,'GIIc']-Adhesive.loc[Coh_Tri,'GIc'])*M**eta
    Adhesive.loc[Coh_Tri,'etaBK'] = curve_fit(BK,xdata=BK_MM,ydata=Gss)[0][0]

    
    Adhesive.loc[Coh_Tri,'sigc'] = sigc2
    
    Adhesive.loc[Coh_Tri,'KI'] = Adhesive.loc[Coh_Tri,'sigc']*Adhesive.loc[Coh_mat,'sigc']/(2*Adhesive.loc[Coh_mat,'GIc'])

    tauc2 = Adhesive.loc[Coh_Tri,'tauc']*(sigc2/Adhesive.loc[Coh_Tri,'sigc'])*(Adhesive.loc[Coh_Tri,'GIIc']/Adhesive.loc[Coh_mat,'GIIc'])\
        *(Adhesive.loc[Coh_mat,'GIc']/Adhesive.loc[Coh_Tri,'GIc'])
    
        
    print('tauc2 = ',tauc2)

    Adhesive.loc[Coh_Tri,'tauc'] = tauc2
    Adhesive.loc[Coh_Tri,'Ksh'] = Adhesive.loc[Coh_Tri,'tauc']*Adhesive.loc[Coh_mat,'tauc']/(2*Adhesive.loc[Coh_mat,'GIIc'])
    return Adhesive

def WriteToExcel(MPB,Direc,n_Nodes,n_Elements,txt_Reason,txt_Comments):
    writer = pd.ExcelWriter('Models.xlsx', engine='xlsxwriter')
    columns = ['Cohesives','trilinear','n Elements','n Nodes','Specimen length','Specimen width',\
               'thickness skin','thickness stringer','Sx','Sy','Lx','Ly','Why model','Comments'\
                   ,'Global mesh size','Cohesive mesh size','Gc','Gc_tri']
    data =  [Coh_mat if Coh else '',Coh_Tri if superpose else '',n_Elements,n_Nodes,\
            sk_L,sk_W,Thickness['Skin'],Thickness['Stringer'],Sup_X,Sup_Y,Load_X,Load_Y,txt_Reason,txt_Comments,\
                Mesh_glo,Mesh_fla,Adhesive.loc[Coh_mat]  if Coh else '','' if not superpose else Adhesive.loc[Coh_Tri] ]
     # Create empty dataframe to be filled with the version, error and variables
    
    try: 
        Df_Excel = pd.read_excel('Models.xlsx', sheet_name= MPB)
        Df_Excel.loc[MPB+'-'+Direc] = data
    except:
        print('Initiate new excel sheet')
        Df_Excel = pd.DataFrame(data = np.array(data).reshape((1,-1)),columns = columns,index = [MPB+'-'+Direc])
    Df_Excel.to_excel(writer, sheet_name= MPB) #, index=False

    # workbook  = writer.book ; worksheet = writer.sheets[MPB]
    # # Apply a conditional format to the cell range.
    # worksheet.conditional_format('B2:B{}'.format(Version+1), {'type': '3_color_scale','min_color': "green",'mid_color': "yellow", 'max_color': "red"})
    # # Add some cell formats.
    # format1 = workbook.add_format({'num_format': '#,##0'})
    # format2 = workbook.add_format({'num_format': '0.00'})
    
    # # Set the column width and format.
    # worksheet.set_column('B:B', None, format1)
    # # Set the format but not the column width.
    # worksheet.set_column('G:G', None, format2)
    writer.save()
    