import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def readPower(filename):
    times = []
    values = []
    with open(filename) as f:
        lines = f.readlines()
        names = lines[3].split(",")
        idx = names.index('"Battery Power* [uW]"')
        for i in range(5, len(lines)):
            time = lines[i].split(",")[idx - 1]
            val = lines[i].split(",")[idx]
            if len(time) == 0 or len(val) == 0:
                break
            else:
                time = int(time)
                val = float(val)/1000000
            times.append(time)
            values.append(val)
    return times, values

def plot_cdf(data, fmt, label, linewidth):
    counts, bin_edges = np.histogram(data, bins="auto", density=True)
    ecdf = np.cumsum(counts)
    ecdf = ecdf/ecdf.max()
    plt.plot(bin_edges[1:], ecdf, fmt, label=label, linewidth=linewidth)

path = sys.argv[1]
prev_times, prev_data = readPower(os.path.join(path, "onlyPreview.csv"))
imu_times, imu_data = readPower(os.path.join(path, "onlyPreviewAndIMU.csv"))
of_times, of_data = readPower(os.path.join(path, "onlyPreviewAndOF_YUV.csv"))
offload_times, offload_data = readPower(os.path.join(path, "onlyPreviewAndOffloading.csv"))
local_times, local_data = readPower(os.path.join(path, "rtabmap.csv"))

print "prev:", np.mean(prev_data), np.std(prev_data)
print "imu:", np.mean(imu_data), np.std(imu_data)
print "of:", np.mean(of_data), np.std(of_data)
print "offload:", np.mean(offload_data), np.std(offload_data)
print "local:", np.mean(local_data), np.std(local_data)

fig = plt.figure(figsize=(12, 5))
plot_cdf(prev_data, 'k-', "Preview", linewidth=2)
plot_cdf(imu_data, 'g-.', "Preview + IMU", linewidth=2)
plot_cdf(of_data, 'b:', "Preview + Optical Flow", linewidth=2)
plot_cdf(offload_data, 'r--', "Preview + Offloading", linewidth=2)
plt.legend(loc="lower right")
plt.xlabel("Power Usage (Watt)", fontsize=22)
plt.ylabel("CDF", fontsize=22)
plt.grid()
plt.savefig("power.pdf", bbox_inches='tight')
plt.tight_layout()
#plt.show()
