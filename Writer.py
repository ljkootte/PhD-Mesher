# -*- coding: utf-8 -*-
"""
@author: L.J. Kootte
@email: luckootte@gmail.com
Developed for the PhD Thesis at TUDelft supervised by Prof.dr. C. Bisagni and Prof.dr. C. Kassapoglou
"""
from InputVariables import *
from CohTie import FindSurface
from Supports import SupportContact

def WriteSupsFile(file,IndID):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    
    WriteInteraction_Sup(file)
    enter(2)
    WriteStep(file,IndID)
    WriteOutputReq(file)
    return

def WriteOutOfPlaneLoad(file,Name,Load):
    file.write('{}, 1, 2\n'.format(Name))
    file.write('{}, 3, 3,{}'.format(Name,Load)+'\n')
    file.write('{}, 4, 6\n'.format(Name))

def WriteStep(file,IndID):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    file.write('** Step Displacing'+'\n')
    enter(1)
    file.write('*Step, name=Displacing, nlgeom=YES, inc={}'.format(inc)+'\n')
    file.write('*Dynamic,application=QUASI-STATIC\n') #, TIME INTEGRATOR=BWE, INCREMENTATION=AGGRESSIVE, IMPACT=NO, initial=NO 
    file.write('{},{},{},{}'.format(t0,tend,tmin,tmax)+'\n')
    if TimeIncrements:
        file.write('*CONTROLS, PARAMETERS=TIME INCREMENTATION\n')
        file.write('12,12,12,12,12,20,20,20,20,5,\n')
    if FieldDisplacement:
        file.write('*CONTROLS,PARAMETERS=FIELD,FIELD=DISPLACEMENT\n')
        file.write(' 0.025, 0.05\n')
        file.write('*CONTROLS,PARAMETERS=FIELD,FIELD=ROTATION\n')
        file.write('0.050, 0.10\n')
    if LineSearch:
        file.write('*CONTROLS, PARAMETERS=LINE SEARCH \n')
        file.write('4, 4.0, 0.25, 0.25, 0.15\n')
            
    enter(1)
    file.write('** BOUNDARY CONDITIONS\n')
    file.write('*Boundary\n')
    WriteDisp = Disp*(1-2*(MPB=='3PB'))
    if MPB=='MMB' or MPB=='DCB':
        file.write('{}, 1, 1\n'.format('Loads'))
        file.write('{}, 3, 3,{}\n'.format('Loads',WriteDisp))
        file.write('{}, 5, 6\n'.format('Loads'))  
    elif MPB=='FSP' or MPB=='SSCS':
        file.write('{}, 1, 1,{}\n'.format('Loads',WriteDisp))
        file.write('{}, 2, 6\n'.format('Loads'))     
    elif MPB=='Test':
        file.write('{}, 3, 3,{}\n'.format('Loads',WriteDisp))
        file.write('{}, 1\n'.format('RSymm'))
    else:        
        WriteOutOfPlaneLoad(file,'Loads',WriteDisp)
    if (Shape=='Coupon' and sk_L <= 2):
        file.write('*Boundary\n')
        file.write('{}, 1\n'.format('RSymm'))
    file.write('*Boundary\n')
    file.write('Supports, 1, 6\n')
    if MPB =='3PB':
        file.write('*Boundary\n')
        file.write('Center, 2\n')
        file.write('*Boundary\n')
        file.write('CNode, 1, 2\n')
    enter(1)
    
def WriteOutputReq(file):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    file.write('*OUTPUT, HISTORY, FREQ=1\n')
    file.write('*NODE OUTPUT, NSET=Supports'+'\n')
    file.write('RF,U'+'\n')
    file.write('*NODE OUTPUT, NSET=Loads'+'\n')
    file.write('RF,U'+'\n')
    if Energy: file.write('*OUTPUT, HISTORY,variable = PRESELECT\n')
    
    enter(1)
    for Output in ['FREQ={}\n'.format(FieldFreq),'time interval={},Time marks=YES'.format(tmax)]:
        
        file.write('*Output, field,{}\n'.format(Output)+'\n')# time interval=0.05'+'\n')
        file.write('*Node Output'+'\n')
        file.write('U'+'\n')
        if Strain:
            file.write('*Element Output, directions=YES'+'\n')
            file.write('EE, S,Sk,Sm,Sf'+'\n')
            
        if Coh:
            for CohOut in (['Coh'] + (['COH_Bridge'] if superpose else [])):
                enter(1)
                file.write('*ELEMENT OUTPUT, ELSET={}'.format(CohOut)+'\n')
                file.write('SDEG,  DMICRT, MMIXDME, MMIXDMI'+'\n') 
    file.write('*End Step'+'\n')


def WriteInteraction_Sup(file):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    file.write('** Interaction Properties'+'\n')
    enter(1)
    file.write('*Surface Interaction, name=SURFS\n')
    file.write('*Friction\n')
    file.write('{}\n'.format(Int_Fric))

def WriteLayup(file,Parts):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    file.write('*ORIENTATION, SYSTEM=R, NAME=OID_T'+'\n')
    file.write('      1.,          0.,          0.,          0.,          1.,          0.'+'\n')
    file.write('   3,         0.'+'\n')
    if Coh:
        file.write('*ORIENTATION, SYSTEM=R, NAME=OID_COH'+'\n')
        file.write('      1.,          0.,          0.,          0.,          1.,          0.'+'\n')
        file.write('   3,         90.'+'\n')
    enter(1)
    file.write('** Section: SkinCompositeLayup'+'\n')
    Section = 'Shell' if ElType == 'SC8R' else 'Solid'    
    for Part in Layup.keys():
        for i,layup in enumerate(Layup[Part]):
            Layer = float(i) if (Part=='Stringer' and Plydrop!=0) else i/(len(Layup[Part])/(ttt[Part]))
            if Layer.is_integer():
                
                if (Plydrop!=0 and Part=='Stringer'):
                    if ElPlyDrop>0 or ((i+1)/ElPlyDrop).is_integer():next
                    else: continue
                    file.write('*{0} Section, elset={2}_L{1:1d}, composite, layup={2}CL_L{1:1d}, orientation=OID_T,stack direction=3\n '.format(Section,int(Layer),Part))
                    # for j in range(len(Layup['Stringer'])-1- int(Layer),len(Layup['Stringer'])):#+1):
                    for j in range(0,int(Layer)+1):#):

                        file.write('{0},{1},{2},{3},P{4:1d}'.format(Lamina.loc[Material[Part],'t'],3,Material[Part],Layup[Part][j],j+1)+'\n')
                else:
                    file.write('*{0} Section, elset={2}_L{1:1d}, composite, layup={2}CL_L{1:1d}, orientation=OID_T,stack direction=3\n '.format(Section,int(Layer),Part))

                    for j in range(int(len(Layup[Part])/(ttt[Part])*int(Layer)),int(len(Layup[Part])/(ttt[Part])*(int(Layer)+1))):
                        file.write('{0},{1},{2},{3},P{4:1d}'.format(Lamina.loc[Material[Part],'t'],3,Material[Part],Layup[Part][j],j+1)+'\n')
            

def WriteCoh(file,CohName,CohSet):
    Adh = Adhesive.loc[CohName]
    file.write('*Material, name={}'.format(CohName)+'\n')
    file.write('*Density\n')
    file.write(str(Adh['density'])+'\n')
    file.write('*Elastic, type=traction\n')
    file.write('{0},{1},{1}'.format(Adh['KI'],Adh['Ksh'])+'\n')
    file.write('*DAMAGE INITIATION,CRITERION=QUADS\n')
    file.write('{0},{1},{1}'.format(Adh['sigc'],Adh['tauc'])+'\n')
    file.write('*damage evolution, type=energy, softening=linear, mixed mode behavior=BK, POWER={}'.format(Adh['etaBK'])+'\n')
    file.write('{0},{1},{1}'.format(Adh['GIc'],Adh['GIIc'])+'\n')

    file.write('*COHESIVE SECTION,elset={}, material={},THICKNESS=specified, response=traction separation,controls=ctrs, orientation=OID_COH\n'.format(CohSet,CohName))
    file.write('1.0,\n')
    
def WriteMaterials(file,Parts):
    enter = lambda a: [file.write('**\n') for i in range(a)]
    file.write('** MATERIALS'+'\n')
    enter(1)
    for Lam in list(set(Material.values())):
        file.write('*Material, name={}'.format(Lam)+'\n')
        file.write('*Density\n')
        file.write(str(Lamina.loc[Lam,'density'])+'\n')
        if ElType == 'SC8R':
            file.write('*Elastic, type=LAMINA\n')
            file.write('{},{},{},{},{},{}'.format(Lamina.loc[Lam,'E1'],Lamina.loc[Lam,'E2'],\
                   Lamina.loc[Lam,'v12'],Lamina.loc[Lam,'G12'],Lamina.loc[Lam,'G13'],Lamina.loc[Lam,'G23'])+'\n')
        else:
            file.write('*Elastic, type=ENGINEERING CONSTANTS\n')
            file.write('{0},{1},{1},{2},{2},{3},{4},{5},\n {6}\n'.format(Lamina.loc[Lam,'E1'],\
                       Lamina.loc[Lam,'E2'],Lamina.loc[Lam,'v12'],Lamina.loc[Lam,'v23'],\
                       Lamina.loc[Lam,'G12'],Lamina.loc[Lam,'G13'],Lamina.loc[Lam,'G23']))
 
    if Coh:
        WriteCoh(file,Coh_mat,'COH')
        file.write('*section control,name=ctrs,viscosity={}\n'.format(Visc))
        
    if superpose: 
        file.write('*ELCOPY, element shift=1000000, oldset=COH, new set=COH_Bridge, shift nodes=0\n')
        WriteCoh(file,Coh_Tri,'COH_Bridge')
        
