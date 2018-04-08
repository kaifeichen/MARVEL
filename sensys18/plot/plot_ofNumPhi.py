import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure(figsize=(8, 4))
plt.tick_params(axis='both', which='major', labelsize=24)
#ax = fig.add_subplot(111)
#ax.set_xticklabels(('25','50', '75', '100', '200'))

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

plt.xlabel(r"Calibration Threshold $\phi$ Vaule (pixel)", fontsize=24)
plt.ylabel("Calibration Counts", fontsize=24)
x = np.arange(0.5,7.5)
rects = plt.gca().bar(x, [23,9,4,4,2,2,1], align='center', alpha=0.5)
from matplotlib.ticker import MaxNLocator
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.xticks(x,('0', '10', '25','50', '75', '100', '200'))
plt.grid(axis='y')
autolabel(rects, plt.gca(), "center")
plt.ylim(ymax=26)
plt.tight_layout()
plt.savefig("eval_phi_cnt.pdf", bbox_inches='tight')
plt.show()


