from label_video import *
import matplotlib.pyplot as plt
import numpy as snp
import sys

filename = sys.argv[1]

with open(filename) as f:
    lines = f.readlines()
features = tuple(int(l.strip()) for l in lines[::3])
edges = tuple(int(float(l.strip())) for l in lines[1::3])
assert len(features) == len(edges)

fig = plt.figure(figsize=(12, 5))
plt.scatter(features, [e/1000 for e in edges], alpha=0.5)
plt.xlabel("Number of Features", fontsize=22)
plt.ylabel("Sum of Edge Pixel Values (K)", fontsize=22)
plt.grid()
plt.xlim(xmin=0)
plt.ylim(ymin=0)
plt.tick_params(axis='both', which='major', labelsize=20)
plt.savefig("edge_feature.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
