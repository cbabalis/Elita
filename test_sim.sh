#!/bin/bash
#PBS -q tuc

export PYTHONPATH=/storage/tuclocal/babalis/libs/lib/python/
python2.7 /storage/tuclocal/babalis/source/trunk/simulation/environment.py 100 2 1 0.2 '/storage/tuclocal/babalis/dataset/wc_day44'
