import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure(figsize=(6, 5))
plt.tick_params(axis='both', which='major', labelsize=20)
#ax = fig.add_subplot(111)
#ax.set_xticklabels(('25','50', '75', '100', '200'))

plt.xlabel(r"$\phi$ Vaule (pixel)", fontsize=22)
plt.ylabel("Calibration Counts", fontsize=22)
x = np.arange(0.5,5.5)
plt.bar(x, [4,4,2,2,1], align='center', alpha=0.5)
from matplotlib.ticker import MaxNLocator
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.xticks(x,('25','50', '75', '100', '200'))
plt.grid()
plt.ylim(ymax=5)
plt.tight_layout()
plt.savefig("eval_phi_cnt.pdf", bbox_inches='tight')
plt.show()


