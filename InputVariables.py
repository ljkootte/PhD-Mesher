# -*- coding: utf-8 -*-_
"""
Created on Sun Apr  8 14:03:40 2018

@author: luuki
"""
import numpy as np
import pandas as pd
from BasicFunctions import GetMM,CalculateTauc2

#Variables

MPB = '3PB';  ElType   = 'SC8R' ; Shape = 'Doubler' #Hat, Doubler, Coupon, Plate
Str_Lay = 'Thick'; Sk_Lay = 'Thin'
Coh = True; superpose = True;  
cpu = 32 if Coh else 4 ; mem =  None # number of cores and gb ram
Coh_mat = 'G0' ; Coh_Tri = 'GSS'

Mesh_glo = 2.0
if not Coh: El_Edge = 0.3
ttt = {'Skin':1,'Stringer':1}

if Shape=='Coupon':
    Mesh_fla = 0.1
    ttt['Stringer'] = ttt['Skin']
else:  
    Mesh_fla = 0.3 if Coh else Mesh_glo

Plydrop = 0.#  # drop a ply every x mm to create a taper, needs to be zero for large mesh size and element through-the-thickness.


if MPB == '7PB':
    sk_W    = 254  # Skin width 
    # sk_L    = 180  # Skin length
    if Str_Lay=='Thin':    
        sk_L    = 180  # Skin length
        Sup_X   = 20   # mm from bottom side
        Sup_Y   = 20   # mm from right side
        Load_Y  = 34
    elif Str_Lay=='Thick': 
        sk_L    = 140  # Skin length
        Sup_X   = 24   # mm from bottom side
        Sup_Y   = 36   # mm from right side
        Load_Y  = 36
    Load_X  = None # mm from bottom
    ind_ra  = 12.5 ; ind_L = 4
    Surf_sq = ind_ra # mm square around the loading and support points for interaction 



elif MPB == '6PB':
    sk_W    = 254  # Skin width 
    sk_L    = 260  # Skin length
    Sup_X   = 38.5 # mm from bottom side
    Sup_Y   = 60   # mm from right side
    Load_X  = None # mm from bottom
    Load_Y  = 60

elif MPB == 'SSCS':
    sk_W    = 254  # Skin width 
    sk_L    = 240  # Skin length

elif MPB == '4PB':
    if Shape == 'Doubler': sk_W = 127 #127
    elif Shape == 'Hat':   sk_W = 254 #sk_W = 254   
    else: sk_W = 220
    if Str_Lay=='Thin':    
        sk_L    = 140  # Skin length
        Sup_X   = 44   # mm from right side  
        Sup_Y   = 50   # mm from bottom side
    elif Str_Lay=='Thick': 
        sk_L    = 120  # Skin length
        Sup_X   = 30   # mm from right side 
        Sup_Y   = 27  # mm from bottom side
    Load_X  = None # mm from bottom
    Load_Y  = None
    if Shape == 'Coupon': 
        sk_W = 38 
        sk_L = 108
        Precrack = 0.2*sk_W
        Sup_X   = (sk_L-76)/2   # mm from right side  
        Sup_Y   = (sk_W-32)/2   # mm from bottom side 
        ind_ra  = 3
    elif Shape =='Doubler':
        Sup_X2 = Sup_X
        Sup_Y2 = sk_W-15
        
elif MPB == '3PB':
    sk_W    = 254#9*25.4  # Skin width
    sk_L    = 25.4  # Skin length
    Sup_Y   = 34#(sk_W-8*25.4)/2   # mm from bottom side
    R_bot   = 25.4
    R_top   = 6.35
    
    if Shape == 'Coupon': 
        sk_W      = 125  # Skin width
        sk_L      = 25 # Skin length
        Precrack  = 25
        Sup_Y     = 25   # mm from bottom side
        R_bot   = 3
        R_top   = 3
   
elif MPB=='DCB':
    sk_W      = 200  # Skin width
    sk_L      = 25 # Skin length
    Precrack  = 25

elif MPB=='MMB':
    sk_W      = 125  # Skin width
    sk_L      = Mesh_fla*2#0.2#25 # Skin length
    Precrack  = 25
    MMB_Ydown = sk_W - 25
    MMB_Yup   = MMB_Ydown/2
    R_circ = 3
    MM = 0.76 #0.2, 0.44, 0.76

elif MPB=='FSP':
    sk_W    = 770  # Skin width
    sk_L    = 685  # Skin length

elif MPB=='Test':
    sk_L    = 2  # Skin length

if MPB in ['4PB', '6PB', '7PB']: # indenter length and radius
    ind_ra  = 12.5  # Radius of the indenter, Delft is 12.5 mm
    ind_L = 4 # length of the indenter, only visual, Delft is 4 mm
    Surf_sq = ind_ra # mm square around the loading and support points for interaction 1-2x radius of indenter
elif MPB == '3PB':  Surf_sq = R_top*2   # mm square around the loading and support points for interaction  
elif MPB == 'MMB':  Surf_sq = R_circ*2   # mm square around the loading and support points for interaction  


Material = {'Skin':'IM7/977-3','Stringer':'IM7/977-3'}

Sym = lambda lst,mid: lst+mid+lst[::-1]
if (MPB=='DCB' or MPB =='MMB' or (MPB=='3PB' and Shape=='Coupon')) and (Sk_Lay =='UD' or Str_Lay=='UD'): 
    Layup    = {'Skin':[90]*12,'Stringer':[90]*12}
else:
    Layup    = {'Skin':{'Thin':Sym([-45,45,0,90,-45,45],[]),\
                            'Thick':Sym([-45,45,0,90,-45,45],[])*2}[Sk_Lay],\
                'Stringer':{'Thin':Sym([-45,45,0,90,-45,45],[]),\
                            'Thick':Sym([-45,45,0,90,-45,45],[])*2}[Str_Lay]}

# STRINGER Geometry
if Shape =='Hat':
    str_Wfla = 27    # Stringer flange width
    str_Wtop = 30.6  # Stringer top width
    str_H    = 32.7  # Stringer heigth
    str_ang  = 70    # Stringer angle degrees
    str_HalfWidth = (str_Wfla+str_H/np.tan(str_ang*np.pi/180.))+str_Wtop/2
    radius = 5
    
elif Shape=='Doubler':
    if MPB=='3PB':
        str_HalfWidth = 2*25.4
        str_Wfla = 25.4
    else:
        str_Wfla = 27
        str_HalfWidth = (str_Wfla+32.7/np.tan(70*np.pi/180.))+15.3
    if MPB=='Test': sk_W = 2*(100+str_HalfWidth)

elif Shape=='Coupon':
    if MPB =='MMB': str_Wfla = MMB_Yup - Precrack   + R_circ   
    else:           str_Wfla = sk_W - Precrack-30
    str_HalfWidth = sk_W - Precrack
    
elif Shape =='Plate':
    str_HalfWidth = 0
    str_Wfla = 0



if MPB=='FSP': Str_Loc = np.array([11.8,222.8,438.8,649.8])+str_HalfWidth # Locations of the stringers on the four-stringer panel.
elif Shape=='Coupon': Str_Loc = np.array([str_HalfWidth])
elif Shape=='Doubler' and MPB == '4PB': Str_Loc = np.array([sk_W])
else: Str_Loc = np.array([sk_W/2])


# Lamina properties
LamName = ['IM7/977-3','New']
LamData = [[1.7E-9, 164000., 8980., .32,  .45, 5010., 5010., 3000., 0.128],\
           [0.0E-9, 66000., 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    
Lamina = pd.DataFrame(data = LamData, index = LamName, \
            columns = ['density','E1','E2','v12','v23','G12','G13','G23','t'])


    
if Coh:
    ## adhesive properties
    AdhName = ['Gclay','G0','GSS'] 
    AdhData = [[1.7E-9, 0.256, 0.65,  78.9, 99.4, 4.76E5, 2.07],\
               [1.7E-9, 0.26,  1.19,  78.9, 99.4, 4.76E5, 2.77],\
               [1.7E-9, 0.64,  1.29,  78.9, 99.4, 4.76E5, 3.33]] 
    Adhesive = pd.DataFrame(data = AdhData, index = AdhName, \
                columns = ['density','GIc','GIIc','sigc','tauc','KI','etaBK'])
        

    if superpose: 
        sigc2 = 0.7  # Secondary mode I strength
        Gss = np.array([0.64,0.66,0.62,0.93,1.29])
        BK_MM = np.array([0,0.2,0.44,0.76,1])
        
        Adhesive = CalculateTauc2(Adhesive,sigc2,Coh_mat,Coh_Tri,Gss,BK_MM) 

    Adhesive.loc[Coh_mat,'Ksh'] = int(Adhesive.loc[Coh_mat,'KI']*(Adhesive.loc[Coh_mat,'GIc']/Adhesive.loc[Coh_mat,'GIIc'])*(Adhesive.loc[Coh_mat,'tauc']/Adhesive.loc[Coh_mat,'sigc'])**2)


# Interaction properties
Int_Name = 'SURFS'
Int_Fric = 0.2
if MPB=='MMB': Int_Fric = 0.

# Dependent Variables
Thickness = {}
for Part in Material: Thickness[Part] = len(Layup[Part]) *Lamina.loc[Material[Part],'t']


# Loading time parameters
if MPB=='MMB':    c = GetMM(MM,MMB_Yup,Precrack,Lamina,Material,Layup,Thickness)

Disp = {'DCB':20,'3PB':-12,'4PB':-12,'7PB':-20,'FSP':-4,'SSCS':-4,'Test':-45} 
Disp = Disp[MPB] if MPB in Disp.keys() else -20
Loadspeed = 4
tend = np.abs(Disp)/Loadspeed # 0.4
inc  = 10000
t0   = 1e-4*tend if Coh else 0.01*tend
tmin = 1e-10
tmax = (0.1 if MPB=='FSP' else 0.1)/Loadspeed
if sk_L<=2: tmax= t0*5
LineSearch = True ; FieldDisplacement = True; RunTemp = True
TimeIncrements = False if Shape=='Coupon' else True

FieldFreq = 1 if (Shape=='Coupon' or not Coh) else 5 
Energy = True ; Strain =True

    
#Cohesive Zone
Visc  = 1E-5*tend  # 1.0E-7
if MPB=='FSP' :  L_Coh = 0.2
elif MPB=='4PB': L_Coh = 0.05 
else:  L_Coh = 0
Inserts = {} #'Stringer0':{'Right':{'X':sk_L/2,'len':20}}}



if Shape == 'Hat':
    if radius!=0: Spacing =  Mesh_fla + radius/(np.tan((np.pi-str_ang*np.pi/180.)/2))
    elif radius==0: Spacing =  Mesh_glo
else: Spacing =  Mesh_fla 


MeshDiv = int(np.round(np.log(Mesh_glo/Mesh_fla)/np.log(3)))
if Shape !='Hat' or MeshDiv == 0: Remeshing = False


ElPlyDrop = 1
if Plydrop!=0:
    if Plydrop>Mesh_fla:    
        while (Mesh_fla*1.2)*ElPlyDrop <Plydrop: ElPlyDrop += 1
    elif Plydrop<Mesh_fla:
        for ElPlyDrop in range(1,len(Layup['Stringer'])):
            if len(Layup['Stringer'])%ElPlyDrop!=0: continue
            if (Mesh_fla/1.2)*(ElPlyDrop**-1) <=Plydrop: break
        ElPlyDrop*=-1
    Mesh_fla = Plydrop/(abs(ElPlyDrop)**int(np.sign(ElPlyDrop)))
    
print(f'Mesh flange size is: {Mesh_fla}')
FlangeTermination = (sk_W/(2-((Shape=='Doubler' and MPB=='4PB')or Shape=='Coupon'))-str_HalfWidth)
InnerCorner = str_Wfla-radius/(np.tan((np.pi-str_ang*np.pi/180.)/2)) if Shape=='Hat' else str_Wfla


Mesh_ind = 0.5 if Coh else 0.5
if MPB=='3PB' or Shape=='Coupon':
    MeshX_regi = np.array([0.0, sk_L/2])
    MeshX_size = np.array([(Mesh_glo+Mesh_fla)/2])    
elif MPB=='Test':
    MeshX_regi = np.array([0.0, sk_L/2])
    MeshX_size = np.array([sk_L/2])    
elif MPB=='SSCS' or MPB=='FSP':
    MeshX_regi = np.array([0.0, L_Coh*sk_L, (L_Coh+0.1)*sk_L, sk_L/2])
    MeshX_size = np.array([Mesh_glo,(Mesh_glo+Mesh_fla)/2,Mesh_fla])        
else:
    if MPB=='7PB':
        MeshX_regi = np.array([0.0, Sup_X-Surf_sq/2,Sup_X , Sup_X+Surf_sq/2, sk_L/2])
        MeshX_size = np.array([Mesh_glo,(Mesh_glo+Mesh_fla)/2,(Mesh_glo+Mesh_fla)/2,Mesh_fla])  
    else:
        MeshX_regi = np.array([0.0, Sup_X-Surf_sq/2,Sup_X , Sup_X+Surf_sq/2, sk_L/2])
        MeshX_size = np.array([Mesh_fla,Mesh_fla,Mesh_fla,Mesh_fla])  
        

if Shape=='Coupon' or MPB=='SSCS' or MPB=='FSP':
    MeshY_regi = np.array([0.0, 0.9*FlangeTermination,FlangeTermination])
    MeshY_size = np.array([Mesh_glo,(Mesh_fla+Mesh_glo)/2])

elif MPB=='Test':
    MeshY_regi = np.array([0.0,FlangeTermination])
    MeshY_size = np.array([Mesh_glo])

else:

    if MPB=='7PB': Ymin,Yplus = tuple(np.sort([Load_Y,Sup_Y]))
    else: Ymin = Yplus = Sup_Y

    MeshY_regi = np.array([0.0, Ymin-Surf_sq/2,Ymin])
    MeshY_size = np.array([Mesh_glo,Mesh_ind])  
    
    if Ymin!=Yplus:
        MeshY_regi = np.hstack((MeshY_regi,[Yplus]))
        MeshY_size = np.hstack((MeshY_size,[Mesh_ind]))    

    if Yplus+Surf_sq/2 < FlangeTermination:  
        MeshY_regi = np.hstack((MeshY_regi,[Yplus+Surf_sq/2]))
        MeshY_size = np.hstack((MeshY_size,[Mesh_ind]))

    if MeshY_regi[-1] < 0.9*FlangeTermination:  
        MeshY_regi = np.hstack((MeshY_regi,0.9*FlangeTermination))
        MeshY_size = np.hstack((MeshY_size,[(Mesh_glo+Mesh_fla)/2]))     
        
    MeshY_regi = np.hstack((MeshY_regi,[FlangeTermination]))
    MeshY_size = np.hstack((MeshY_size,[(Mesh_glo+Mesh_fla)/2]))





