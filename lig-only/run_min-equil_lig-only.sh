#!/bin/bash
gmx grompp -f 04_minimize.mdp -c 03_solv-ion.gro -p topol.top -o 04_minimization.tpr -maxwarn 4
gmx mdrun -v -nt 8 -deffnm 04_minimization

gmx grompp -f L05_nvt_equil.mdp -c 04_minimization.gro -r 04_minimization.gro -p topol.top \
-n index.ndx -o 05_nvt_equil.tpr
gmx mdrun -v -nt 8 -deffnm 05_nvt_equil

gmx grompp -f L06_npt_equil.mdp -c 05_nvt_equil.gro -t 05_nvt_equil.cpt -r 05_nvt_equil.gro  \
-p topol.top -n index.ndx -o 06_npt_equil.tpr
gmx mdrun -v -nt 8 -deffnm 06_npt_equil

gmx grompp -f L07_md_run.mdp -c 06_npt_equil.gro -t 06_npt_equil.cpt -p topol.top -n \
index.ndx -o 07_md_run.tpr

