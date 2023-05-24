# -*- coding: utf-8 -*-
"""
@author: L.J. Kootte
@email: luckootte@gmail.com
Developed for the PhD Thesis at TUDelft supervised by Prof.dr. C. Bisagni and Prof.dr. C. Kassapoglou
"""
import numpy as np
import pandas as pd
from InputVariables import *


def Df_Coh(Df):
    indexID = pd.MultiIndex.from_arrays([np.round(Df['X'],3),np.round(Df['Y'],3)], names=['X', 'Y'])
   
    Df3 = (pd.DataFrame(data = Df.index.tolist(),index = indexID)).unstack().astype(str) 
    add = lambda a,b,c,d: Df3.iloc[a:b,c:d].reset_index(drop=True).T.reset_index(drop=True)

    a = ',   '+ add(0,-1,0,-1)    + ',  ' + add(1,None,0,-1)+\
        ',  ' + add(1,None,1,None)+ ',  ' + add(0,-1,1,None)
    b = a.T.unstack().reset_index(drop=True)
    
    return b


def CreateCohSet(Df_Nd,Side,Loc,Ins={}):
    
    if Side == 'Left':    Df = Df_Nd.query('{}<=Y<={} & Z=={}'.format(Loc+str_HalfWidth-str_Wfla+(Spacing-Mesh_fla)-0.01,Loc+str_HalfWidth+0.01,Thickness['Skin']))
    elif Side == 'Right': Df = Df_Nd.query('{}<=Y<={} & Z=={}'.format(Loc-str_HalfWidth-0.01,Loc-str_HalfWidth+str_Wfla-(Spacing-Mesh_fla)+0.01,Thickness['Skin']))
   
    elif Side =='All':    
            Df = Df_Nd.query('{0}<=Y<={1} & ({2}-0.01)<=Z<=({2}+0.01)'.format(Precrack,Precrack+100,Thickness['Skin']))

    
    if L_Coh !=0.: Df = Df.query('{0}<=X<={1}'.format(L_Coh*sk_L,(1-L_Coh)*sk_L))
            
    if len(Ins)!=0: 
        if Ins['l']<0:   Df = Df.query('X<={0}+{1}'.format(Ins['X'],Ins['l']))
        elif Ins['l']>0: Df = Df.query('X>={0}+{1}'.format(Ins['X'],Ins['l']))

    
    
    if len(Df)==0:
         return False
    else:
        return Df_Coh(Df)

def MeshCohesive(tot_Df_Nd,StartElID):
    global CohSide
    CohSide={}
    if Shape=='Coupon':
        CohSide,StartElID = CombineCohSets(CohSide,'All',tot_Df_Nd,StartElID,Loc=Str_Loc[0],Part='Stringer0')
    else:
        for j,Loc in enumerate(Str_Loc):
            for Side in ['Left','Right']:
                if 'Stringer'+str(j) in Inserts.keys() and Side in Inserts['Stringer'+str(j)].keys():
                    for Ins in [-Inserts['Stringer'+str(j)][Side]['len']/2,+Inserts['Stringer'+str(j)][Side]['len']/2]:
                        CohSide,StartElID = CombineCohSets(CohSide,Side,tot_Df_Nd,StartElID,Loc=Loc,Ins={'X':Inserts['Stringer'+str(j)][Side]['X'],'l':Ins},Part='Stringer'+str(j))
                else:
                    CohSide,StartElID = CombineCohSets(CohSide,Side,tot_Df_Nd,StartElID,Loc=Loc,Part='Stringer'+str(j))

    return CohSide, StartElID



def CombineCohSets(CohSide,Side,tot_Df_Nd,StartElID,Loc,Ins={},Part='Stringer0'):
    Ski = CreateCohSet(tot_Df_Nd['Skin'],Side,Loc,Ins)
    Str = CreateCohSet(tot_Df_Nd[Part],Side,Loc,Ins)
    if type(Str)!=bool: 
        El_id = pd.DataFrame(data =np.arange(StartElID,StartElID+len(Str))).astype(str)
        CohSide[Part+'_'+Side]  = El_id[0] + Ski + Str
        StartElID += len(Str)
    return CohSide,StartElID

def WriteCoh(file,tot_Df_Nd,StartElID):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    # Cohesive Elements
    CohSide, StopElID = MeshCohesive(tot_Df_Nd,StartElID)
    
    file.write('*ELEMENT, TYPE=COH3D8\n')
    for Side in CohSide.keys():
        for txt in CohSide[Side].values: file.write(txt+'\n')
    
    split  = lambda Df, i: int(Df.iloc[i].split(',')[0])
    
    file.write('*ELSET, ELSET=COH, GENERATE\n')
    file.write('{},  {},1\n'.format(StartElID,StopElID-1))

    return StopElID+1


def WriteTieEl(file,Df_El_loc):
    enter = lambda a: [file.write('**\n') for i in range(a)]

    SkinSurf = np.array([]) ;     StringerSurf = np.array([])
    for j,Loc in enumerate(Str_Loc):
        SkinSurf     = np.concatenate((SkinSurf,FindSurface(Df_El_loc['Skin'],Loc=Loc)))
        StringerSurf = np.concatenate((StringerSurf,FindSurface(Df_El_loc['Stringer'+str(j)],Loc = Loc)))
            
    
    if len(SkinSurf)==0 or len(StringerSurf)==0:
        return

    SPOS ='S2';   SNEG ='S1' 
    
    WriteTieEl2(file,SkinSurf,'Skin',SPOS) 
    WriteTieEl2(file,StringerSurf,'Stringer',SNEG) 
        
    file.write('*Tie, name=Skin_Stringer, adjust=yes\n')#, no thickness
    file.write('Stringer,Skin\n')
    return

def WriteTieEl2(file,Surf,Part,S):
    file.write('*ElSET, ElSET = {0}\n'.format(Part))
    WriteSet(file,Surf)
    file.write('*Surface, type=Element, name={}\n'.format(Part))
    file.write('{0},{1}\n'.format(Part,S))
    return



def FindSurface(Df,Loc):
    
    if Shape == 'Coupon' :
        TieEl = '{0}<=Y<={1} '.format(Precrack,sk_W)
    elif (Shape=='Doubler' and MPB=='4PB'):
        TieEl = '{0}<=Y<={1} '.format(Loc-str_HalfWidth,sk_W)
    elif Shape == 'Doubler':
        TieEl = '{0}<=Y<={1} '.format(Loc-str_HalfWidth,Loc+str_HalfWidth)
    else:
        TieEl = '(({0} <= Y <= {1})|({2} <= Y <= {3}))'.format(\
            Loc-str_HalfWidth,Loc-str_HalfWidth+str_Wfla-Spacing+Mesh_fla,Loc+str_HalfWidth-str_Wfla+Spacing-Mesh_fla, Loc+str_HalfWidth)
    if Coh :
        if Shape == 'Coupon' :
            CohEl = '({0}<=Y<={1})'.format(Precrack,Precrack+100)
        elif (MPB=='4PB' and Shape=='Doubler'):
            CohEl = '({0}<=Y<={0}+{1})'.format(Loc-str_HalfWidth,str_Wfla)
        else:
            CohEl = '(({0} <= X <= {1}) & (({2} <= Y <= {3}) | ({4} <= Y <= {5})) )'.format(\
                              L_Coh*sk_L,(1-L_Coh)*sk_L,Loc-str_HalfWidth,Loc-str_HalfWidth+str_Wfla-(Spacing-Mesh_fla),\
                              Loc+str_HalfWidth-str_Wfla+(Spacing-Mesh_fla),Loc+str_HalfWidth)
            
        TieEl += ' & ~ {0}'.format(CohEl)

    return np.array(Df.query(TieEl).index.tolist())


def WriteSet(file,Surf):
    Row = 16
    El_begin = Surf[:Row*int(len(Surf)/Row)].reshape(int(len(Surf)/Row),Row)
    El_end = Surf[Row*int(len(Surf)/Row):]
    
    np.savetxt(file,El_begin,fmt='%8d',delimiter=',') 
    if len(El_end)>0:
        string = ','.join(map('{0:8d}'.format,map(int,El_end)))
        file.write(string+'\n')
    return

def CreateDelam(file,Df_El_loc):
    
    for i,Part in enumerate(['Stringer0','Skin'],1):
        if i==1: Z = Thickness['Skin']+Thickness['Stringer']*(1/(2*ttt['Stringer']))
        else:    Z = Thickness['Skin']*(1-1/(2*ttt['Skin']))

        
        Els  = np.array(Df_El_loc[Part].query('{0}<=Y<={1} & {2}-0.01<=Z<={2}+0.01'.format(0,Precrack,Z)).index.tolist())
        file.write(f'*ELSET, ELSET = {Part}_Insert\n')
        WriteSet(file,Els)
        file.write(f'*Surface, type=ELEMENT, name=InsertS{i}\n')
        file.write(f'{Part}_Insert,S{i}\n')
    Type = ', type=SURFACE TO SURFACE, no thickness, TRACKING=STATE' if Solver=='Implicit' else ', mechanical constraint=KINEMATIC'
    file.write('*Contact Pair, interaction=SURFS'+Type+'\n')
    file.write('InsertS2,InsertS1\n')




