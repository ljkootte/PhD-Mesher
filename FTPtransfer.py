# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:43:58 2019

@author: ljkootte
"""

import paramiko 
import os
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are 
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise
                import os


def GetClusterCoreUsage(ssh):
    
    _, stdout, stderr = ssh.exec_command('LOCALnodeload.pl')
    output = stdout.read().decode("utf-8").split('\n')
    Df = pd.DataFrame(data = [f.split() for f in output[2:-1]], columns= output[0].split())
    Df = Df[np.array(Df['Properties'].str.contains('asm'))]
    Df.loc[Df['State/jobs']=='free','State/jobs']= 0 
    
    for col in ['State/jobs','Np']:
        Df[col] = pd.to_numeric(Df[col], errors='coerce')
    Cpu_avail = max(Df['Np']-Df['State/jobs'])
    print('max available cores on a single nodes: ', Cpu_avail)
    return Df,  Cpu_avail


def executeCommand(ssh,string):
    _, stdout, stderr = ssh.exec_command(string)
    print(stderr.read().decode("utf-8"))
    return stdout.read().decode("utf-8").split('\n')

def GetAbaqusLicenses(ssh,get=''):
    # executeCommand(ssh,'export PATH="/opt/ud/abaqus-2021/Commands/abaqus:$PATH"')
    # executeCommand(ssh,'export PATH="/opt/ud/torque-4.2.10/bin/qsub:$PATH"')
    # # executeCommand(ssh,'module load abaqus/2021')
    output = executeCommand(ssh,'/opt/ud/abaqus-2021/Commands/abaqus licensing lmstat -f cae')
    for i,out in enumerate(output):
        if 'Users of cae:' in out:
            if get!='Usage': print(out)

    output = executeCommand(ssh,'/opt/ud/abaqus-2021/Commands/abaqus licensing lmstat -f abaqus')
    Istart= np.inf ; Istop= np.inf
    for i,out in enumerate(output):
        if 'Users of abaqus:' in out:
            if get!='Usage': print(out)
            Istart = i+5
        if i>Istart and out=='':
            if get!='Usage': print(out)
            Istop = i
            break
            
    Df2 = pd.DataFrame(data = [f.split(',') for f in output[Istart:Istop]], columns= ['Name','Start','Licenses'])
    Df2['Licenses'] = pd.to_numeric(Df2['Licenses'].str.replace(" licenses",""), errors='coerce')
    Df2.dropna(inplace=True)
    for ind in Df2.index:    
        if 'Shared' in Df2.loc[ind,'Name'] or 'LocalAdmin' in Df2.loc[ind,'Name']:
            Df2.loc[ind,'Name'] = Df2.loc[ind,'Name'].split()[1] #Df2.loc[ind,'Name'].split()[0]+' '+
        else: 
            Df2.loc[ind,'Name'] = Df2.loc[ind,'Name'].split()[0]
        
    Df2 = Df2.drop('Start', axis=1)
    Df2['Licenses'] = Df2.groupby(['Name'])['Licenses'].transform('sum')
    Df2 = Df2.drop_duplicates(subset=['Name'])
    Df2.set_index('Name',inplace =True)
    Df2.sort_values(['Licenses'],ascending=False,inplace=True)
    # if get =='Usage': return (450-sum(Df2['Licenses']))
    if get =='Usage': return Df2
    print(Df2)    
    Cpu_avail = int(((450-sum(Df2['Licenses']))/5)**(1/0.422))
    print('Max tokens available: ', Cpu_avail)
    
    return Df2,Cpu_avail

def get_Password():
    import tkinter as tk 
    app = tk.Tk()   
    PASSWORD = tk.StringVar() #Password variable
    tk.Entry(app, textvariable=PASSWORD, show='*').pack() 
    button = tk.Button(app, text='Ok',command=app.destroy).pack()   
    app.bind('<Return>',lambda e: app.destroy())
    app.mainloop() 
    return PASSWORD.get()

def ConnectToCluster(HOST,PORT,USERNAME,PASSWORD):
    global ssh, shell
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, PORT,username=USERNAME, password=PASSWORD)
    shell = ssh.invoke_shell()
    return ssh,shell
    
def ClusterParam():
    import getpass
    import keyring
    HOST = 'hpc12.tudelft.net'
    PORT = 22
    USERNAME = 'ljkootte' 
    if keyring.get_password("system", USERNAME)==None:
        PASSWORD = getpass.getpass('Password:\n')
        keyring.set_password("system", USERNAME, PASSWORD)
    else:
        PASSWORD = keyring.get_password("system", USERNAME)
    return HOST,PORT,USERNAME,PASSWORD

def GetSFTP():
    global sftp
    HOST,PORT,USERNAME,PASSWORD = ClusterParam()
    print ('Password input succesful')
    ssh,shell  = ConnectToCluster(HOST,PORT,USERNAME,PASSWORD)
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USERNAME, password=PASSWORD)
    sftp = MySFTPClient.from_transport(transport)
    return ssh,shell,sftp

def RunCluster(source_path,Subfile,sftp,ssh):

    target_path = '/home/scratch/ljkootte/'+source_path.split('/')[-1]

    sftp.mkdir(target_path, ignore_existing=True)
    sftp.put_dir(source_path, target_path)

    Runcommand = lambda command: print(ssh.exec_command(command)[1].read())
    Runcommand('cd {0};dos2unix {1};qsub {1}'.format(target_path,Subfile))
    # Runcommand(''.format(Subfile))
    #/opt/ud/torque-4.2.10/bin/
    return target_path+'/'+source_path.split('/')[-1]


def PlotParams(): # This sets the plotting style
    import matplotlib.pylab as pylab
    from matplotlib import rcParams,rc,cm,font_manager
    params = {
         'axes.labelsize': 'medium',
         'axes.titlesize':'medium',
         'xtick.labelsize':'medium',
         'ytick.labelsize':'medium',
         'font.family':'Times New Roman',
         'legend.fontsize':'medium',
         'font.serif' : ['Times New Roman'] + rcParams['font.serif'],
         'font.size': 10,
         'font.weight':'light'}
    pylab.rcParams.update(params)
    # rcParams["font.serif"] = 
    global p,Cols
    # del font_manager.weight_dict['roman']
    # font_manager._rebuild()
    return

def Plotsta(sftp,Filename,tend):
    import time
    time_to_wait = 600
    sleeptime = 1
    time_counter = 0
    while time_counter<time_to_wait:
        try: 
            pd.read_csv(sftp.open(Filename+'.sta'),header=2,skiprows=range(3,5), usecols=range(9), sep='\s+')            
            break
        except: 
            time.sleep(sleeptime)
            time_counter += sleeptime

    import matplotlib.animation as animation
    # Create figure for plotting
    PlotParams()
    fig, axs = plt.subplots(3, sharex=True)
    fig.tight_layout()
    # Initialize communication with TMP102
    ani = animation.FuncAnimation(fig, animate, fargs=(sftp,axs,Filename,tend), interval=2000)
    plt.show()
    # This function is called periodically from FuncAnimation
def animate(i,sftp,axs,Filename,tend):
    Df = pd.read_csv(sftp.open(Filename+'.sta'),header=2,skiprows=range(3,5), usecols=range(9), sep='\s+').dropna()
    xs = Df['INC']
    # Draw x and y lists
    # for ax in axs: ax.label_outer()
    for ax in axs: ax.clear()
    
    for i, out in enumerate(['TOTAL.1','TOTAL','INC.1']):
        axs[i].plot(xs, Df[out])
        axs[i].set_xlim(0,axs[i].get_xticks()[-1])
        axs[i].grid()
        if i==0:
            axs[0].set_ylim(0,tend)
        else:
            axs[i].set_ylim(0,axs[i].get_yticks()[-1])

    # Format plot
    axs[0].set_xlabel('Increment number')
    for i, out in enumerate(['total time','iterations','timestep']):
        axs[i].set_ylabel(out)
    return

def Monitor():
    ssh,shell,sftp =  GetSFTP()
    import matplotlib.animation as animation
    # Create figure for plotting
    PlotParams()
    fig, ax = plt.subplots()
    # Initialize communication with TMP102
    ani = animation.FuncAnimation(fig, animate2, fargs=(ssh,fig,ax), interval=5000)
    plt.show()
    # This function is called periodically from FuncAnimation
def animate2(i,ssh,fig,ax):
    global Df
    Df = GetAbaqusLicenses(ssh,'Usage')
    ax.clear()
    ax.bar(Df.index,Df['Licenses'])
    ax.axhline(y=20)
    ax.set_xticklabels(Df.index, rotation=45, ha='right')
    for bar in ax.patches:
        bar.set_facecolor('#888888')
    try: 
        pos = Df.index.get_loc('ljkootte')
        ax.patches[pos].set_facecolor('#aa3333')
    except: next
    totLic = sum(Df['Licenses']) ; totUs = len(Df.index)
    fig.suptitle('Number of available licenses: '+str(450-totLic))
    fig.tight_layout()
    
    from datetime import datetime    
    import os
    try: 
        Df = Df.T
        Df_New = pd.DataFrame({'0_Total': int(totLic) , '1_Users': int(totUs),\
                  '2_Top1': int(Df.iloc[-1].nlargest(3)[0]),\
                  '3_Top2': int(Df.iloc[-1].nlargest(3)[1]),\
                  '4_Top3': int(Df.iloc[-1].nlargest(3)[2])},\
                              index= [datetime.now().strftime("%d/%m/%Y %H:%M:%S")])   
        
        if os.path.exists('Df_Lic.csv'):
            Df_base = pd.read_csv('Df_Lic.csv',index_col=0)
            Df_base = Df_base.append(Df_New,sort=False).fillna(0)
        else:
            Df_base = Df_New
        Df_base.sort_index(axis=1).to_csv('Df_Lic.csv')
    except: next
    return
# Df2['Licenses']

# Df = GetAbaqusLicenses(ssh,'Usage')
# Monitor()