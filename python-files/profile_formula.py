import math

h=float(input('ertefa ra vared konid: '))
tool=float(input('andaze zel ra vared konid: '))
L1=0
if h<=100:
   L1=38
if 100<h and h<=160:
   L1=35
if h>160:
   L1=32


L2=L1+4

x=math.floor((tool-17)/L1)

if (tool-17)/x > L2:
   n=x+2
else: 
   n=x+1



print('tedad profile: ',n)
  