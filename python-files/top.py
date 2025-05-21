from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import string
import random
import time
import tempfile
import os
Root =Tk()
Root.geometry("1200x1000")
Root.title("CLASS SCHEDULING")
v1=StringVar()
v2=StringVar()
v3=StringVar()
v4=StringVar()
v5=StringVar()
v=StringVar()
v13=StringVar()
v14=StringVar()
v15=StringVar()
v16=StringVar()
v6=IntVar()
v7=IntVar()
v8=IntVar()
v9=IntVar()
v10=IntVar()
v11=IntVar()
v12=IntVar()
d1 = IntVar()
d2 = IntVar()
d3 = IntVar()
d4 = IntVar()
d5 = IntVar()
d6 = IntVar()
d7 = IntVar()
d8 = IntVar()
tna=[]
tnad=[]
tna1=[]
tnag=[]
sna=[]
snag=[]
snagn=[]
tem=[]
wee=[]
para=[]
gs=[]
fre=[]
kt=[]
ktt=[]
ks=[]
co=[]
cox=[]
added=[]
al= list(string.ascii_uppercase)
alg=[]
a,b,c,d,e,f,g,h,j,k,l,m,m1,m2,o=0,0,0,0,0,0,0,0,0,0,0,0,0,1,0
loc,loc2,loc3,loc5,loc7,p,p1=0,0,1,0,0,0,0
s0,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s14,s15,s16,s17,s18,s19,s20,s21,s22=True,True,True,True,False,True,True,False,True,False,True,True,False,False,True,False,False,True,False,True,True,True,True
loc4=""
loc7=""
def sho():
	global s7,s8,s0,s1,m,m1
	m=1
	z=3		
	k=len(tna)	
	t=int(time.strftime('%H'))
	if s0==True:
		for i in range(k):		
			tna[i]=tna[i] + "  (" + str(t+100+z) + ")"
			tna1[i]=tna1[i] + "(" + str(t+100+z) + ")"
			tnad[i]=tnad[i] + "(" + str(t+100+z) + ")"
			z+=1
		s0=False		
	fr1=Frame()
	fr2=Frame()
	fr3=Frame()	
	la1 = Label( fr1, text="Insert the name of a subject and click 'save' for each subject taught in the school.",font=("Calibri",15),justify="left")
	la1.pack()
	fr1.place(x=50,y=205)
	fr2=Frame()
	la2 = Label( fr2,text="Subject:",font=("Calibri",15),justify="left")
	la2.pack(side=LEFT)	
	en1 =Entry( fr2,textvariable=v4,font=("Calibri",15),justify="left")
	en1.pack(side=LEFT)	
	s1=v4.get()
	en1.delete(0,END)	
	if s7==True and s8==True:
		if m1>0:		
			if s1.isalpha()==FALSE:
				if len(s1)>15:
					s1=s1[:14] + "..."
				s5="Subject name:" + "'" + s1 + "'" + "is not name of a subject. \nPlease insert name of a subject.\n"
				m1=3	
		if m1==3:
			messagebox.showinfo("Error", s5 + "	Try again.")
		else:			
			s1=s1.capitalize()
			sna.append(s1)		
	m1=2					
	bu1 =Button( fr2, text="Save",font=("Calibri",12),command=sho,padx=5,pady=5,width=7)
	bu1.pack(side=LEFT)
	bu2 =Button( fr2, text="Next",font=("Calibri",12),command=ent2,padx=5,pady=5,width=7)
	bu2.pack(side=LEFT)		
	fr2.place(x=50,y=235)
	s7=True	
def ent2():
	global s1,s8,m2
	s8=False		
	fr4=Frame()
	pla1 = Label( fr4,text="What is the starting grade of the school?",font=("Calibri",15),justify="left")
	pla1.pack(side=LEFT)	
	pi1=Spinbox(fr4,textvariable=v6,from_=0,to=12,width=3,font=('Calibri', 15))
	pi1.pack(side=LEFT)	
	pbu1 =Button( fr4, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent3,width=7)	
	pbu1.pack(side=LEFT)	
	fr4.place(x=50,y=280)		
	t=len(sna)			
	tep=[]
	k1=0		
	k=""			
	for i in range(t):
		for ii in range(t):			
			if sna[i]==sna[ii] and i!=ii:				
				sna[ii]=" "*(m2)*(m2+1)
				m2+=m2					
	while(k1!=t):
		k=sna[k1]
		if k.isspace():
			sna.pop(k1)
			t-=1
		else:
			k1+=1			
def ent3():
	global a,s2,loc	
	if s2==True:
		a=v6.get()
		loc=a	
	s2=False		
	fr5=Frame()
	pla2 = Label( fr5,text="What is the last grade of the school?",font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT)	
	pi2=Spinbox(fr5,textvariable=v7,from_=a,to=12,width=3,font=('Calibri', 15))
	pi2.pack(side=LEFT)	
	pbu1 =Button( fr5, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent4,width=7)	
	pbu1.pack(side=LEFT)	
	fr5.place(x=600,y=280)	
def ent4():
	global a,b,loc,loc2,s3,s4,s6,al,alg,o,al			
	if s3==True:
		b=v7.get()	
	s3=False
	loc2=a
	if s4==True:
		if s6==True:
			n=v8.get()
			gs.append(n)
			o=0			
			for i in range(n):
				loc4=al[o]
				alg.append(loc4)				
				o+=1
			if loc==b:
				s6=False
			if loc < b:
				loc+=1				
	loc1=str(loc)	
	fr4=Frame()
	pla2 = Label( fr4,text="Insert number of sections for grade-" + loc1 + "    ",font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT)	
	pi2=Spinbox(fr4,textvariable=v8,from_=1,to=26,width=3,font=('Calibri', 15))
	pi2.pack(side=LEFT)	
	pbu1 =Button( fr4, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent4,width=7)	
	pbu1.pack(side=LEFT)
	pbu2 =Button( fr4, text="Next",font=("Calibri",12),padx=5,pady=5,command=ent5,width=7)		
	pbu2.pack(side=LEFT)	
	fr4.place(x=50,y=330)
	s4=True
def ent5():	
	fr10=Frame()	
	pla2 = Label( fr10,text="Insert the number of classes per day of the school.",font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT)
	pi2=Spinbox(fr10,textvariable=v9,from_=1,to=9,width=3,font=('Calibri', 15))
	pi2.pack(side=LEFT)			
	pbu1 =Button( fr10, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent6,width=7)	
	pbu1.pack(side=LEFT)	
	fr10.place(x=600,y=330)
def ent6():	
	global loc2,s4,s5,s9,s14,c	
	if s14==True:
		c=v9.get()
	s14=False					
	fr6=Frame()
	fr7=Frame()	
	loc3=str(loc2)
	loc4=loc3	
	pla2 = Label( fr6,text="Select a subject and click 'Save' for all subjcts of grade-" + loc3 ,font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT)	
	co2= ttk.Combobox(fr6,textvariable=v5,value = sna,width=50,height=50,font="Calibri 14 ")	
	co2.pack(side=LEFT)
	fr6.place(x=50,y=380)	
	pbu1 =Button( fr7, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent6,width=7)	
	pbu1.pack(side=LEFT)
	pbu2 =Button( fr7, text="Finished grade " + loc4,font=("Calibri",12),padx=5,pady=5,command=ent7,width=15)		
	pbu2.pack(side=LEFT)
	pbu3 =Button( fr7, text="Next",font=("Calibri",12),padx=5,pady=5,command=ent8,width=7)		
	pbu3.pack(side=LEFT)	
	fr7.place(x=500,y=420)
	if s5==True and s9==True:		
			n=v5.get()
			tem.append(n)	
	s9=True	
def ent7():
	global b,loc2,tem,s5,s10			
	k=""
	k1=0	
	t=len(tem)	
	if s10==True:
		for i in range(t):
			for ii in range(t):			
				if tem[i]==tem[ii] and i!=ii:				
					tem[ii]=" "*(i+1)*(ii+1)	
		while(k1!=t):
			k=tem[k1]
			if k.isspace():
				tem.pop(k1)
				t-=1
			else:
				k1+=1	
		for i in range(t):
			k=tem[i]		
			snag.append(k)
		k1=len(tem)
		snagn.append(k1)			
		tem.clear()			
	if loc2==b:
		s5=False							
	if b > loc2:
		loc2+=1		
	fr6=Frame()
	loc3=str(loc2)
	pla2 = Label( fr6,text="Select a subject and click 'Save' for all subjcts of grade-" + loc3 ,font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT)
	fr6.place(x=50,y=380)
def ent8():
	global wee,a,loc3,loc5,s10
	loc3=a	
	loc5=0			
	fr8=Frame()
	fr9=Frame()
	fr10=Frame()		
	pla1 = Label( fr8,text="Select class days \nand click 'Save'.",font=("Calibri",15),justify="left")
	pla1.pack(side=LEFT)	
	C1 = Checkbutton(fr8, text = "Monday", variable = d1, height=3, width = 9,font=("Calibri",15))
	C1.pack(side=LEFT)
	C2 = Checkbutton(fr8, text = "Tuesday", variable = d2, height=3, width = 9,font=("Calibri",15))
	C2.pack(side=LEFT)
	C3 = Checkbutton(fr8, text = "Wendesday", variable = d3, height=3, width = 9,font=("Calibri",15))
	C3.pack(side=LEFT)
	C4 = Checkbutton(fr8, text = "Thursday", variable = d4, height=3, width = 9,font=("Calibri",15))
	C4.pack(side=LEFT)
	C5 = Checkbutton(fr8, text = "Friday", variable = d5, height=3, width = 9,font=("Calibri",15))
	C5.pack(side=LEFT)
	C6 = Checkbutton(fr8, text = "Saturday", variable = d6,	height=3, width = 9,font=("Calibri",15))
	C6.pack(side=LEFT)
	C7 = Checkbutton(fr8, text = "Sunday", variable = d7, height=3, width = 9,font=("Calibri",15))
	C7.pack(side=LEFT)
	fr8.place(x=50,y=460)	
	pbu1 =Button( fr9, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent9,width=7)	
	pbu1.pack(side=LEFT)	
	fr9.place(x=1040,y=478)		
	s10=False			
def ent9():
	global a,b,d,e,k,p1,loc3,loc4,loc5,loc7,s12,s11,j,l,snag,fre,wee,tna,pla3		
	loc7=a		
	k=0			
	if s11==True:					
		if d1.get()==1:
			wee.append("Monday")		
		if d2.get()==1:
			wee.append("Tuesday")		
		if d3.get()==1:
			wee.append("Wendesday")		
		if d4.get()==1:
			wee.append("Thursday")		
		if d5.get()==1:
			wee.append("Friday")		
		if d6.get()==1:
			wee.append("Saturday")		
		if d7.get()==1:
			wee.append("Sunday")
	s11=False		
	d=len(wee)				
	if s12==True and e < len(snag):		
		n=v10.get()
		fre.append(n)
		e+=1
		l+=1
		if snagn[p1]==l:
			p1+=1
			l=0
			if loc3!=b:
				loc3+=1				
	loc4=str(loc3)					
	fr11=Frame()	
	fr12=Frame()
	fr16=Frame()	
	pla2 = Label( fr11,text="Insert the frequency per week and click 'Save' for grade " +  loc4 + " of the subject below." ,font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT);
	fr11.place(x=50,y=535)
	if s12==True:
		pla3.config(text = "")		
	if e < len(snag):			
		pla3 = Label( fr16,text=snag[e] ,font=("Calibri",15),justify="left")
	pla3.pack(side=LEFT);	
	fr16.place(x=50,y=560)
	pi2=Spinbox(fr12,textvariable=v10,from_=1,to=c*d,width=3,font=('Calibri', 15))
	pi2.pack(side=LEFT)			
	pbu1 =Button( fr12, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent9,width=7)	
	pbu1.pack(side=LEFT)	
	pbu3 =Button( fr12, text="Next",font=("Calibri",12),padx=5,pady=5,command=ent10,width=7)		
	pbu3.pack(side=LEFT)
	fr12.place(x=500,y=585)							
	s12=True			
def ent10():
	global e,s11,s13,tna,loc7,p,snag,co,cox,al,alg,f,g,h,k,s13,pla4	
	fr11=Frame()
	s=len(alg)
	if e!=len(snag):
		pla2 = Label( fr11,text="You have not finished inserting, please start again. " ,font=("Calibri",15),justify="left")
		pla2.pack(side=LEFT);
		fr11.place(x=600,y=800)
	if s13==True and p != s:		
		n=v.get()
		co.append(n)
		m1=tna.index(n)
		cox.append(m1)
		k+=1		
		if snagn[h]==k:
			p+=1		
			g=k
			k=0
			if p != s:
				if alg[p]=="A":
					loc7+=1
					f+=g			
					h+=1
	loc6=str(loc7)		
	fr12=Frame()	
	fr13=Frame() 
	fr14=Frame()
	fr15=Frame()
	if p < s:
		pla2 = Label( fr12,text="Select a teacher and click 'Save' for grade-" + loc6 + alg[p] + " who teaches the subjct below." ,font=("Calibri",15),justify="left")
		pla2.pack(side=LEFT)
	fr12.place(x=50,y=625)
	if s13==True:
		pla4.config(text = "")
	if p < s:		
		pla4 = Label( fr15,text= "'" + snag[f+k] + "'" + "."  ,font=("Calibri",15),justify="left")
		pla4.pack(side=LEFT)
		fr15.place(x=50,y=655)	
	pla5 = Label( fr13,text= "Teacher name with computer generated code:"  ,font=("Calibri",15),justify="left")
	pla5.pack(side=LEFT)			
	co2= ttk.Combobox(fr13,textvariable=v,value = tna,width=50,height=50,font="Calibri 14 ")	
	co2.pack(side=LEFT)
	fr13.place(x=50,y=685)
	pbu1 =Button( fr14, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent10,width=7)	
	pbu1.pack(side=LEFT)	
	pbu3 =Button( fr14, text="Next",font=("Calibri",12),padx=5,pady=5,command=ent11,width=7)		
	pbu3.pack(side=LEFT)
	fr14.place(x=600,y=715)		
	s13=True		
def ent11():
	global tna,tnag,snagn,added,gs,alg,co,cox,fre,kt,ktt,ks,a,b,c,d,s15,s16,s17
	s13=False
	p=0
	e=0
	x=c*d
	coz=[]
	tem=[]
	puf=[]
	k1=0
	st=""
	if s17==True:
		for i in range(b-a+1):
			for ii in range(snagn[i]):			
				e=e+fre[p]
				p+=1		
			if x < e:
				st=st + "-Over frequency per week for grade " + str(a+i) + "\n"
				s16=True
			if x > e:
				st=st + "-Low frequency per week for grade" + str(a+i) + "\n"
				s16=True			
			e=0	
		p=len(cox)
		for i in range(p):
			coz.append(cox[i])
		for i in range(p):
			for ii in range(p):			
				if coz[i]==coz[ii] and i!=ii:				
					coz[ii]=-1
		while(k1!=p):
			if coz[k1]==-1:
				coz.pop(k1)
				p-=1
			else:
				k1+=1
		for i in range(len(coz)):
			tnag.append(coz[i])
		x=c*d	
		p=len(cox)
		t=0
		t1=0
		e=0
		if len(coz) < len(alg):		
			st=st + "-Less number of teachers than the available teaching class room(s).\n"
			s16=True
		for i in tnag:				
			t=0
			t1=0
			e=0
			for ii in range(b-a+1):
				tem.clear()
				for s in range(snagn[ii]):
					tem.append(fre[t])
					t+=1
				for si in range(gs[ii]):
					coz.clear()
					for sii in range(snagn[ii]):
						coz.append(cox[t1])
						t1+=1
					for sii in range(len(coz)):
						if i==coz[sii]:
							e=e + tem[sii]				
			if e > x:
				st=st + "-Teacher " + str(tna[tnag[i]]) + " is over loaded.\n"
				s16=True
		if s16==True:
			messagebox.showinfo("Error report.", st + "	Try again.")
		else:
			messagebox.showinfo("Success report.", "You have successfully inserted school information.")
		s17=False
	fr1=Frame()
	pla2 = Label( fr1,text="Choose the type of Scheduling you want." ,font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT);	
	pbu1 =Button( fr1, text="Normal Scheduling",font=("Calibri",12),padx=5,pady=5,command=ent12,width=20)	
	pbu1.pack(side=LEFT)	
	pbu3 =Button( fr1, text="Parcially Scheduled Scheduling",font=("Calibri",12),padx=5,pady=5,command=ent13,width=40)		
	pbu3.pack(side=LEFT)
	fr1.place(x=50,y=775)	
def ent12():
	global tna,tnag,snagn,added,wee,gs,alg,co,cox,fre,kt,ktt,ks,a,b,c,d,s15,s22																	
	f,g,h,k=0,0,0,0
	coz=[]
	tem=[]
	puf=[]
	data=[]
	buff=0	
	bufs=""
	buf=-1
	t1=0
	x=c*d	
	s=0	
	y=0
	y1=0
	y2=0	
	p=0
	h1=len(alg)
	p1=h1
	p1=p1*x
	x1=x
	p2=len(para)
	s21=True
	tt=int(time.strftime('%H'))
	if tt % 2==0: 
		s21=True
	else:
		s21=False	
	for iiiii in range(p1):
				ktt.append("")																					
				kt.append(-1)
				ks.append("")
	coz.clear()
	for i in range(b-a+1):
		q=snagn[i]						
		for ii in range(gs[i]):
			a1=0
			qq=q			
			q1=0
			xx=0			
			q4=0			
			y3=0		
			y2=y1
			x1=x-q			
			puf.clear()
			coz.clear()
			tem.clear()
			for si in range(q):
				puf.append(fre[si + s])
				coz.append(cox[y])
				y+=1
			for si in range(q):
				tem.append(snag[si+s])							
			for iii in range(d):				
				for iiii in range(c):
					if qq > 2:
						if s21==True and y1%c !=0:
							if ks[y1-1]==tem[f]:
								if f+1==qq:
									f=0
								else:
									f+=1
							if ks[y1+1]==tem[f]:
								if f+1==qq:
									f=0
								else:
									f+=1
						else:						
							if ks[y2+x1+xx+q1-1]==tem[f] and (y2+x1+xx+q1)%c !=0:
								if f+1==qq:
									f=0
								else:
									f+=1
							if (y2+x1+xx+q1+1)<p1 and (y2+x1+xx+q1)%c !=0 :
								if ks[y2+x1+xx+q1+1]==tem[f]:
									if f+1==qq:
										f=0
									else:
										f+=1
					else:
						if s21==True:
							if ks[y1-1]==tem[f] and y1+1<p1:
								if ks[y1+1]!="" and ks[y1+1]!=tem[f]:
									ks[y1]=ks[y1+1]
									y1+=1
							if y1+1<p1 and (y1+1)%c!=0:
								if ks[y1+1]==tem[f]:
									if ks[y1-1]!=tem[f]:
										ks[y1]=ks[y1-1]
										y1-=1														
						else:												
							if ks[y2+x1+xx+q1-1]==tem[f] and y1+1<p1 and (y2+x1+xx+q1+1)<p1:
								if ks[y2+x1+xx+q1+1]!=tem[f]:
									ks[y2+x1+xx+q1]=ks[y2+x1+xx+q1+1]
									ks[y2+x1+xx+q1+1]=""
									a1=1
							if (y2+x1+xx+q1+1)<p1 and (y2+x1+xx+q1+1)%c!=0:
								if ks[y2+x1+xx+q1+1]==tem[f]:
									if ks[y2+x1+xx+q1-1]!="" and ks[y2+x1+xx+q1-1]!=tem[f]:
										ks[y2+x1+xx+q1]=ks[y2+x1+xx+q1-1]
										a1-=1						
					if s21==True:
						while(h!=p):
							p=0
							for si in range(h):										
								if kt[y3 + si*x]==coz[f]:
									if f < (qq-1):
										f+=1
										continue
									else:
										f=0
										continue
								else:
									p+=1
					else:
						while(h!=p):
							p=0
							for si in range(h):										
								if kt[x1+q1+xx+si*x]==coz[f]:
									if f < (qq-1):
										f+=1
										continue
									else:
										f=0
										continue
								else:
									p+=1
					if s21==True:						
						ktt[y1]=(tna1[coz[f]])																					
						kt[y1]=(coz[f])
						ks[y1]=(tem[f])						
						puf[f]-=1
						if puf[f]==0:
							puf.remove(0)																												
							coz.remove(coz[f])
							tem.remove(tem[f])
							qq-=1
							f-=1
							q4-=1
							xx+=1							
						if f+1==qq:
							f=0
						else:
							f+=1
						y1+=1
						y3+=1								
						if q4+1<qq:
							s21=True
							q1+=1
							q4+=1
						else: 
							s21=False
							q1=0
							q4=0
						if (f==0):
							t1=0
							for ex in range(int(qq/2)):
								buf=coz[2*t1]
								bufs=tem[2*t1]
								buff=puf[2*t1]
								coz[2*t1]=coz[2*t1+1]
								tem[2*t1]=tem[2*t1+1]
								puf[2*t1]=puf[2*t1+1]
								coz[2*t1+1]=buf
								tem[2*t1+1]=bufs
								puf[2*t1+1]=buff
								t1+=1
							if qq>2 and qq%2==1:
								buf=coz[0]
								bufs=tem[0]
								buff=puf[0]
								coz[0]=coz[qq-1]
								tem[0]=tem[qq-1]
								puf[0]=puf[qq-1]
								coz[qq-1]=buf
								tem[qq-1]=bufs
								puf[qq-1]=buff																								
					else:																		
						ktt[y2+x1+xx+q1+a1]=(tna1[coz[f]])																					
						kt[y2+x1+xx+q1+a1]=(coz[f])
						ks[y2+x1+xx+q1+a1]=(tem[f])						
						puf[f]-=1
						if puf[f]==0:
							puf.remove(0)																												
							coz.remove(coz[f])
							tem.remove(tem[f])
							qq-=1
							f-=1
							q4-=1																																					
						if f+1==qq:
							f=0
						else:
							f+=1																												
						if q4+1<qq:
							s21=False
							q1+=1
							q4+=1
							a1=0																															
						else: 						
							s21=True
							q1=0
							q4=0
							x1-=qq							
							xx=0
							a1=0
						if (f==0):
							t1=0
							for ex in range(int(qq/2)):
								buf=coz[2*t1]
								bufs=tem[2*t1]
								buff=puf[2*t1]
								coz[2*t1]=coz[2*t1+1]
								tem[2*t1]=tem[2*t1+1]
								puf[2*t1]=puf[2*t1+1]
								coz[2*t1+1]=buf
								tem[2*t1+1]=bufs
								puf[2*t1+1]=buff
								t1+=1
							if qq>2 and qq%2==1:
								buf=coz[0]
								bufs=tem[0]
								buff=puf[0]
								coz[0]=coz[qq-1]
								tem[0]=tem[qq-1]
								puf[0]=puf[qq-1]
								coz[qq-1]=buf
								tem[qq-1]=bufs
								puf[qq-1]=buff	
					p=0
			h+=1
			y1=h*x								
		s=s+snagn[i]
	ly=len(ktt)
	added1=[]
	for i in range(ly):
		f=len(ks[i])
		g=len(ktt[i])
		st1=ks[i]
		st1=st1[:15]
		st2=ktt[i]
		st2=st2[:8] + st2[g-5:]
		added.append(st1 + "/" + st2)
		st1=ks[i]
		st2=ktt[i]		
		if f<10:
			k=9-f
			st1=st1 + k*" "
		else:
			st1=st1[:9]
		if g>1:		
			st2=st2[:2] + st2[g-5:]
		added1.append(st1 + "/" + st2)		
	v=1
	w=0
	z=1
	z1=1
	wee.insert(0," ")
	data1=" "	
	st="Grade-" + str(z1) + alg[0]
	data1=data1 + st	
	for j in range(d-1):
		data1=data1 + " "	
	data.append(str(data1))
	data1=""	
	for j in range(d + 1):
		data1=data1 + wee[j] + " "					
	data.append(str(data1))
	for i in range(h*c):
		data1=""		
		data1=str(v)
		for j in range(d):			
			data1=data1 + added[w + j*c ] + " "
		dat=str(data1)
		data.append(dat)		
		w+=1
		v+=1			
		if (i + 1) % c == 0:
			if h != z:
				if alg[z] == "A":
					z1+=1			
				data1=""
				for j in range(d):
					data1=data1 + " "
				dat=str(data1)		
				data.append(dat)								
				data1=" "	
				st="Grade-" + str(z1) + alg[z]
				data1=data1 + st
				data.append(data1)				
				data1=""				
				for j in range(d+1):
					data1=data1 + wee[j] + " "					
				data.append(str(data1))
			v=1
			w=x*z
			z+=1		
	if s22==True:	
		root=Toplevel()		
		root.geometry("1200x500")
		root.title("Scheduled result")
		canvas = Canvas(root)
		scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
		scr = Frame(canvas)
		scr.bind(
	    	"<Configure>",
	    	lambda e: canvas.configure(
	        	scrollregion=canvas.bbox("all")))
		canvas.create_window((0, 0), window=scr, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)	
		index=0	
		def read_data():
   			global y
   			for index, line in enumerate(data):    
      				tree.insert('', END, iid = index,
        			text= line[0],values = line[1:])
		columns = ("A", "B","C","D", "E","F","G")
		tree= ttk.Treeview(scr, columns=columns ,height = 20)
		tree.pack(padx = 5, pady = 5)
		tree.heading('#0', text='Period ')
		tree.heading("A", text='DAY1')
		tree.heading("B", text='DAY2')
		tree.heading("C", text='DAY3')
		tree.heading("D", text='DAY4')
		tree.heading("E", text='DAY5')
		tree.heading("F", text='DAY6')
		tree.heading("G", text='DAY7')
		g=Label(scr, text=read_data())	
		g.pack()   
		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
		s22=False
		lz=0		
		gr=1
		gr1=0
		txt=""
		wee1=[]
		txt='\b' + '\b' + "TIME TABLE" + '\n'
		pro=0		
		for wewe in range(d):
			if wee[wewe+1]=="Monday":
				wee1.append("Monday   ")
			if wee[wewe+1]=="Tuesday":
				wee1.append("Tuesday  ")
			if wee[wewe+1]=="Wendesday":
				wee1.append("Wendesday")
			if wee[wewe+1]=="Thursday":
				wee1.append("Thursday ")
			if wee[wewe+1]=="Friday":
				wee1.append("Friday   ")
			if wee[wewe+1]=="Saturday":
				wee1.append("Saturday ")
			if wee[wewe+1]=="Sunday":
				wee1.append("Sunday  ")	
		for xyz in range(h1):					
			added1.insert(lz, "Period")
			lz+=1
			for zy in range(c):
				added1.insert(lz,str(1+zy))
				lz+=1
			for yz in range(d):
				added1.insert(lz+(c+1)*yz, wee1[yz] + "/" + "DAY " + "(" + str(1+yz) + ")")
			lz=(xyz+1)*(c+1)*(d+1)
		lz=0
		ly=ly+h1*(1+d+c)
		txt=txt + '\n' + '\n'
		txt=txt + "Teacher Name and Code" + '\n'
		for xyz in range(len(tna)):
			txt=txt + tnad[xyz] + '\n'		
		while(lz<ly):
			txt=txt + '\n' + '\n'	
			st='\t' + "Grade-" + str(gr) + alg[gr1]	
			txt=txt + st
			txt=txt + '\n'					
			for dt in range(c+1):
				for dtt in range(d+1):
				    txt=txt + added1[pro + dt + dtt*(c+1)] + '\t'
				    lz+=1
				txt=txt + '\n'	
			gr1+=1
			pro=gr1*(c+1)*(d+1)
			if (gr1<h1):
				if (alg[gr1])== "A":
					gr+=1
		print(txt)				
		def ent(txt):	
			temp_file=tempfile.mktemp('.txt')
			open(temp_file,'w').write(txt)
			os.startfile(temp_file, 'print')				
		prin =Button( scr, text="Print",font=("Calibri",12),padx=5,pady=5,command=lambda:ent(txt),width=20)	
		prin.pack(side=BOTTOM)
def ent13():
	global tna,tnag,gs,snag,a,b,al,wee,c,s21
	if s21==True:
		root=Toplevel()
		root.title("Pre-scheduled information")	
		root.geometry("1000x500")
		s21=False	
	tep=[]
	tep1=[]
	teps=[]		
	tep.append(tnag[0])
	teps.append(snag[0])
	t=1
	m=0	
	k=len(tnag)
	for i in range(k):
		m=0		
		while True:
			if tep[m]==tnag[i]:
				break
			if (m+1)==t:				
				tep.append(tnag[i])
				t+=1
				break
			m+=1
	k=len(tep)
	for i in range(k):
		tep1.append(tna[tep[i]])
	t=1
	m=0	
	k=len(snag)
	for i in range(k):
		m=0		
		while True:
			if teps[m]==snag[i]:				
				break
			if (m+1)==t:
				teps.append(snag[i])
				t+=1
				break
			m+=1
	al11=[]	
	gs.sort()	
	al12=(gs[b-a])	
	for i in range(al12):
		al11.append(al[i])	
	fr=Frame(root)
	fr1=Frame(root)
	fr2=Frame(root)
	fr3=Frame(root)	
	fr4=Frame(root)
	la1 = Label( fr, text="INSERT PRE-SCHEDULED CLASS INFORMATION\n AND CLICK 'Save' FOR EACH SCHEDULED ONE. WHEN YOU FINISH INSERTING CLICK 'Finish'.",foreground="blue", justify="center",font=("Elephant",12,"underline") ,pady=50)
	la1.pack()	
	fr.place(x=10,y=5)
	pla1 = Label( fr1,text= "Teacher name with \ncomputer generated code:"  ,font=("Calibri",15),justify="left")
	pla1.pack(side=LEFT)			
	co1= ttk.Combobox(fr1,textvariable=v13,value = tep1,width=50,height=50,font="Calibri 14 ")	
	co1.pack(side=LEFT)
	fr1.place(x=50,y=135)
	pla2 = Label( fr2,text= "Subject:"  ,font=("Calibri",15),justify="left")
	pla2.pack(side=LEFT)			
	co2= ttk.Combobox(fr2,textvariable=v14,value = teps,width=50,height=50,font="Calibri 14 ")	
	co2.pack(side=LEFT)
	fr2.place(x=50,y=200)
	pla3 = Label( fr3,text= "Grade:"  ,font=("Calibri",15),justify="left")
	pla3.pack(side=LEFT)			
	co3= Spinbox(fr3,textvariable=v11,from_=a,to=b,width=3,font="Calibri 14 ")	
	co3.pack(side=LEFT)	
	pla4 = Label( fr3,text= "Section:"  ,font=("Calibri",15),justify="left")
	pla4.pack(side=LEFT)			
	co4= ttk.Combobox(fr3,textvariable=v15,value = al11,width=3,height=50,font="Calibri 14 ")	
	co4.pack(side=LEFT)	
	pla5 = Label( fr3,text= "Day:"  ,font=("Calibri",15),justify="left")
	pla5.pack(side=LEFT)			
	co5= ttk.Combobox(fr3,textvariable=v16,value = wee,width=12,height=10,font="Calibri 14 ")	
	co5.pack(side=LEFT)	
	pla6 = Label( fr3,text= "Class period:"  ,font=("Calibri",15),justify="left")
	pla6.pack(side=LEFT)			
	co6= Spinbox(fr3,textvariable=v12,from_=1,to=c,width=3,font="Calibri 14 ")	
	co6.pack(side=LEFT)
	fr3.place(x=50,y=250)
	pbu1 =Button( fr4, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent14,width=7)	
	pbu1.pack(side=LEFT)	
	pbu2 =Button( fr4, text="Finish",font=("Calibri",12),padx=5,pady=5,command=ent15,width=7)
	pbu2.pack(side=LEFT)		
	pbu3 =Button( fr4, text="Cancel",font=("Calibri",12),padx=5,pady=5,command=root.destroy,width=10)
	pbu3.pack(side=LEFT)		
	fr4.place(x=600,y=385)
def ent14():
	global para,s19
	if s19==True:
		u=v11.get()
		v=v15.get()
		w=v16.get()
		x=v12.get()
		y=v13.get()
		z=v14.get()		
		para.append([u,v,w,x,y,z])	
def ent15():
	global para,tna,tnag,snagn,added,wee,gs,alg,al,co,cox,fre,kt,ktt,ks,a,b,c,d,s15,s18,s19,s20	
	s19=False											
	f,g,h,k=0,0,0,0	
	coz=[]
	tem=[]
	temp=[]
	temp1=[]	
	puf=[]
	data=[]	
	x=c*d	
	s=0	
	y=0
	y1=0
	p=0
	y2=0
	p1=len(alg)
	h1=p1
	p1=p1*x
	p2=len(para)
	su=0
	cu=0
	su1=0
	cu1=0
	cu2=0
	s21=True
	tt=int(time.strftime('%H'))	
	st=""
	if tt % 2==0: 
		s21=True
	else:
		s21=False
	for ij in range(p2):
		temp.append(para[ij][4])
	for ij in range(p2):
		temp1.append(para[ij][5])
	if s20==True: 		
		for ij in range(p2):
			if para[ij][0]!=1:
				for i in range(para[ij][0]-1):				
					su=su + gs[i]*snagn[i]
			su=su + snagn[para[ij][0]-1]*al.index(para[ij][1]) 
			for jj in range(snagn[para[ij][0]-1]):			
				if co[su]==para[ij][4]:
					for jjj in range(para[ij][0]-1):
						su1=su1 + snagn[jjj]	
					for jjjj in range(snagn[para[ij][0]-1]):
						if snag[su1]==para[ij][5]:
							if cu==cu1:
								s18=True
								if temp.count(para[ij][4])>0:										
									if temp1[temp.index(para[ij][4])]==para[ij][5]:
										for jx in range(p2):
											if para[jx][4]==para[ij][4] and para[jx][5]==para[ij][5]:
												temp.remove(para[ij][4])
												temp1.remove(para[ij][5])
												cu2+=1
										if cu2 > fre[su1]:
											st=st + "*The frequency of subject " + para[ij][5] + " is " + str(fre[su1]) + " not " + str(cu2) + " for grade " + str(para[ij][0]) + ".\n"							
									cu2=0							
							su1+=1
							cu1+=1
						su1=0
						cu1=0					
				su+=1
				cu+=1
			if s18==False:
				if temp.count(para[ij][4])>0:
					if temp1[temp.index(para[ij][4])]==para[ij][5]:
		 				st=st + "-Teacher " + para[ij][4] + " does not teach subject " + para[ij][5] + " in grade " + str(para[ij][0]) + para[ij][1] + ".\n"
					for jx in range(p2):
						if para[jx][4]==para[ij][4] and para[jx][5]==para[ij][5]:
							temp.remove(para[ij][4])
							temp1.remove(para[ij][5])						
			s18=False
			su=0
			cu=0
	if s20==True:
		for jx in range(p2):
			for jxx in range(p2):
				if jx!=jxx:
					if para[jx][0]==para[jxx][0]:
						if para[jx][1]==para[jxx][1]:
							if para[jx][2]==para[jxx][2]:
								if para[jx][3]==para[jxx][3]:
									st=st + "** Grade" +  str(para[jx][0]) + "," + "section" + str(para[jx][1]) + "," + "on " + para[jx][2] + "," + "period" "," + para[jx][3] + " is aready assigned.\n"
	if s20==True:
		if st=="":
			messagebox.showinfo("Success report.", "Your pre-scheduling is successful.")
			s20=False
			for iiiii in range(p1):
				ktt.append("")																					
				kt.append(-1)
				ks.append("")	
		else:
			messagebox.showinfo("Error report.", st + "	Cancel and try again.")
			s20=False				
	for ij in range(p2):
		pj=para[ij][0]
		pj1=para[ij][1]
		pj2=para[ij][2]
		pj3=para[ij][3]
		pj4=para[ij][4]
		pj5=para[ij][5]
		sj=0
		for iij in range(pj-1):
			sj=sj + gs[iij]
		sj=sj + al.index(pj1)
		sj=sj*x
		sj=sj + c*wee.index(pj2)
		sj=sj + pj3-1																							
		kt[sj]=tna.index(pj4)
		ktt[sj]=tna1[kt[sj]]
		ks[sj]=pj5
	p3=0		
	coz.clear()
	for i in range(b-a+1):
		q=snagn[i]
		tem.clear()
		for si in range(q):
			tem.append(snag[si+s])			
		for ii in range(gs[i]):
			qq=q
			xx=0
			q4=0			
			q1=0			
			y3=0		
			y2=y1
			x1=x-q	
			puf.clear()
			coz.clear()
			for si in range(q):
				puf.append(fre[si + s])
				coz.append(cox[y])
				y+=1
			for ijj in range(p2):
				if (i+1)==para[ijj][0]:
					for ijjj in range(gs[i]):
						if ii==al.index(para[ijj][1]):
							p3=tem.index(para[ijj][5])
							puf[p3]-=1																				
			for iii in range(d):
				for iiii in range(c):					
					if qq > 2:
						if s21==True:
							if ks[y1-1]==tem[f]:
								if f+1==qq:
									f=0
								else:
									f+=1
							if ks[y1+1]==tem[f]:
								if f+1==qq:
									f=0
								else:
									f+=1
						else:						
							if ks[y2+x1+xx+q1]==tem[f]:
								if f+1==qq:
									f=0
								else:
									f+=1
							if ks[y2+x1+xx+q1]==tem[f]:
								if f+1==qq:
									f=0
								else:
									f+=1
					if s21==True:
						while(h1!=p):
							p=0
													
							for si in range(h1):										
								if kt[y3+si*x]==coz[f]:
									if f+1==qq:
										f=0
										continue
									else:
										f+=1
										continue
								else:
									p+=1
								
					else:
						while(h1!=p):
							p=0
							for si in range(h1):																
								if kt[x1+q1+xx+si*x]==coz[f]:
									if f+1==qq:
										f=0
										continue
									else:
										f+=1
										continue
								else:
									p+=1								
					if s21==True:
						if ktt[y1] == "":							
							ktt[y1]=(tna1[coz[f]])																					
							kt[y1]=(coz[f])
							ks[y1]=(tem[f])
							puf[f]-=1
							if puf[f]==0:
								puf.remove(0)																												
								coz.remove(coz[f])
								tem.remove(tem[f])
								qq-=1
								f-=1
								q4-=1
								xx+=1
							if f+1==qq:
								f=0
							else:
								f+=1
							y1+=1
							y3+=1
						else:
							y1+=1
							y3+=1									
						if q4+1<qq:
							s21=True
							q1+=1
							q4+=1
						else: 
							s21=False
							q1=0
							q4=0									
					else:
						if ktt[y2+x1+xx+q1] != "":
							while ktt[y2+x1+xx+q1] != "":								
								q1+=1
								q4+=1
						if ktt[y2+x1+xx+q1] == "":													
							ktt[y2+x1+xx+q1]=(tna1[coz[f]])																					
							kt[y2+x1+xx+q1]=(coz[f])
							ks[y2+x1+xx+q1]=(tem[f])
							puf[f]-=1
							if puf[f]==0:
								puf.remove(0)																												
								coz.remove(coz[f])
								tem.remove(tem[f])
								qq-=1
								f-=1
								q4-=1															
							if f+1==qq:
								f=0
							else:
								f+=1																														
						if q4+1<qq:
							s21=False
							q1+=1
							q4+=1																	
						else: 						
							s21=True
							q1=0
							q4=0	
							x1-=qq		
							xx=0
					p=0				
			h+=1
			y1=h*x
			p=0					
		s=s+snagn[i]		
	for i in range(len(ktt)):
		added.append(ks[i] + "/" + ktt[i])	
	root=Toplevel()		
	root.geometry("1200x1000")
	root.title("Scheduled result(parcially scheduled)")		
	v=1
	w=0
	z=1
	z1=1
	wee.insert(0," ")
	data1=" "	
	st="Grade-" + str(z1) + alg[0]
	data1=data1 + st	
	for j in range(d-1):
		data1=data1 + " "	
	data.append(str(data1))
	data1=""	
	for j in range(d + 1):
		data1=data1 + wee[j] + " "					
	data.append(str(data1))
	for i in range(h*c):
		data1=""		
		data1=str(v)
		for j in range(d):			
			data1=data1 + added[w + j*c ] + " "
		dat=str(data1)
		data.append(dat)		
		w+=1
		v+=1			
		if (i + 1) % c == 0:
			if h != z:
				if alg[z] == "A":
					z1+=1			
				data1=""
				for j in range(d):
					data1=data1 + " "
				dat=str(data1)		
				data.append(dat)								
				data1=" "	
				st="Grade-" + str(z1) + alg[z]
				data1=data1 + st
				data.append(data1)				
				data1=""				
				for j in range(d+1):
					data1=data1 + wee[j] + " "					
				data.append(str(data1))
			v=1
			w=x*z
			z+=1		
	canvas = Canvas(root)
	scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
	scr = Frame(canvas)
	scr.bind(
	    "<Configure>",
	    lambda e: canvas.configure(
	        scrollregion=canvas.bbox("all")
	    )
	)
	canvas.create_window((0, 0), window=scr, anchor="nw")
	canvas.configure(yscrollcommand=scrollbar.set)	
	index=0	
	def read_data():
   		global y
   		for index, line in enumerate(data):    
      			tree.insert('', END, iid = index,
        		text= line[0],values = line[1:])
	columns = ("A", "B","C","D", "E","F","G")
	tree= ttk.Treeview(scr, columns=columns ,height = 20)
	tree.pack(padx = 5, pady = 5)
	tree.heading('#0', text='Period ')
	tree.heading("A", text='DAY1')
	tree.heading("B", text='DAY2')
	tree.heading("C", text='DAY3')
	tree.heading("D", text='DAY4')
	tree.heading("E", text='DAY5')
	tree.heading("F", text='DAY6')
	tree.heading("G", text='DAY7')
	g=Label(scr, text=read_data())	
	g.pack()   
	canvas.pack(side="left", fill="both", expand=True)
	scrollbar.pack(side="right", fill="y")		
def ent1():	
	global m,s0			
	fr1=Frame()
	la1 = Label( fr1, text="Insert the name of a teacher and click 'save' for each teacher of the school.",font=("Calibri",15),justify="left")
	la1.pack()
	fr1.place(x=50,y=143)
	fr2=Frame()
	la2 = Label( fr2,text="Teacher name:",font=("Calibri",15),justify="left")
	la2.pack(side=LEFT)	
	en1 =Entry( fr2,textvariable=v1,font=("Calibri",15),justify="left",width=12)
	en1.pack(side=LEFT)
	la3 = Label( fr2, text="Father name:",font=("Calibri",15),justify="left")
	la3.pack(side=LEFT)	
	en2 = Entry( fr2, textvariable=v2,font=("Calibri",15),justify="left",width=12)
	en2.pack(side=LEFT)
	la4 = Label( fr2, text="Grand father name:",font=("Calibri",15),justify="left")
	la4.pack(side=LEFT)	
	en3 = Entry( fr2,textvariable=v3,font=("Calibri",15),justify="left",width=12)
	en3.pack(side=LEFT)
	R1 = Radiobutton(fr2, text="Male", variable=d8, value=1,font=("Calibri",15))
	R1.pack(side=LEFT)
	R2 = Radiobutton(fr2, text="Female", variable=d8, value=2,font=("Calibri",15))
	R2.pack(side=LEFT)	
	bu1 =Button( fr2, text="Save",font=("Calibri",12),padx=5,pady=5,command=ent1,width=7)
	bu1.pack(side=LEFT)
	bu2 =Button( fr2, text="Next",font=("Calibri",12),padx=5,pady=5,command=sho,width=7)
	bu2.pack(side=LEFT)
	fr2.place(x=50,y=170)		
	s1=v1.get()
	s2=v2.get()
	s3=v3.get()
	en1.delete(0,END)
	en2.delete(0,END)
	en3.delete(0,END)
	s5=""		
	if m>0:		
		if s1.isalpha()==FALSE:
			if len(s1)>15:
				s1=s1[:14] + "..."
			s5="Teacher name:" + "'" + s1 + "'" + " is not name of a person.\n"
			m=3		
		if s2.isalpha()==FALSE:
			if len(s2)>15:
				s2=s2[:14] + "..."						
			s5=s5 + "Father name:" + "'" + s2 + "'" + " is not name of a person.\n"
			m=3			
		if s3.isalpha()==FALSE:
			if len(s3)>15:
				s3=s3[:14] + "..."						
			s5=s5 + "Grand father name:" + "'" + s3 + "'" + " is not name of a person.\n"
			m=3
	if m==3:
		messagebox.showinfo("Error", s5 + "	Try again.")		
	if m==2 and s0==True:		
		s1=s1.capitalize()
		s2=s2.capitalize()
		s3=s3.capitalize()
		s11=s1[:40]
		s21=s2[:40]
		s31=s3[:40]
		tna1.append(s1[:15])
		s4=s1 + " " + s2 + " " + s3
		s41=s11 + " " + s21 + " " + s31
		q1=d8.get()
		if q1==2:
			s4="Miss." + s4
			s41="Miss." + s41
		else:
			s4="Mr." + s4
			s41="Miss." + s41		
		tna.append(s4)
		tnad.append(s41)				
	m=2		
fr=Frame(Root)
fr5=Frame()
pla3=Label(text = "")
pla4=Label(text = "")
la1 = Label( fr, text="SCHOOL CLASS SCHEDULING SOFTWARE",foreground="blue", justify="center",font=("Elephant",25,"underline") ,pady=50)
la1.pack()
fr.pack()
fr.place(x=200,y=5)
bu1 =Button( fr5, text="Start",font=("Calibri",12),padx=5,pady=5,command=ent1,width=15)
bu1.pack(side=LEFT)
bu2 =Button( fr5, text="Cancel",font=("Calibri",12),padx=5,pady=5,command=Root.destroy,width=15)
bu2.pack(side=LEFT)
fr5.place(x=500,y=100)
Root.mainloop()



