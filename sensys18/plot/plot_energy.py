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

path_w_p = sys.argv[-1]


idle_w_p = []
offof_w_p = []
still_w_p = []
rotate_w_p = []
translate_w_p = []
for filename in os.listdir(path_w_p):
    print filename
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

data_w_p = [idle_w_p, offof_w_p, still_w_p, rotate_w_p, translate_w_p]

fig, ax = plt.subplots(figsize=(8, 4))
ind = np.arange(5)
width = 0.5
labels = ('Idle', 'Baseline', 'MARVEL:\nStatic', 'MARVEL:\nRotation', 'MARVEL:\nTranslation')

rects_w_p = ax.bar(ind, data_w_p, width, alpha=0.5)#, label='w/ cam feed')

ax.set_ylabel("Average Power (Watt)", fontsize=22)
ax.set_xticks(ind+width/2)
ax.set_xticklabels(labels, rotation=0, fontsize=18) #, rotation=45)
ax.tick_params(axis='y', labelsize = 18)
ax.grid(axis='y')
ax.set_xlim(xmin=-0.3, xmax=max(ind)+width+0.3)
#ax.set_ylim(ymax=3.1)

#ax.legend(loc="upper left")

autolabel(rects_w_p, ax, "center")

plt.tight_layout()

plt.show()

