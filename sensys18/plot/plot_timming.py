import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def getLatencyList(fileName):
    myFile = open(fileName)
    networkTimes = []
    serverTimes = []

    while(True):
        line = myFile.readline()
        if(len(line)>3):
            networkTimes.append((float(line.split()[-7]) - float(line.split()[-2]))/1000)
            serverTimes.append(float(line.split()[-2])/1000)
        else:
            break
    return [sum(networkTimes)/len(networkTimes), sum(serverTimes)/len(serverTimes)] 

networkAvgs = []
serverAvgs = []
for i in range(7):
    fileName = "../data/offloadingTime/offload_"+str(i+1)+".txt"
    result = getLatencyList(fileName)
    networkAvgs.append(result[0])
    serverAvgs.append(result[1])

fig = plt.figure(figsize=(8, 4))

#plt.plot([],[],color='c', label='Image Localization', linewidth=5)
#plt.plot([],[],color='m', label='Transmission', linewidth=5)

#plt.stackplot(range(1,8), networkAvgs, serverAvgs, colors=['m','c'])

ind = np.arange(len(networkAvgs))
width = 0.35
p1 = plt.bar(ind, networkAvgs, width, color='w', label='Transmission')
p2 = plt.bar(ind, serverAvgs, width, bottom=networkAvgs, color='g', label='Image Localization')


plt.legend(loc="upper left", fontsize=18)
plt.xlabel("Number of Images Offloaded", fontsize=24)
plt.ylabel("Offloading Time (s)", fontsize=24)
plt.xticks(ind+width/2, ind)
plt.xlim(xmin=-0.5)
plt.tick_params(axis='both', which='major', labelsize=24)
plt.grid(axis='y')
plt.savefig("mul_img_time.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
