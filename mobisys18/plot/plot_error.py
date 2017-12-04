from label_video import *
import matplotlib.pyplot as plt
import numpy as snp
import sys

video_file = sys.argv[1]
file_hash = hashlib.md5(open(video_file, 'rb').read()).hexdigest()
truth_locs = np.array(read_data("." + file_hash + ".truth_locs"))
label_locs = np.array(read_data("." + file_hash + ".label_locs"))

data = []
for a, b in zip(truth_locs, label_locs):
    if any(x < 0 for x in a[0]) or any(x < 0 for x in b):
        data.append(np.nan)
    else:
        data.append(np.linalg.norm(a[0] - b))

plt.plot(data, ".-")
plt.xlabel("Frame Number", fontsize=22)
plt.ylabel("Error (pixel)", fontsize=22)
plt.grid()
plt.savefig("pixel_error.pdf", bbox_inches='tight')
plt.tight_layout()
#plt.show()
