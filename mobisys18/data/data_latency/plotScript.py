import matplotlib.pyplot as plt
def getLatencyList(fileName):
    myFile = open(fileName)
    latencyDatas = []
    while(True):
        line = myFile.readline()
        if(len(line)>3):
            latencyDatas.append(float(line.split()[-1]))
        else:
            break
    return latencyDatas
l1 = getLatencyList("imageLantency.txt")
l2 = getLatencyList("gyroDelay.txt")
l3 = getLatencyList("magDelay.txt")
l4 = getLatencyList("accDelay.txt")
print(len(l1))
print(len(l2))
print(len(l3))
print(len(l4))
x_axis = range(1000)
plt.plot(x_axis, l1[0:1000], 'r.', x_axis, l2[0:1000], 'b.', x_axis, l3[0:1000], 'g.', x_axis, l4[0:1000], 'c.' )
plt.show()
