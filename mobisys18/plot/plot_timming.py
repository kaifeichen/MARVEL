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
            networkTimes.append(float(line.split()[-7]) - float(line.split()[-2]))
            serverTimes.append(float(line.split()[-2]))
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

fig = plt.figure(figsize=(12, 5))
plt.stackplot(range(1,8), networkAvgs, serverAvgs)


plt.legend(loc="lower right")
plt.xlabel("Latency from Caputre to Appearance in Application (ms)", fontsize=22)
plt.ylabel("CDF", fontsize=22)
plt.grid()
#plt.savefig("sensor_latency.pdf", bbox_inches='tight')
plt.tight_layout()
plt.show()
