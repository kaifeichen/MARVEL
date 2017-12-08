from label_video import *
import matplotlib.pyplot as plt
import numpy as snp
import sys

video_file = sys.argv[1]
file_hash = hashlib.md5(open(video_file, 'rb').read()).hexdigest()
truth_locs = np.array(read_data("." + file_hash + ".truth_locs"))
labels = read_data("." + file_hash + ".labels")

datas = []
for i in range(7):
    datas.append([])

for a, b in zip(truth_locs, labels):
    if any(x < 0 for x in a[0]) or b == None:
        for i in range(7):
            datas[i].append(np.nan)
    else:
        for i in range(7):
            if(len(b)==7):
                datas[i].append(np.linalg.norm(a[0] - np.array(b[i])))

fig = plt.figure(figsize=(12, 5))
#for i in range(7):
#    plt.plot(datas[i], label=str(i))

plt.boxplot(datas)
#plt.boxplot(datas, whis = 'range')
plt.xlabel("Number of Images Offloaded", fontsize=22)
plt.ylabel("Error (pixel)", fontsize=22)
plt.grid()
plt.legend()
plt.savefig("cali.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
