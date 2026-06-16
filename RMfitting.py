#!/usr/bin/env python3

import os
import numpy as np
from pathlib import Path

import sys
import subprocess
#testing
#template = 'GUPPI_0737-3039A_57957_51399.project_id.x.shifted.scaled'
template = sys.argv[1]

with open('rmfitdata.txt', 'w') as file:
    pass
subprocess.run(
    f'rmfit -t {template} > rmfitdata.txt 2>&1',
    shell=True)

with open('rmfitdata.txt', 'r') as file:
    strls = file.read().split()
    RM = strls[-3]
    Chisq = float(strls[22])
    print(Chisq)
    print(RM)
  #Only accepts Chi square in this range
if 0.01 < Chisq and Chisq < 10:
    subprocess.run(
        f'pam -R {RM} -e rm_scrunch {template}',
        shell=True)
    print("process successful")
subprocess.run(
    f'rm rmfitdata.txt',
    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
