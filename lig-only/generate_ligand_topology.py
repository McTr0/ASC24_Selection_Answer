#!/bin/env python

from sys import argv
import shutil
import os

ligand_basename = argv[1]
ligand_dir = ligand_basename+'.acpype'
#get the necessary ligand_files
curr_dir = os.getcwd()
for file_name in [ligand_basename+'_GMX.gro', ligand_basename+'_GMX.itp', 'posre_'+ligand_basename+'.itp']:
    shutil.copy(ligand_dir+'/'+file_name, curr_dir+'/'+file_name)

posre_file = curr_dir+'/posre_'+ligand_basename+'.itp'
ligand_file = curr_dir+'/'+ligand_basename+'_GMX.gro'
itp_file = curr_dir+'/'+ligand_basename+'_GMX.itp'
topology_file = curr_dir+'/topol.top'

# rewrite topol.top to make it a "real" topol.top

with open(itp_file, 'r') as in_file:
    topology_lines = in_file.readlines()
    topology_lines[0] = '#include "amber99sb.ff/forcefield.itp"\n'
    topology_lines.append('; Ligand position restraints\n')
    topology_lines.append('#ifdef POSRES\n')
    topology_lines.append('#include "posre_'+ligand_basename+'.itp"\n')
    topology_lines.append('#endif\n')
    topology_lines.append('\n')
    topology_lines.append('; Include water topology\n')
    topology_lines.append('#include "amber99sb.ff/tip3p.itp"\n')
    topology_lines.append('\n')
    topology_lines.append('#ifdef POSRES_WATER\n')
    topology_lines.append('; Position restraint for each water oxygen\n')
    topology_lines.append('[ position_restraints ]\n')
    topology_lines.append(';  i funct       fcx        fcy        fcz\n')
    topology_lines.append('   1    1       1000       1000       1000\n')
    topology_lines.append('#endif\n')
    topology_lines.append('\n')
    topology_lines.append('; Include topology for ions\n')
    topology_lines.append('#include "amber99sb.ff/ions.itp"\n')
    topology_lines.append('\n')
    topology_lines.append('[ system ]\n')
    topology_lines.append('; Name\n')
    topology_lines.append('Ligand in water\n')
    topology_lines.append('\n')
    topology_lines.append('[ molecules ]\n')
    topology_lines.append('; Compound        #mols\n')
    topology_lines.append(ligand_basename+'              1\n')
    with open('topol.top', 'w') as tmp_file:
        for line in topology_lines:
            tmp_file.write(line)
