from label_video import *
import matplotlib.pyplot as plt
import numpy as snp
import sys


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


pickle_r1_b_1 = sys.argv[1]
pickle_r1_b_2 = sys.argv[2]
loc_r1_b_1 = np.array(read_data(pickle_r1_b_1))
loc_r1_b_2 = np.array(read_data(pickle_r1_b_2))


errors_r1_b = []
for a, b in zip(loc_r1_b_1, loc_r1_b_2):
    if a is None or b is None or any(x < 0 for x in a[0]) or any(x < 0 for x in b[0]):
        continue
    else:
        errors_r1_b.append(np.linalg.norm(np.array(a[0]) - np.array(b[0])))

b1 = np.mean(errors_r1_b)
m1 = 0
b2 = 0
m2 = 0
b3 = 0
m3 = 0

b = [b1, b2, b3]
m = [m1, m2, m3]

fig, ax = plt.subplots(figsize=(8, 4))
ind = np.arange(3)
width = 0.35
labels = ('Room 1', 'Room 2', 'Room 3')

rects_b = ax.bar(ind-width/2, b, width, color='r', alpha=0.5, label='Baseline')
rects_m = ax.bar(ind+width/2, m, width, color='y', alpha=0.5, label='MARVEL')

ax.set_ylabel("Average Error (Pixel)", fontsize=24)
ax.set_xticks(ind+width/2)
ax.set_xticklabels(labels, rotation=0, fontsize=14) #, rotation=45)
ax.tick_params(axis='y', labelsize = 24)
ax.grid(axis='y')
ax.set_xlim(xmin=-0.5)
ax.set_ylim(ymax=80)

ax.legend(loc="upper left")

autolabel(rects_b, ax, "center")
autolabel(rects_m, ax, "center")

plt.tight_layout()

plt.show()
