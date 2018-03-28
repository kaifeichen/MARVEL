import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def getLatency(fileName):
    f = open(fileName)
    data = []
    while True:
        line = f.readline()
        if len(line) > 3:
            data.append(float(line)/10**6)
        else:
            break
    return data

def plot_cdf(data, fmt, label):
    counts, bin_edges = np.histogram(data, bins="auto", density=True)
    ecdf = np.cumsum(counts)
    ecdf = ecdf/ecdf.max()
    plt.plot(bin_edges[1:], ecdf, fmt, label=label)

path = sys.argv[1]
local_imu = getLatency(os.path.join(path, "local_imu.txt"))
cloud_wifi = getLatency(os.path.join(path, "cloud_wifi.txt"))
cloud_celluar = getLatency(os.path.join(path, "cloud_celluar.txt"))

fig = plt.figure(figsize=(12, 5))
plt.plot(local_imu)
#plot_cdf(local_imu, 'r--', "Local IMU")
#plot_cdf(cloud_wifi, 'g-.', "Image Localization over WiFi")
#plot_cdf(cloud_celluar, 'g-.', "Image Localization over Celluar")
plt.legend()#loc="lower right")
plt.xlabel("Latency from Sensor Capture to Getting Localization Result (ms)", fontsize=22)
plt.ylabel("CDF", fontsize=22)
plt.grid()
plt.savefig("e2e_latency.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
