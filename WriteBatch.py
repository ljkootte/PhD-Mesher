# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 16:18:08 2018

@author: lkootte
"""

def ToTemp(file):
    # create a temporary directory in /var/tmp
    file.write('set TMP=/var/tmp/${PBS_JOBID}\n')
    file.write('mkdir -p ${TMP}\n')
    file.write('echo "Temporary work dir: ${TMP}"\n')
    file.write('\n')
    file.write('# copy the input files to ${TMP}\n')
    file.write('echo "Copying from ${PBS_O_WORKDIR}/ to ${TMP}/"\n')
    file.write('/usr/bin/rsync -vax "${PBS_O_WORKDIR}/" ${TMP}/\n')
    file.write('\n')
    file.write('cd ${TMP}\n')
    return

def ReturnTemp(file):
    file.write('# job done, copy everything back\n')
    file.write('echo "Copying from ${TMP}/ to ${PBS_O_WORKDIR}/"\n')
    file.write('/usr/bin/rsync -vax ${TMP}/ "${PBS_O_WORKDIR}/"\n')
    file.write('\n')
    file.write('# delete my temporary files\n')
    file.write('[ $? -eq 0 ] && /bin/rm -rf ${TMP}\n')



def WriteBatchFile(MPB,Direc,cpu,mem,Solver,Coh,SubRoutine,RunTemp):
    enter = lambda a: [file.write('\n') for i in range(a)]
    Name = '{}-{}'.format(MPB,Direc)
    with open(MPB+'-'+Direc+"\Sub{}.txt".format(Direc), "w") as file:
        file.write('# Job for Torque PBS 4.2.10\n')
        file.write('#\n')
        file.write('# PBS parameters (see: man qsub)\n')
        file.write('# -----------------------------\n')
        file.write('#PBS -j oe \n')
        if cpu==20 or mem==None: file.write('#PBS -l nodes=1:ppn={}\n'.format(cpu))
        else:       file.write('#PBS -l nodes=1:ppn={},mem={}g\n'.format(cpu,mem))    
        file.write('#PBS -M l.j.kootte@tudelft.nl\n')
        file.write('#PBS -m abe\n')
        file.write('#PBS -N {}\n'.format(Name))
        file.write('#PBS -o ${PBS_JOBNAME}.LOG \n')
        file.write('#PBS -q asm\n')
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
        if SubRoutine and Coh: WriteJob += ' user=/home/ljkootte/Cohesive_UMAT_Fatigue.v25.for'
        file.write('python "/home/ljkootte/SimpleCopy.py" -- ${PBS_JOBNAME} ${TMP} ${PBS_O_WORKDIR}& \n')
        file.write(WriteJob+'\n')
        file.write('wait\n')
        if RunTemp: ReturnTemp(file)
        file.write('cd ${PBS_O_WORKDIR}\n')
        file.write('abaqus cae noGUI="/home/ljkootte/CreateDisplay.py" -- ${PBS_O_WORKDIR}\n')
        if not Coh: file.write('abaqus cae noGUI="/home/ljkootte/CreateOutFieldsSK.py" -- ${PBS_O_WORKDIR}\n')
        elif Coh: file.write('abaqus cae noGUI="/home/ljkootte/CreateOutFieldsSDEG.py" -- ${PBS_O_WORKDIR}\n')
        file.write('python "/home/ljkootte/PlotFemExp/CombinedPlot.py" -- ${PBS_O_WORKDIR}\n')
        file.write('exit 0\n')
        
    return
        
        

