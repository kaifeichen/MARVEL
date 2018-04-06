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


def autolabel(rects, ax, xpos='center'):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    xpos = xpos.lower()  # normalize the case of the parameter
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

    for rect in rects:
        height = round(rect.get_height(), 2)
        ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                '{}'.format(height), ha=ha[xpos], va='bottom', fontsize=20)


low = 30
# = 750

path_wo_p = sys.argv[-2]
path_w_p = sys.argv[-1]

_, idle_wo_p = readPower(os.path.join(path_wo_p, "doNothing30.csv"))
_, offof_wo_p = readPower(os.path.join(path_wo_p, "offof31.csv"))
_, still_wo_p = readPower(os.path.join(path_wo_p, "still30.csv"))
_, rotate_wo_p = readPower(os.path.join(path_wo_p, "rotate30.csv"))
_, translate_wo_p = readPower(os.path.join(path_wo_p, "translate30.csv"))


idle_wo_p = np.mean(idle_wo_p[low:])
offof_wo_p = np.mean(offof_wo_p[low:])
still_wo_p = np.mean(still_wo_p[low:])
rotate_wo_p = np.mean(rotate_wo_p[low:])
translate_wo_p = np.mean(translate_wo_p[low:])

idle_w_p = []
offof_w_p = []
still_w_p = []
rotate_w_p = []
translate_w_p = []
for filename in os.listdir(path_w_p):
    if filename.endswith(".csv"):
        _, power = readPower(os.path.join(path_w_p, filename))
        mean_power = np.mean(power[low:])
        if 'Idle' in filename:
            idle_w_p.append(mean_power)
        elif 'Offloading' in filename:
            offof_w_p.append(mean_power)
        elif 'Static' in filename:
            still_w_p.append(mean_power)
        elif 'Rotating' in filename:
            rotate_w_p.append(mean_power)
        elif 'Translating' in filename:
            translate_w_p.append(mean_power)
idle_w_p = np.mean(idle_w_p)
offof_w_p = np.mean(offof_w_p)
still_w_p = np.mean(still_w_p)
rotate_w_p = np.mean(rotate_w_p)
translate_w_p = np.mean(translate_w_p)

#print "nothing:", np.mean(idle_wo_p), np.std(idle_wo_p)
#print "offloading:", np.mean(offof_wo_p), np.std(offof_wo_p)
#print "still:", np.mean(still_wo_p), np.std(still_wo_p)
#print "rotate:", np.mean(rotate_wo_p), np.std(rotate_wo_p)
#print "translate:", np.mean(translate_wo_p), np.std(translate_wo_p)

data_wo_p = [idle_wo_p, offof_wo_p, still_wo_p, rotate_wo_p, translate_wo_p]
data_w_p = [idle_w_p, offof_w_p, still_w_p, rotate_w_p, translate_w_p]

fig, ax = plt.subplots(figsize=(12, 5))
ind = np.arange(5)
width = 0.35
labels = ('Idle', 'Baseline', 'MARVEL:\nStatic', 'MARVEL:\nRotation', 'MARVEL:\nTranslation')

rects_wo_p = ax.bar(ind-width/2, data_wo_p, width, color='r', alpha=0.5, label='w/o cam feed')
rects_w_p = ax.bar(ind+width/2, data_w_p, width, color='y', alpha=0.5, label='w/ cam feed')

ax.set_ylabel("Average Power (Watt)", fontsize=22)
ax.set_xticks(ind+width/2)
ax.set_xticklabels(labels, rotation=0, fontsize=18) #, rotation=45)
ax.tick_params(axis='y', labelsize = 18)
ax.grid(axis='y')
ax.set_xlim(xmin=-0.5)
ax.set_ylim(ymax=2.6)

ax.legend(loc="upper left")

autolabel(rects_wo_p, ax, "center")
autolabel(rects_w_p, ax, "center")

plt.tight_layout()

plt.show()

