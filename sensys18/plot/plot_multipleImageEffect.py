from label_video import *
import matplotlib.pyplot as plt
import numpy as np
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
        height = int(rect.get_height())
        ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                '{}'.format(height), ha=ha[xpos], va='bottom', fontsize=20)

video_file = sys.argv[1]
file_hash = hashlib.md5(open(video_file, 'rb').read()).hexdigest()
truth_locs = np.array(read_data("." + file_hash + ".truth_locs"))
labels = read_data("." + file_hash + ".labels")

datas = []
for i in range(7):
    datas.append([])
print(labels)
for a, b in zip(truth_locs, labels):
    if any(x < 0 for x in a[0]) or b == None:
        pass
    else:
        for i in range(7):
            if(len(b)==7):
                datas[i].append(np.linalg.norm(a[0] - np.array(b[i])))

fig = plt.figure(figsize=(8, 4))
#for i in range(7):
#    plt.plot(datas[i], label=str(i))

x= np.arange(0.5,7.5)
rects = plt.gca().bar(x,[np.mean(data) for data in datas], align='center', alpha=0.5)
plt.xticks(x,('1','2', '3', '4', '5', '6', '7'))
print(12345)
print(len(datas[0]))
print(len(datas[2]))
print(len(datas[3]))
print(len(datas[4]))
print(len(datas[5]))
print(len(datas[6]))
#plt.boxplot(datas, whis = 'range')
plt.tick_params(axis='both', which='major', labelsize=24)
plt.xlabel("Number of Images Offloaded", fontsize=24)
plt.ylabel("Average Error (pixel)", fontsize=24)
plt.grid(axis='y')
plt.ylim(ymax=60)
autolabel(rects, plt.gca(), "center")
plt.legend(loc="upper right", fontsize=14)
plt.savefig("mul_img_err.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
