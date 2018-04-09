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

pickle_r1_m_1 = sys.argv[3]
pickle_r1_m_2 = sys.argv[4]
loc_r1_m_1 = np.array(read_data(pickle_r1_m_1))
loc_r1_m_2 = np.array(read_data(pickle_r1_m_2))

errors_r1_b = []
for a, b in zip(loc_r1_b_1, loc_r1_b_2):
    if a is None or b is None or any(x < 0 for x in a[0]) or any(x < 0 for x in b[0]):
        continue
    else:
        errors_r1_b.append(np.linalg.norm(np.array(a[0]) - np.array(b[0])))

errors_r1_m = []
for a, b in zip(loc_r1_m_1, loc_r1_m_2):
    if a is None or b is None or any(x < 0 for x in a[0]) or any(x < 0 for x in b[0]):
        continue
    else:
        errors_r1_m.append(np.linalg.norm(np.array(a[0]) - np.array(b[0])))

pickle_r2_b_1 = sys.argv[5]
pickle_r2_b_2 = sys.argv[6]
loc_r2_b_1 = np.array(read_data(pickle_r2_b_1))
loc_r2_b_2 = np.array(read_data(pickle_r2_b_2))

pickle_r2_m_1 = sys.argv[7]
pickle_r2_m_2 = sys.argv[8]
loc_r2_m_1 = np.array(read_data(pickle_r2_m_1))
loc_r2_m_2 = np.array(read_data(pickle_r2_m_2))

errors_r2_b = []
for a, b in zip(loc_r2_b_1, loc_r2_b_2):
    if a is None or b is None or any(x < 0 for x in a[0]) or any(x < 0 for x in b[0]):
        continue
    else:
        errors_r2_b.append(np.linalg.norm(np.array(a[0]) - np.array(b[0])))

errors_r2_m = []
for a, b in zip(loc_r2_m_1, loc_r2_m_2):
    if a is None or b is None or any(x < 0 for x in a[0]) or any(x < 0 for x in b[0]):
        continue
    else:
        errors_r2_m.append(np.linalg.norm(np.array(a[0]) - np.array(b[0])))



errors_r3_b = [1]
errors_r3_m = [1]

b = [np.mean(errors_r1_b), np.mean(errors_r2_b)] #, np.mean(errors_r3_b)]
m = [np.mean(errors_r1_m), np.mean(errors_r2_m)] #, np.mean(errors_r3_m)]
b_std = [np.std(errors_r1_b), np.std(errors_r2_b)] #, np.std(errors_r3_b)]
m_std = [np.std(errors_r1_m), np.std(errors_r2_m)] #, np.std(errors_r3_m)]

print b, m
print b_std, m_std

fig, ax = plt.subplots(figsize=(8, 4))
ind = np.arange(2)
width = 0.35
labels = ('Room 1', 'Room 2', 'Room 3')

error_config = {'ecolor': '0.3'}

rects_b = ax.bar(ind-width/2, b, width, yerr=b_std, color='w', alpha=0.5, error_kw=error_config, label='Baseline')
rects_m = ax.bar(ind+width/2, m, width, yerr=m_std, color='g', alpha=0.5, error_kw=error_config,label='MARVEL')

ax.set_ylabel("Average Error (Pixel)", fontsize=24)
ax.set_xticks(ind+width/2)
ax.set_xticklabels(labels, rotation=0, fontsize=24) #, rotation=45)
ax.tick_params(axis='y', labelsize = 24)
ax.grid(axis='y')
ax.set_xlim(xmin=-0.5, xmax=2)
ax.set_ylim(ymax=120)

ax.legend(loc="upper left", fontsize=24)

autolabel(rects_b, ax, "left")
autolabel(rects_m, ax, "right")

plt.tight_layout()

plt.show()
