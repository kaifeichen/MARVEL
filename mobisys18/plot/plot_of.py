from label_video import *
import matplotlib.pyplot as plt
import numpy as snp
import sys

video_file = sys.argv[1]
file_hash = hashlib.md5(open(video_file, 'rb').read()).hexdigest()
truth_locs = np.array(read_data("." + file_hash + ".truth_locs"))
labels = read_data("." + file_hash + ".labels")

events = []
corrected = []
imu = []
of = []
for a, b in zip(truth_locs, labels):
    if any(x < 0 for x in a[0]) or b == None:
        events.append(np.nan)
        corrected.append(np.nan)
        imu.append(np.nan)
        of.append(np.nan)
    else:
        events.append(b[0])
        corrected.append(np.linalg.norm(a[0] - np.array(b[1])))
        imu.append(np.linalg.norm(a[0] - np.array(b[2])))
        of.append(np.linalg.norm(a[0] - np.array(b[3])))

fig = plt.figure(figsize=(12, 5))
seconds = [float(x)/30 for x in range(len(labels))]
plt.plot(seconds, corrected, "r-", label="Corrected", lw=2)
plt.plot(seconds, imu, "b:", label="IMU")
plt.plot(seconds, of, "g--", label="Optical Flow")

for i in range(len(events)):
    if events[i] == "Z":
        print "plot vertical line"
#        plt.axvline(x = i, c="r", ls="--")

plt.xlabel("Time (s)", fontsize=22)
plt.ylabel("Error (pixel)", fontsize=22)
plt.grid()
plt.legend(loc="upper left")
plt.xlim(xmax=80)
plt.ylim(ymax=180)
plt.savefig("eval_still.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
