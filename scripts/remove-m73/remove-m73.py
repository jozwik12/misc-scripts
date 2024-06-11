#!/usr/bin/python
import sys
import re
import os

sourceFile = sys.argv[1]
print(sys.argv[1])

# Read the ENTIRE g-code file into memory
with open(sourceFile, "r+") as f:
    lines = f.readlines()
    for line in lines:
      stringMatch = re.search(r'^M73', line)
      # print(line.startswith("M73"))
      # print(stringMatch)
      if not line.startswith("M73"):
          # Write original line if it does not start with 'M73'
          f.write(line)
f.close()