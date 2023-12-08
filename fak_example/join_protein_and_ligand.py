#!/bin/env python

from sys import argv
import subprocess
import shutil
import os
#from acpype import acs_api

gmx_exec = 'gmx'
acpype_exec = '/N/slate/mrobo/mambaforge_br200/envs/acpype/bin/acpype'
gmx_file_dir= '/N/project/TREAT-AD/mrobo//5/mmpbsa/gmx_files/many_frames'
#gmx_file_dir = '/N/project/R-M-01/1/pak1_4zjj/mmgbsa/workflow/gmx_files/'
ions_mdp = gmx_file_dir + '/add_ions.mdp'
minimize_mdp = gmx_file_dir + '/minimize.mdp'

input_ligand_basename = argv[1]
protein_file = argv[2]
topology_file = argv[3]

curr_dir = os.getcwd()
complex_file = curr_dir+'/complex.gro'


print('CREATING complex.gro')
# make complex file and rewrite it to add the ligand
with open(complex_file, 'w') as gromacs_file:
    for f in [protein_file, input_ligand_basename+'.acpype/'+input_ligand_basename+'_GMX.gro']:
        with open(f) as f_input:
            shutil.copyfileobj(f_input, gromacs_file)

with open(complex_file, 'r') as gromacs_file:
    gromacs_lines = gromacs_file.readlines()
    num_protein_lines = int(gromacs_lines[1])
    num_ligand_lines = int(gromacs_lines[num_protein_lines + 4])
    gromacs_lines[1] = str(num_protein_lines + num_ligand_lines) + '\n'
    
    del gromacs_lines[num_protein_lines + 3 : num_protein_lines + 5]
    del gromacs_lines[-1]
    gromacs_lines.append(gromacs_lines.pop(num_protein_lines + 2))

    with open('tmp.gro', 'w') as tmp_file:
        for line in gromacs_lines:
            tmp_file.write(line)

os.rename('tmp.gro', complex_file)

print('MODIFYING topol.top')
# rewrite topol.top to include the ligand
include_line = '#include "'+input_ligand_basename+'.acpype/'+input_ligand_basename+'_GMX.itp"\n'
molecule_line = input_ligand_basename+'              1\n'
posres_joined_lines = '; Ligand position restraints\n#ifdef POSRES\n#include "'+input_ligand_basename+'.acpype/posre_'+input_ligand_basename+'.itp"\n#endif\n'


with open(topology_file, 'r') as top_file:
    topology_lines = top_file.readlines()
    include_insert = None
    posres_insert = None
    for i, line in enumerate(topology_lines):
        if '#include "amber99sb.ff/forcefield.itp"' in line:
            include_insert = i + 1
        if '; Include Position restraint file' in line:
            posres_insert = i + 4
    topology_lines.insert(include_insert, include_line)
    topology_lines.insert(posres_insert, posres_joined_lines)
    topology_lines.append(molecule_line)

    with open('tmp.top', 'w') as tmp_file:
        for line in topology_lines:
            tmp_file.write(line)

os.rename(topology_file, 'bak_'+topology_file)
os.rename('tmp.top', topology_file)

"""

# use gromacs to solvate and add ions
#subprocess.run([gmx_exec, 'editconf', '-f', complex_file, '-o', '01_boxgen.gro', '-bt', 'dodecahedron', '-d', '1.0'])
subprocess.run([gmx_exec, 'editconf', '-f', complex_file, '-o', '01_boxgen.gro', '-bt', 'triclinic', '-d', '1.0'])
subprocess.run([gmx_exec, 'solvate', '-cp', '01_boxgen.gro', '-cs', 'spc216.gro', '-p', topology_file, '-o', '02_solvated.gro'])
subprocess.run([gmx_exec, 'grompp', '-f', ions_mdp, '-c', '02_solvated.gro', '-p', topology_file, '-o', '03_ions.tpr'])

#there are cleaner ways to have python interact with an interactive script, but that requires thought
# see https://stackoverflow.com/questions/19880190/interactive-input-output-using-python
# and https://eli.thegreenplace.net/2017/interacting-with-a-long-running-child-process-in-python/
with open('ion_choice.txt', 'w') as choice_file:
    choice_file.write('SOL\n')
os.system(' '.join([gmx_exec, 'genion', '-s', '03_ions.tpr', '-o', '03_solv-ion.gro', '-p', topology_file, '-pname', 'NA', '-nname', 'CL', '-neutral', '-conc', '0.10', '<', 'ion_choice.txt']))

# make index file. ASSUMES THE ONLY 'OTHER' IS THE LIGAND
# had to use OTHER because there are multiple MOL options (why does gromacs insist on interaction?)
with open('index_choice.txt', 'w') as choice_file:
    choice_file.write('"Protein" | "Other"\n')
    choice_file.write('q\n')
os.system(' '.join([gmx_exec, 'make_ndx', '-f', '03_solv-ion.gro', '-o', 'index.ndx', '<', 'index_choice.txt']))
"""
