# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 16:18:08 2018

@author: lkootte
"""


def WriteBatchFile(MPB,Direc,cpu,mem,Solver,Coh,SubRoutine,RunTemp):
    enter = lambda a: [file.write('\n') for i in range(a)]
    Name = '{}-{}'.format(MPB,Direc)
    with open(MPB+'-'+Direc+"\Sub{}.txt".format(Direc), "w") as file:
        file.write('# Job for Torque PBS 4.2.10\n')
        file.write('#\n')
        file.write('# PBS parameters (see: man qsub)\n')
        file.write('# -----------------------------\n')
        file.write('#PBS -j oe \n')
        file.write('#PBS -l nodes=1:ppn={},mem={}g\n'.format(cpu,mem))    
        file.write('#PBS -M <email<\n')
        file.write('#PBS -m abe\n')
        file.write('#PBS -N {}\n'.format(Name))
        file.write('#PBS -o ${PBS_JOBNAME}.LOG \n')
        file.write('#PBS -q <asm>\n')
        file.write('#PBS -rn\n')
        file.write('#PBS -S /bin/csh\n')
        file.write('# -------------------------------------\n')
        file.write('#\n')
        if RunTemp: ToTemp(file)
        else: file.write('cd ${PBS_O_WORKDIR}\n')
        file.write('#\n')
        file.write('module load abaqus/2019\n')
        file.write('#\n')
        WriteJob = 'abaqus job=$PBS_JOBNAME cpus={}'.format(cpu)
        if mem!=None: WriteJob += ' memory="{} gb'.format(mem)
        if Solver =='Explicit': WriteJob += ' double=both'
        file.write(WriteJob+'\n')
        file.write('wait\n')
        if RunTemp: ReturnTemp(file)
        file.write('cd ${PBS_O_WORKDIR}\n')
        %file.write('abaqus cae noGUI="/home/.../CreateDisplay.py" -- ${PBS_O_WORKDIR}\n')
        %if not Coh: file.write('abaqus cae noGUI="/home/.../CreateOutFieldsSK.py" -- ${PBS_O_WORKDIR}\n')
        %elif Coh: file.write('abaqus cae noGUI="/home/.../CreateOutFieldsSDEG.py" -- ${PBS_O_WORKDIR}\n')
        %file.write('python "/home/.../PlotFemExp/CombinedPlot.py" -- ${PBS_O_WORKDIR}\n')
        file.write('exit 0\n')
        
    return
        
        

