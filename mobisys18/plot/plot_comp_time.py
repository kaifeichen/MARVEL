import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def readTime(filename):
    times = []
    values = []
    with open(filename) as f:
        for l in f:
            val = l.split()[-1]
            if "=" in val:
                val = float(val.strip("="))/1000000
            else:
                val = float(val.strip("ms"))
            values.append(val)
    return values

def plot_cdf(data, fmt, label, linewidth):
    counts, bin_edges = np.histogram(data, bins="auto", density=True)
    ecdf = np.cumsum(counts)
    ecdf = ecdf/ecdf.max()
    plt.plot(bin_edges[1:], ecdf, fmt, label=label, linewidth=linewidth)

path = sys.argv[1]
rot_data = readTime(os.path.join(path, "imuGameVectorProcessTime"))
acc_data = readTime(os.path.join(path, "imuLinearProcessTime"))
of_data = readTime(os.path.join(path, "opticalFlowTime"))

print "rotation:", np.mean(rot_data), np.std(rot_data)
print "acceleration:", np.mean(acc_data), np.std(acc_data)
print "optical flow:", np.mean(of_data), np.std(of_data)

fig = plt.figure(figsize=(12, 5))
plot_cdf(rot_data, 'r--', "Rotation Integration", linewidth=2)
plot_cdf(acc_data, 'g-.', "Acceleration Integration", linewidth=2)
plot_cdf(of_data, 'b:', "Optical Flow", linewidth=2)
plt.legend(loc="lower center")
plt.xscale("log")
plt.xlabel("Computation Time (ms)", fontsize=22)
plt.ylabel("CDF", fontsize=22)
plt.grid()
plt.savefig("comp_time.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
