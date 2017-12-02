from label_video import *
import matplotlib.pyplot as plt
import numpy as snp
import sys

video_file = sys.argv[1]
file_hash = hashlib.md5(open(video_file, 'rb').read()).hexdigest()
truth_locs = np.array(read_data("." + file_hash + ".truth_locs"))
label_locs = np.array(read_data("." + file_hash + ".label_locs"))

print zip(truth_locs, label_locs)
diff = [np.linalg.norm(a[0] - b) for a, b in zip(truth_locs, label_locs)]
print len(truth_locs), len(label_locs)

plt.plot(diff)
plt.show()
