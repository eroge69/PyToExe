import matplotlib.pyplot as plt
import subprocess as exe
import numpy as np


t0 = input("t0:")
tend = input("tend:")
h = input("h:")
x01 = input("x01:")
x02 = input("x02:")
x03 = input("x03:")
x04 = input("x04:")
test=exe.Popen("C:\\Users\\New\\Desktop\\Proga\\2sem\\kontr\\zadacha2\\ITOG\\kr2.1.exe "+t0+" "+tend+" "+h+" "+x01+" "+x02+" " + x03+" "+x04,shell=True)


#//s=exe.Popen("C:\\Users\\New\\Desktop\\Proga\\2 sem\\kontr\\zadacha2\\ITOG\\kr 2.1.exe",shell=True, stdout=exe.PIPE)
#print(s.stdout.read())
#/plt.plot([1,2,3,4],[1,2,4,5])
#plt.show()
test.wait()
data=np.loadtxt("rk.txt", delimiter=' ', dtype=float)
plt.plot(data[:,0],data[:,1]) #y1(t)
plt.plot(data[:,0],data[:,2]) #y2(t)
plt.plot(data[:,0],data[:,3]) #y3(t)
plt.plot(data[:,0],data[:,4]) #y4(t)
# отображаем все кривые на одном графике
plt.show()
data=np.loadtxt("ei.txt", delimiter=' ', dtype=float)
plt.plot(data[:,0],data[:,1]) #y1(t)
plt.plot(data[:,0],data[:,2]) #y2(t)
plt.plot(data[:,0],data[:,3]) #y3(t)
plt.plot(data[:,0],data[:,4]) #y4(t)
# отображаем все кривые на одном графике
plt.show()

#print("  /n car")