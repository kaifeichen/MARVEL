import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def getLatencyList(fileName):
    myFile = open(fileName)
    latencyDatas = []
    while(True):
        line = myFile.readline()
        if(len(line)>3):
            latencyDatas.append(float(line.split()[-1]))
        else:
            break
    return latencyDatas

def plot_cdf(data, fmt, label):
    counts, bin_edges = np.histogram(data, bins="auto", density=True)
    ecdf = np.cumsum(counts)
    ecdf = ecdf/ecdf.max()
    plt.plot(bin_edges[1:], ecdf, fmt, label=label)

path = sys.argv[1]
gyro = getLatencyList(os.path.join(path, "gyroDelay.txt"))[-1000:]
mag = getLatencyList(os.path.join(path, "magDelay.txt"))[-1000:]
acc = getLatencyList(os.path.join(path, "accDelay.txt"))[-1000:]
img = getLatencyList(os.path.join(path, "imageLantency.txt"))[-1000:]

print "gyro:"
print "mean: ", np.mean(gyro)
print "std: ", np.std(gyro)
print "median: ", np.percentile(gyro, 50)
print "99th: ", np.percentile(gyro, 99)

print "mag:"
print "mean: ", np.mean(mag)
print "std: ", np.std(mag)
print "median: ", np.percentile(mag, 50)
print "99th: ", np.percentile(mag, 99)

print "acc:"
print "mean: ", np.mean(acc)
print "std: ", np.std(acc)
print "median: ", np.percentile(acc, 50)
print "99th: ", np.percentile(acc, 99)

print "img:"
print "mean: ", np.mean(img)
print "std: ", np.std(img)
print "median: ", np.percentile(img, 50)
print "99th: ", np.percentile(img, 99)

fig = plt.figure(figsize=(12, 5))
plot_cdf(gyro, 'r--', "Gyroscope")
plot_cdf(mag, 'g-.', "Magnetometer")
plot_cdf(acc, 'b:', "Accelerometer")
plot_cdf(img, 'k-', "Image")
plt.legend(loc="lower right")
plt.xlabel("Latency from Caputre to Appearance in Application (ms)", fontsize=22)
plt.ylabel("CDF", fontsize=22)
plt.grid()
plt.savefig("sensor_latency.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
