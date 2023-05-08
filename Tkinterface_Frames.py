# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 11:57:53 2021

@author: ljkootte
"""


from tkinter import *
import tkinter.ttk
from PIL import ImageTk, Image
import pickle
import os.path
import pandas as pd
import numpy as np

class App(Frame,):
    global Vars
    if os.path.isfile('Vars'):
        try:
            infile = open('Vars','rb')
            Vars = pickle.load(infile, encoding='bytes')
            infile.close()
        except: Vars= {}
        # self.previous = True
    else:
        Vars = {}
        # self.previous = False
        
    def __init__(self,master,Window):

        self.Window = Window
        Frame.__init__(self,master)
        tkinter.ttk.Frame(self.master, borderwidth=5, relief="sunken", width=200, height=100)
        self.master = master
#        self.master.resizable(False, False)
        
        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window()
        self.WindInt=0

        self.Start_Model()
            
    #Creation of init_window
    def init_window(self):
        
        # changing the title of our master widget      
        self.master.title(self.Window)
        tkinter.ttk.Separator(self.master, orient=VERTICAL).grid(column=1, row=0, rowspan=8, sticky='ns')
        self.master.withdraw()
        
    def Resize(self):        
        col_count, row_count = self.Top.grid_size()
        print(col_count,row_count)
        for col in range(col_count):
            # if col==1:continue
            self.Top.grid_columnconfigure(col, minsize=700/(col_count+2))
        
        for row in range(row_count):
            self.Top.grid_rowconfigure(row, minsize=480/(row_count+1))

    def CheckVars(self,var2,startvar):
        if var2 in Vars.keys(): return Vars[var2]  
        else: return startvar

    def Start_Model(self):        
        self.var = {}
        self.CreateTopLevel()
        self.Top.title('Page 1')
        self.PlaceText([0,0],'Model Name')
        self.var['Direc'] = self.WriteWindow([0,2])
        self.PlaceText([1,0],'Test configuration')

        self.var['MPB'] = self.RadioButton({'FSP':'MSP','7PB':'7PB','6PB':'6PB','4PB':'4PT','3PB':'3PB','SSCS':'SSCS','DCB':'DCB','MMB':'MMB','Test':'Test'},\
                                            {'FSP':None,'7PB':None,'6PB':None,'4PB':None,'3PB':None,'SSCS':None,'DCB':None,'MMB':None,'Test':None},1,Active = self.CheckVars('MPB',''))



        self.PlaceText([2,0],'Geometry')
        self.var['Shape'] = self.RadioButton({'Hat':'Hat-stringer','Doubler':'Doubler','Coupon':'Coupon'},{'Hat':None,'Doubler':None,'Coupon':None},2,Active = self.CheckVars('Shape',''))
        self.PlaceText([3,0],'Check boxes')        
        self.var['Coh'],self.Coh = self.CheckWindow('Cohesive',[3,2],self.Superp_Clickable,TF = self.CheckVars('Coh',False))
        self.var['Superpose'],self.Superp = self.CheckWindow('Superpose',[3,3],None,TF = self.CheckVars('Superpose',False),State= DISABLED)
        self.PlaceText([4,0],'Element type:')        
        self.var['ElType'] = self.RadioButton({'SC8R':'SC8R','CSS8':'CSS8','C3D8R':'C3D8R','S4R':'S4R'},\
                  self.Coh_clickable,4,Active = self.CheckVars('ElType',''))

        self.PlaceText([5,2],'Skin',columnspan=1,sticky='s')
        self.PlaceText([5,4],'Stringer',columnspan=1,sticky='s')
        self.PlaceText([6,0],'Layup:')
        self.var['Layup'] = {'Skin':self.WriteWindow([5,2], str(Vars['Layup']['Skin'])[1:-1] if "Layup" in Vars.keys() else  '-45,45,0,90,-45,45,45,-45,90,0,45,-45' ,StringInt = 'String')}
        self.var['Layup']['Stringer'] = self.WriteWindow([5,4],str(Vars['Layup']['Stringer'])[1:-1] if "Layup" in Vars.keys() else '45,-45,0,90,45,-45,-45,45,90,0,-45,45',StringInt = 'String')       
        self.PlaceText([7,0],'Elements Through the Thickness:')
        self.var['ttt'] = {'Skin':self.WriteWindow([7,2],'1',columnspan=1,StringInt = 'Int')}
        self.var['ttt']['Stringer'] = self.WriteWindow([7,4],'1',columnspan=1,StringInt = 'Int')

        TopGrid = self.Top.grid_size()[0]+2
        self.OkButton([TopGrid,2],command = lambda: self.ResetVars(),text='Reset')
        self.OkButton([TopGrid,3],command = lambda: self.SwitchWindows(1),text='Next')
        self.OkButton([TopGrid,4],command = lambda: self.client_exit(),text='Close')

        
        self.Resize()
        
        # elif self.Window == 'Second':
        # self.Size_model()

    def Size_model(self):        
        self.var = {}

        self.CreateTopLevel()
        self.Top.title('Page 2')

        self.PlaceText([0,1],'Specimen Length')
        self.PlaceText([0,2],'Specimen Width')
        self.var['sk_L'] = self.WriteWindow([1,1],StringInt='Double',Start = self.CheckVars('sk_L',{'FSP':685,'7PB':140,'4PB':140,'3PB':25}[Vars['MPB']]),columnspan=1)
        self.var['sk_W'] = self.WriteWindow([1,2],StringInt='Double',Start = self.CheckVars('sk_W',{'FSP':770,'7PB':140,'4PB':120,'3PB':200}[Vars['MPB']]),columnspan=1)



        if Vars['Shape']=='Hat':
            Hat  = {'str_Wfla':('Stringer Flange',self.CheckVars('str_Wfla',27)),\
                    'str_Wtop':('Stringer Top',self.CheckVars('str_Wtop',30.6)),\
                    'str_H':('Stringer Heigth',self.CheckVars('str_H',32.7)),\
                    'str_ang':('Stringer Angle',self.CheckVars('str_ang',70)),\
                    'radius':('Stringer Radius',self.CheckVars('str_ang',5))} 
            for i,key in enumerate(Hat):
                self.PlaceText([2,1+i],Hat[key][0])
                self.var[key] = self.WriteWindow([3,1+i],StringInt='Double',Start = self.CheckVars(key,Hat[key][1]),columnspan=1)





        # elif Vars['Shape']=='Doubler':
        #     Hat = {'str_Wfla':('Stringer Flange',self.CheckVars('str_Wfla',27))}
             
        # for i,key in enumerate(Hat):
        #     self.PlaceText([2,1+i],Hat[key][0])
        #     self.var[key] = self.WriteWindow([3,1+i],StringInt='Double',Start = self.CheckVars(key,Hat[key][1]),columnspan=1)


        # elif Vars['Shape']=='Coupon':


        self.EndButtons(self.Top.grid_size()[0])


    def Config_Model(self):        
        self.var = {}

        self.CreateTopLevel()
        self.Top.title('Page 3')
        configuration = {}
        if Vars['MPB'] in ['3PB','4PB','7PB']: configuration['Sup_Y'] = ('Y-distance Support',self.CheckVars('Sup_Y',{'7PB':20.,'4PB':54,'3PB':Vars['sk_W']/2}[Vars['MPB']]))
        if Vars['MPB'] in ['4PB','7PB']: configuration['Sup_X'] = ('X-distance Support',self.CheckVars('Sup_X',{'7PB':20.,'4PB':40.}[Vars['MPB']]))
        if Vars['MPB']=='7PB': configuration['Load_X'] = ('X-distance Load',self.CheckVars('Load_X',{'7PB':Vars['sk_L']/2}[Vars['MPB']]))
        if Vars['MPB'] in ['3PB','7PB']: configuration['Load_Y'] = ('Y-distance Load',self.CheckVars('Load_Y',{'7PB':34.,'3PB':34.}[Vars['MPB']]))


        if Vars['MPB'] in ['3PB','4PB','7PB']:
            for i,key in enumerate(configuration.keys()):
                self.PlaceText([0,i],configuration[key][0])
                self.var[key] = self.WriteWindow([1,i],Start=configuration[key][1],columnspan=1,StringInt='Double')
    
            self.PlaceText([2,0],'Indenter Radius')
            self.PlaceText([2,1],'Indenter Length')
            self.PlaceText([2,2],'Contact Area Length')
            self.var['ind_ra'] = self.WriteWindow([3,0],Start=self.CheckVars('ind_ra',12.5),columnspan=1,StringInt='Double')
            self.var['ind_L'] = self.WriteWindow([3,1],Start=self.CheckVars('ind_L',4.0),columnspan=1,StringInt='Double')
            self.var['Surf_sq'] = self.WriteWindow([3,2],Start=self.CheckVars('Surf_sq',self.var['ind_ra'].get()*2),columnspan=1,StringInt='Double')



        if Vars['MPB'] == 'FSP': 
            self.PlaceText([0,2],'Stringer placement')
            self.var['Str_Loc'] = self.WriteWindow([1,2], str(Vars['Str_Loc'])[1:-1] if "Str_Loc" in Vars.keys() else '62.6, 273.6, 489.6, 700.6' ,StringInt = 'String')
        elif Vars['MPB']=='Coupon': Vars['Str_Loc'] = [Vars['str_HalfWidth']]
        elif Vars['Shape']=='Doubler' and Vars['MPB'] == '4PB': Vars['Str_Loc'] = [Vars['sk_W']]
        else: Vars['Str_Loc'] = [Vars['sk_W']/2]

        self.EndButtons(self.Top.grid_size()[0])

    def SkinMatprops(self):        
        self.var = {}

        self.CreateTopLevel()
        self.Top.title('Page 4')
        
        
        Vars['Lamina'] = self.CheckVars('Lamina', pd.DataFrame(data= np.zeros((5,9)), index=[f'MatName {i}' for i in range(5)],\
                    columns = ['density','E1','E2','v12','v23','G12','G13','G23','t']))

        self.PlaceText([1,0],'Name')
        for i,key in enumerate(Vars['Lamina'].columns):
            self.PlaceText([1,1+i],key)

        for j, Lam in enumerate(Vars['Lamina'].index):
            self.var[Lam]={}
            self.var[Lam]['Name'] = self.WriteWindow([2+j,0],StringInt='String',Start = Lam,columnspan=1)
            for i,key in enumerate(Vars['Lamina'].columns):
                self.var[Lam][key] = self.WriteWindow([2+j,1+i],StringInt='Double',Start = Vars['Lamina'].loc[Lam,key],columnspan=1,width=9)


        # self.PlaceText([4+j,2],'Skin laminate',columnspan=2)
        # self.PlaceText([4+j,5],'Stringer laminate ',columnspan=2)
        # self.var['Material'] = {'Skin':self.WriteWindow([5+j,2], Vars['Layup']['Skin'] if "Material" in Vars.keys() else 'IM7/977-3' ,StringInt = 'String',columnspan=2)}
        # self.var['Material']['Stringer'] = self.WriteWindow([5+j,5],Vars['Layup']['Stringer'] if "Material" in Vars.keys() else 'IM7/977-3',StringInt = 'String',columnspan=2)       

        self.EndButtons(self.Top.grid_size()[0])

    def SelectMat(self):
        self.var = {}

        self.CreateTopLevel()
        self.Top.title('Page 6')

        self.PlaceText([0,2],'Skin laminate',columnspan=2)
        self.PlaceText([0,4],'Stringer laminate ',columnspan=2)
        # self.var['Material'] = {'Skin':self.WriteWindow([1,2], Vars['Material']['Skin'] if "Material" in Vars.keys() else Vars['Lamina'].index[0] ,StringInt = 'String',columnspan=2)}
        # self.var['Material']['Stringer'] = self.WriteWindow([1,5],Vars['Material']['Stringer'] if "Material" in Vars.keys() else Vars['Lamina'].index[0],StringInt = 'String',columnspan=2)       
    

        # if Vars['Coh']:
        #     self.PlaceText([3,2],'Cohesive Name')
        #     self.var['Coh_mat'] = self.WriteWindow([4,1],Start=self.CheckVars('Coh_mat',Vars['Adhesive'].index[0]),columnspan=1,StringInt='String')
    
        #     try: 
        #         if Vars['superpose']:
        #             self.PlaceText([3,5],'Superposed Name')
        #             self.var['Coh_Tri'] = self.WriteWindow([4,2],Start=self.CheckVars('Coh_Tri',Vars['Adhesive'].index[1]),columnspan=2,StringInt='String')
        #     except: next
            
        
        self.var['Material'] ={}
        for i,lam in enumerate(['Skin','Stringer']):
            # try: 
            self.var['Material'][lam]= self.DropDown(Vars['Lamina'].index,[1,2+2*i],start = Vars['Material'][lam])
            # except: 
            #     self.var['Material'][lam]= self.DropDown(Vars['Lamina'].index,[1,2+2*i],start = '')
        
        
        
        self.EndButtons(self.Top.grid_size()[0])

    def Cohprops(self):        
        self.var = {}

        self.CreateTopLevel()
        self.Top.title('Page 5')

        Vars['Adhesive'] = self.CheckVars('Adhesive', pd.DataFrame(data= np.zeros((5,8)), index=[f'CohName {i}' for i in range(5)],\
                    columns = ['density','GIc','GIIc','sigc','tauc','KI','Ksh','etaBK']))

        self.PlaceText([1,0],'Name')
        for i,key in enumerate(Vars['Adhesive'].columns):
            self.PlaceText([1,1+i],key)

        for j, Lam in enumerate(Vars['Adhesive'].index):
            self.var[Lam]={}
            self.var[Lam]['Name'] = self.WriteWindow([2+j,0],Start = Lam,columnspan=1)
            for i,key in enumerate(Vars['Adhesive'].columns):
                self.var[Lam][key] = self.WriteWindow([2+j,1+i],StringInt='Double',Start = Vars['Adhesive'].loc[Lam,key],columnspan=1,width=9)

        self.EndButtons(self.Top.grid_size()[0])


    def AnalysisParameters(self):
        self.var = {}

        self.CreateTopLevel()
        self.Top.title('Page 6')

        self.PlaceText([0,1],'Friction Name')
        self.PlaceText([0,2],'Friction Value')
        
        self.var['Int_Name'] = self.WriteWindow([1,1],StringInt='String',Start = self.CheckVars('Int_Name','SURFS'),columnspan=1)
        self.var['Int_Fric'] = self.WriteWindow([1,2],StringInt='Double',Start = self.CheckVars('Int_Fric',0 if Vars['MPB'] =='MMB' else 0.2),columnspan=1)

        # self.PlaceText([0,1],'Specimen Length')
        # self.var['sk_L'] = self.WriteWindow([1,1],StringInt='Double',Start = self.CheckVars('sk_L',{'FSP':685,'7PB':140,'4PB':140,'3PB':25}[Vars['MPB']]),columnspan=1)
        self.PlaceText([2,1],'Applied displacement')
        try: 
            self.var['Disp'] = self.WriteWindow([3,1],StringInt='Double',Start = self.CheckVars('Disp',{'DCB':20,'3PB':-12,'4PB':-12,'7PB':-20,'FSP':-4,'SSCS':-4,'Test':-45}[Vars['MPB']]),columnspan=1)
        except: 
            self.var['Disp'] = self.WriteWindow([3,1],StringInt='Double',Start = self.CheckVars('Disp',-20,columnspan=1))

        self.PlaceText([2,2],'Loading rate (distance/s)')
        self.var['Loadspeed'] = self.WriteWindow([3,2],StringInt='Double',Start = self.CheckVars('Loadspeed',4),columnspan=1)
        self.EndButtons(self.Top.grid_size()[0])


    def EndButtons(self,TopGrid):
        self.OkButton([TopGrid+2,2],command = lambda: self.SwitchWindows(-1),text='Previous')
        self.OkButton([TopGrid+2,3],command = lambda: self.SwitchWindows(1),text='Next')
        self.OkButton([TopGrid+2,4],command = lambda: self.client_exit(),text='Close')
        self.Resize()

        
    def CreateTopLevel(self):
        self.Top = Toplevel()
        self.Top.maxsize(800, 480)
        self.Top.geometry("800x480+500+300")
        self.Top.state('zoomed')

        self.Top.focus_force()
        self.Top.update()

    def GetVar(self,var1):
        var1 =  var1.get()
        if type(var1) is str and ',' in var1: var1 = [float(x) for x in var1.split(',')]
        return var1
            
    def UpdateVars(self):
        for v in self.var.keys():
            if type(self.var[v]) is dict: 
                for i,w in enumerate(self.var[v].keys()):
                    if i==0: Vars[v] = {w:self.GetVar(self.var[v][w])}
                    else: Vars[v][w] = self.GetVar(self.var[v][w])
            else:
                Vars[v] = self.GetVar(self.var[v])        

    def UpdateMatVars(self,MatCoh='Lamina'):
        # if MatCoh == 'Mat':
        #     Vars['Lamina'] = pd.DataFrame(data= [],columns = ['density','E1','E2','v12','v23','G12','G13','G23','t'])
        for j,v in enumerate(self.var.keys()):
            N = self.GetVar(self.var[v]['Name'])
            del self.var[v]['Name'] 
            if j == 0 :
                Vars[MatCoh] = pd.DataFrame(data= [],columns = self.var[v].keys())
            for i,w in enumerate(self.var[v].keys()):
                # if i==0: continue
                Vars[MatCoh].loc[N,w] = self.GetVar(self.var[v][w])


    
    
    def Dependables(self):
        Vars['tend']=np.abs(Vars['Disp'])/Vars['Loadspeed']

        # self.EndButtons(self.Top.grid_size()[0])

        # tend =  # 0.4
        # inc  = 10000
        # t0   = 1e-4*tend if Coh else 0.01*tend
        # tmin = 1e-10
        # tmax = (0.1 if MPB=='FSP' else 0.1)/Loadspeed
        # if sk_L<=2: tmax= t0*5
        # LineSearch = True ; FieldDisplacement = True; RunTemp = True
        # TimeIncrements = False if Shape=='Coupon' else True
        
        # FieldFreq = 1 if (Shape=='Coupon' or not Coh) else 5 
        # Energy = True ; Strain =True
        
            
        # #Cohesive Zone
        # Visc  = 1E-5*tend  # 1.0E-7
        # if MPB=='FSP' :  L_Coh = 0.2
        # elif MPB=='4PB': L_Coh = 0.05 
        # else:  L_Coh = 0
        # Inserts = {} #'Stringer0':{'Right':{'X':sk_L/2,'len':20}}}



        # if Shape == 'Hat':
        #     if radius!=0: Spacing =  Mesh_fla + radius/(np.tan((np.pi-str_ang*np.pi/180.)/2))
        #     elif radius==0: Spacing =  Mesh_glo
        # else: Spacing =  Mesh_fla 
        
        
        # MeshDiv = int(np.round(np.log(Mesh_glo/Mesh_fla)/np.log(3)))
        # if Shape !='Hat' or MeshDiv == 0: Remeshing = False
        
        
        # ElPlyDrop = 1
    

    # def UpdateMatVars(self,MatCoh='Lamina'):
    #     for j,v in enumerate(self.var.keys()):
    #         # N = v #self.GetVar(self.var[v]['Name'])
    #         # del self.var['Name']#[v]['Name'] 
            
    #         if j == 0 :
                
    #             self.keys = list(self.var[v].keys())
    #             self.keys.remove('Name')
    #             Vars[MatCoh] = pd.DataFrame(data= [],columns = self.keys)
    #             print (self.keys)
    #         for i,w in enumerate(self.keys):
    #             Vars[MatCoh].loc[v,w] = self.GetVar(self.var[v][w])
    #     # Vars  = Vars[MatCoh].drop('Name',axis=1)

    def SwitchWindows(self,add=1):
        if self.WindInt==3 or (self.WindInt==4 and Vars['Coh']):
            self.UpdateMatVars('Adhesive' if self.WindInt==4 else 'Lamina')
        else:
            self.UpdateVars()
        self.WindInt+=add
        self.Top.destroy()
        self.Top.update()

        Frame = [self.Start_Model,self.Size_model,self.Config_Model,self.SkinMatprops]
        if self.WindInt>0 and Vars['Coh']: Frame+=[self.Cohprops]
        Frame+= [self.SelectMat,self.AnalysisParameters]
        
        print(self.WindInt,len(Frame))
        if self.WindInt<len(Frame):
            Frame[self.WindInt]()
        else: 
            # self.Dependables()
            self.client_quit()
            # self.client_exit()

    def ResetVars(self):
        global Vars
        if os.path.isfile('Vars'): os.remove('Vars')
        self.var = {}
        Vars = {}
        self.WindInt=0
        self.SwitchWindows(0)


        
    def client_exit(self):
        self.master.destroy()#destroy()
    def client_quit(self):
        self.master.quit()#destroy()

    def Superp_Clickable(self):
        if self.GetVar(self.var['Coh']) == False:
            self.Superp['state']   = DISABLED
            self.Superp.deselect() 
        else:
            self.Superp['state']   = NORMAL


    def Coh_clickable(self):
        if self.GetVar(self.var['ElType']) == 'S4R':
            self.Coh['state']   = DISABLED
            self.Coh.deselect() 
            self.Superp['state']   = DISABLED
            self.Superp.deselect() 
        else:
            self.Coh['state']   = NORMAL
            self.Superp['state']   = NORMAL


    def OkButton(self,coords,command,text='OK'):
        b = Button(self.Top, text=text, command=command).grid(row = coords[0],column = coords[1])

    def PlaceText(self,coords,text,rowspan=1,columnspan=1,sticky=''):
        # let's provide same sample coordinates with the desired text as tuples in a list
        # interate through the coords list and read the coordinates and the text of each tuple
        label = Label(self.Top, text=text)
        label.grid(row = coords[0],column = coords[1],rowspan=rowspan,columnspan=columnspan,sticky=sticky)


    def WriteWindow(self,coords,Start='',StringInt = 'String',columnspan=2,width=15):
        Inp = {'String':StringVar(),'Int':IntVar(),'Double':DoubleVar()}[StringInt]
        # if StringInt=='String': Inp = 
        # elif StringInt=='Int': Inp = 
        # elif StringInt=='Double': Inp = 
        Inp.set(Start)
        Entry(self.Top, bd = 5,textvariable=Inp,width=width).grid(row = coords[0],column = coords[1],columnspan=columnspan,sticky='ew',padx=5)
        return Inp
        

    def CheckWindow(self,text,coords,Command,TF = False,State=NORMAL):
        CheckVar = BooleanVar()
        CheckVar.set(TF)
        C1 = Checkbutton(self.Top, text = text, variable = CheckVar, \
                         onvalue = True, offvalue = False,command = Command,state = State)
        C1.grid(row = coords[0],column = coords[1])
        return CheckVar,C1

    def DropDown(self,text,coords,start = ''):
        variable = StringVar()
        if start!= '': variable.set(start)
        # else: variable.set(text[0])
        # default value
        OptionMenu(self.Top, variable, *text).grid(row = coords[0],column = coords[1])
        return variable
    
    def RadioButton(self,Radio_dict,Command,coords,Active = ''):
        String = StringVar()
        
        X = range(len(Radio_dict.keys()))
        R = {}
        for i, key in enumerate(Radio_dict):            
            R[key] = Radiobutton(self.Top, text=Radio_dict[key], variable=String, value=key,command=Command)
            R[key].grid(row = coords,column = i+2)
            R[key].configure(state = "normal", relief="raised")
            if i==0: R[key].select()
            
        if Active =='': String.set(list(Radio_dict.keys())[0])                  
        else: String.set(Active)                  


        return String


if __name__=='__main__':
    root = Tk()
    root.geometry("800x480+500+300")
    app = App(root,'root')
    # Top = Toplevel()
    # Top.geometry("800x480+2000+300")
    # app2 = App(Top,'Model Definition')

    root.mainloop()
    
# print(Vars)

outfile = open('Vars','wb')
pickle.dump(Vars,outfile)
outfile.close()

from types import SimpleNamespace  
n = SimpleNamespace(**Vars)

#    root = Tk()
#    root.geometry("600x480+2000+300")
#    root.mainloop()
#    root.destroy()    
#window = TK()
#window.title('My computer science glossary')
