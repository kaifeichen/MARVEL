from label_video import *
import matplotlib.pyplot as plt
import numpy as snp
import sys

video_files = sys.argv[1:6]
errors = []
for video_file in video_files:
    file_hash = hashlib.md5(open(video_file, 'rb').read()).hexdigest()
    truth_locs = np.array(read_data("." + file_hash + ".truth_locs"))
    labels = read_data("." + file_hash + ".labels")

    data = []
    for a, b in zip(truth_locs, labels):
        if any(x < 0 for x in a[0]) or b is None:
            pass
        else:
            data.append(np.linalg.norm(a[0] - np.array(b[1])))

    errors.append(data)

print len(errors)

fig = plt.figure(figsize=(6, 5))
plt.tick_params(axis='both', which='major', labelsize=20)
ax = fig.add_subplot(111)
plt.boxplot(errors)

#x = np.arange(0.5, 5.5)
#plt.bar(x, [np.mean(data) for data in errors], align='center', alpha=0.5)
#plt.xticks(x,('25','50', '75', '100', '200'))

ax.set_xticklabels(('25','50', '75', '100', '200'))
plt.xlabel(r"$\phi$ Vaule (pixel)", fontsize=22)
plt.ylabel("Error (pixel)", fontsize=22)
plt.grid()
plt.savefig("eval_phi_err.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
