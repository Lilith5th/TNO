#!/usr/local/lib/python3.7
from subprocess import Popen
import sys

#filename = sys.argv[1]
while True:
    print("\nStarting " )
    p = Popen("python3.7 KNX_ClientMDPC.py"  , shell=True)
    p.wait()
