import os
import sys
import numpy as np

path = sys.argv[-1]

for file in os.listdir(path):
    file_name = os.path.join(path, file)
    if os.path.isfile(file_name):
        with open(file_name) as f:
            mean_val = np.mean([float(l) for l in f.readlines()])
            print file_name, mean_val
