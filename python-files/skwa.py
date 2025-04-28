import codecs
import tkinter as tk
from tkinter import filedialog
import re
def addArrs(arr, xx):
    arr[0]+=xx[0]
    arr[1]+=xx[1]
    arr[2]+=xx[2]
    arr[3]+=xx[3]
    arr[4]+=xx[4]
    arr[5]+=1
    return arr

def ifErr(x,y,deflt):
    f=deflt
    try:
      f=x/y
    except Exception:
      f = deflt
    stf = str(round(f,2)).replace('.',',')
    ms = stf.split(',')
    if len(ms)==1:
        stf=stf+',00'
    if len(ms)==2:
        ms[1]=ms[1]+'0'
        ms[1]=ms[1][:2:]
        stf=ms[0]+','+ms[1]
    return stf

root = tk.Tk()
root.withdraw()

file_path = 'skwa_in.csv'
print(file_path)
decs=['utf-8','cp1251','usc','usc-2','cp866','utf-16','utf-8-bom']
flag=False
for dec in decs:
  try:
    fr=codecs.open(file_path,'r',dec)
    lines = fr.readlines()
    fr.close()
    line = lines[1].replace('\n','')
    line = line.replace('\r','')
    line = line.replace('\t',';')
    
    p = line.split(';')
    if p[5]!='':
        flag = True
        print(dec)
        break
  except Exception:
    lines=[]
    flag=False 

d={}
x=0
for line in lines:
    if x>0:
        line = line.replace('\n','')
        line = line.replace('\r','')
        #line = line.strip()
        line = line.replace('\t',';')
        line = line.replace(',','.')
        p = line.split(';')
        try:
          xp=[float(p[1]),float(p[2]),float(p[3]),float(p[4]),float(p[5])]
        except Exception:
          print(x)
        ps = p[0].split(' ')
        for i in ps:
            d.update({i:addArrs(d.get(i,[0.0,0.0,0.0,0.0,0.0,0.0]),xp)})
    x+=1
st='слово'
st+=';повторений'
st+=';клики'
st+=';показы'
st+=';стоимость'
st+=';конверсии'
st+=';доход'
st+=';ctr'
st+=';cr'
st+=';cpa'
st+=';roi'+'\r'

if flag:
  #file_path_out = file_path[::-1][4::][::-1]+'_out.csv'

  file_path_out = filedialog.asksaveasfilename(filetypes=[('CSV',  '*.csv')], defaultextension='.csv')
  fw=codecs.open(file_path_out,'w','utf-8-sig')
  fw.write(st)
  for j in d:
    st=j
    st+=';'+str(round(d[j][5],2)).replace('.','.')
    st+=';'+str(round(d[j][0],2)).replace('.','.')
    st+=';'+str(round(d[j][1],2)).replace('.','.')
    st+=';'+str(round(d[j][2],2)).replace('.','.')
    st+=';'+str(round(d[j][3],2)).replace('.','.')
    st+=';'+str(round(d[j][4],2)).replace('.','.')
    st+=';'+str(ifErr(d[j][0]*100,d[j][1],0)).replace(',','.')
    st+=';'+str(ifErr(d[j][3]*100,d[j][0],0)).replace(',','.')
    st+=';'+str(ifErr(d[j][2],d[j][3],0)).replace(',','.')
    st+=';'+str(ifErr(d[j][4]*100,d[j][2],0)).replace(',','.')+'\r'
    fw.write(st)
  fw.close()
else:
  print("Что-то не то с файлом (кодировка или формат)")
  print("Для выхода нажмите Enter...")
  input()
