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
print(labels)
for a, b in zip(truth_locs, labels):
    if any(x < 0 for x in a[0]) or b == None:
        pass
    else:
        for i in range(7):
            if(len(b)==7):
                datas[i].append(np.linalg.norm(a[0] - np.array(b[i])))

fig = plt.figure(figsize=(6, 5))
#for i in range(7):
#    plt.plot(datas[i], label=str(i))

plt.boxplot(datas)
print(12345)
print(len(datas[0]))
print(len(datas[2]))
print(len(datas[3]))
print(len(datas[4]))
print(len(datas[5]))
print(len(datas[6]))
#plt.boxplot(datas, whis = 'range')
plt.tick_params(axis='both', which='major', labelsize=20)
plt.xlabel("Number of Images Offloaded", fontsize=22)
plt.ylabel("Error (pixel)", fontsize=22)
plt.grid()
plt.legend(loc="upper right", fontsize=14)
plt.savefig("cali.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
