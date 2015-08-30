#!/bin/sh
#PBS -q tuc
#PBS -l nodes=6:ppn=2

for rate in 0.1
do
    for node in 2 5
    do
        pbsdsh python2.7 simulation/environment.py 100000 $node_num 1 $rate '/storage/tuclocal/babalis/dataset/wc_day44'
    done
done


