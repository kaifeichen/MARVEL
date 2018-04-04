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

fig = plt.figure(figsize=(6, 5))

plt.plot([],[],color='c', label='Image Localization', linewidth=5)
plt.plot([],[],color='m', label='Communication', linewidth=5)

plt.stackplot(range(1,8), networkAvgs, serverAvgs, colors=['m','c'])


plt.legend(loc="upper left", fontsize=18)
plt.xlabel("Number of Images Offloaded", fontsize=22)
plt.ylabel("Offloading Time (s)", fontsize=22)
plt.tick_params(axis='both', which='major', labelsize=20)
plt.grid()
plt.savefig("mul_img_time.pdf", bbox_inches='tight')
plt.tight_layout()
#plt.show()
