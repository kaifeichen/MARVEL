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


def avg(data):
    return sum(data)/len(data)
still_times, still_data = readPower( "still30.csv")
offof_times, offof_data = readPower("offof31.csv")
rotate_times, rotate_data = readPower("rotate30.csv")
translate_times, translate_data = readPower("translate30.csv")
nothing_times, nothing_data = readPower("doNothing30.csv")
#local_times, local_data = readPower(os.path.join(path, "rtabmap.csv"))
low = 30
high = 750

still_data = still_data[low:high]
offof_data = offof_data[low:high]
rotate_data = rotate_data[low:high]
translate_data = translate_data[low:high]
nothing_data = nothing_data[low:high]
print "still:", np.mean(still_data), np.std(still_data)
print "offloading:", np.mean(offof_data), np.std(offof_data)
print "rotate:", np.mean(rotate_data), np.std(rotate_data)
print "translate:", np.mean(translate_data), np.std(translate_data)
print "nothing:", np.mean(nothing_data), np.std(nothing_data)

'''
plt.plot(still_data, 'k-', label = "still11.csv", linewidth=2)
plt.plot(offof_data, 'g-', label = "offload11.csv", linewidth=2)
plt.plot(rotate_data, 'b:', label = "rotate12.csv", linewidth=2)
plt.plot(translate_data, 'r-', label = "rotate12.csv", linewidth=2)
#plot_cdf(prev_data, 'k-', "Still", linewidth=2)
#plot_cdf(imu_data, 'g-.', "pureRotate", linewidth=2)
#plot_cdf(of_data, 'b:', "Translation", linewidth=2)
#plot_cdf(offload_data, 'r--', "Preview + Offloading", linewidth=2)
#plot_cdf(local_data, 'y-', "RTABMap", linewidth=2)
'''

fig = plt.figure(figsize=(12, 5))
#fig, ax = plt.subplots()
x = np.arange(0.5,5.5)
avgError = [avg(nothing_data), avg(still_data), avg(rotate_data), avg(translate_data), avg(offof_data)]
plt.bar(x, avgError, align='center', alpha=0.5)
plt.xticks(x, ('Idle', 'Static', 'Rotation', 'Translation', 'Continuous'))#, fontsize=18)

plt.legend(loc="upper left")
plt.ylabel("Average Power Usage (Watt)", fontsize=22)
plt.grid()
plt.tick_params(axis='both', which='major', labelsize=20)
plt.savefig("eval_power.pdf", bbox_inches='tight')
plt.tight_layout()
#plt.show()

