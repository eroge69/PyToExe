# -*- coding: utf-8 -*-

import numpy as np
from numpy.linalg import inv, lstsq
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tkinter import *
from tkinter import filedialog 
from tkinter import messagebox as msg
import datetime
from scipy.linalg import solve

#Нужны для формирования таблиц в программе (на данный момент не обязательно)
from pandastable import Table 
from tkintertable import TableCanvas 

#Визуализация результатов
def visual(ABS, B, m_cal):
	
	#Отобразить абсолютное отклонение
	figure, axis=plt.subplots(3)

	axis[0].set_title('Абсолютное отклонение OX')
	axis[0].scatter(B[::,0], ABS[::,0])
	axis[0].grid(b=True)
	
	axis[1].set_title('Абсолютное отклонение OY')
	axis[1].scatter(B[::,1], ABS[::,1])
	axis[1].grid(b=True)
	
	axis[2].set_title('Абсолютное отклонение OZ')
	axis[2].scatter(B[::,2], ABS[::,2])
	axis[2].grid(b=True)
	
	#Точки измерений
	Bb=np.array([-60000,0,60000])
	xgrid, ygrid=np.meshgrid(Bb,Bb)
	
	plt.figure()
	ax=plt.axes(projection='3d')
	ax.set_title('Точки измерений')
	ax.set_xlabel('OX')
	ax.set_ylabel('OY')
	ax.set_zlabel('OZ')
	ax.scatter(B[::,0],B[::,1],B[::,2], c='red', s=1.4)
	ax.scatter(m_cal[::,0],m_cal[::,1],m_cal[::,2], c='green', s=0.2)
	ax.plot_wireframe(xgrid, ygrid, xgrid*0)
	ax.plot_wireframe(xgrid, ygrid, xgrid*0+60000)
	ax.plot_wireframe(xgrid, ygrid, xgrid*0-60000)
	ax.plot_wireframe(xgrid*0+60000, xgrid, ygrid)
	ax.plot_wireframe(xgrid*0-60000, xgrid, ygrid)
	ax.plot_wireframe(xgrid, xgrid*0+60000, ygrid)
	ax.plot_wireframe(xgrid, xgrid*0-60000, ygrid)
	
	plt.show()

def temp_deviat (dataT):
	#Отобразить изменения показаний МЦ от температуры
	figure, axis=plt.subplots(3)

	axis[0].set_title('Изменение OX от Т')
	axis[0].scatter(np.array(dataT.loc[::,8]), np.array(dataT.loc[::,5]))
	axis[0].grid(b=True)
	
	axis[1].set_title('Изменение OY от Т')
	axis[1].scatter(np.array(dataT.loc[::,8]), np.array(dataT.loc[::,6]))
	axis[1].grid(b=True)
	
	axis[2].set_title('Изменение OZ от Т')
	axis[2].scatter(np.array(dataT.loc[::,8]), np.array(dataT.loc[::,7]))
	axis[2].grid(b=True)
	plt.show()


#Работа с графикой

class Calibration: 

	def __init__(self, root): 

		self.root = root 
		self.file_name = '' 
		self.f = Frame(self.root, 
					height = 200, 
					width = 300) 
		
		# Place the frame on root window 
		self.f.pack() 
		
		# Creating label widgets 
		self.message_label = Label(self.f, 
								text = 'Калибровка магнитометра', 
								font = ('Arial', 19,'underline'), 
								fg = 'Black') 
		self.message_label2 = Label(self.f, 
									text = 'Выбор операции', 
									font = ('Arial', 14,'underline'), 
									fg = 'Red') 

		# Buttons 
		self.file_to_calibration_button = Button(self.f, 
									text = 'Калибровка с температурами', 
									font = ('Arial', 14), 
									bg = 'Orange', 
									fg = 'Black', 
									command = self.file_to_calibration) 
		self.adjust_termcam_button = Button(self.f, 
 									text = 'Определить смещение в камере', 
 									font = ('Arial', 14), 
 									bg = 'Orange', 
 									fg = 'Black', 
 									command = self.adjust_termcam) 
		self.display_button = Button(self.f, 
									text = 'Отобразить результаты', 
									font = ('Arial', 14), 
									bg = 'Green', 
									fg = 'Black', 
									command = self.display_result) 
		self.exit_button = Button(self.f, 
								text = 'Выход',
								font = ('Arial', 14), 
								bg = 'Red', 
								fg = 'Black', 
								command = root.destroy) 
		self.Without_Temp_button = Button(self.f, 
									text = 'Калибровка без температур', 
									font = ('Arial', 14), 
									bg = 'Orange', 
									fg = 'Black', 
									command = self.Without_Temp) 


		# Placing the widgets using grid manager 
		self.message_label.grid(row = 1, column = 1) 
		self.message_label2.grid(row = 2, column = 1) 
		self.file_to_calibration_button.grid(row = 4, column = 0, 
								padx = 0, pady = 15)
		self.adjust_termcam_button.grid(row = 3, column = 0, 
								padx = 0, pady = 15) 
		self.display_button.grid(row = 3, column = 1, 
								padx = 10, pady = 15) 
		self.exit_button.grid(row = 3, column = 2, 
							padx = 10, pady = 15) 
		self.Without_Temp_button.grid(row = 5, column = 0, 
						padx = 10, pady = 15) 

	def adjust_termcam(self):
		try: 
			self.file_name = filedialog.askopenfilename(initialdir = '/Desktop', 
														title = 'Выберите файл txt', 
														filetypes = (('txt file','*.txt'), 
																	('txt file','*.txt'))) 
			data = pd.read_table(self.file_name, sep = ';', header = None, skiprows=2,encoding='ISO-8859-1').loc[::,0:8]
			data[[0,10]]=data[0].str.split(' ', expand=True)[[0,1]]
			
			#Фильтрация значений убираем значения 0 и пустые ячейки
			index_filter=(data[8].astype(str).str.strip()=='')|(data[8].astype(str).str.strip()=='0')
			data=data.drop(index=index_filter[index_filter==True].index)
			
			#Преобразование строчных значений полей  в числа с плавающей точкой
			data.loc[::,1:8]=data.loc[::,1:8].replace(',','.',regex=True).astype(float)
			
			#Осреднение каждого из участков и разделение по положениям
			attitude={}
			for i in np.arange(1,7):
				attitude.update({i:np.array(data.loc[data[data[8]==i].index][[2,3,4,5,6,7]].mean())})
			
			#Определяю разницу между показаниями
			det={}
			for i in np.arange(1,7):
				det.update({i:(attitude[i][3:6]-attitude[i][0:3])})
				#Запись при помощи pandas
				result_termocam=pd.DataFrame(det, index=['OX','OY','OZ']).transpose()
			
			result_termocam.to_excel('Коэффициенты смещения в термокамере.xlsx', index=False)

#Вариант записи даты и вермени:
#str(datetime.datetime.now().replace(microsecond=0))

		except FileNotFoundError as e: 
				msg.showerror('Ошибка при работе с файлом', e) 


	def file_to_calibration(self): 
		try: 
			self.file_name = filedialog.askopenfilename(initialdir = '/Desktop', 
														title = 'Выберите файл txt (данные при НУ)', 
														filetypes = (('txt file','*.txt'), 
																	('txt file','*.txt'))) 
			#Чтение файла для калибровки при нормальных условиях
			data = pd.read_table(self.file_name, sep = ';', header = None, skiprows=2,encoding='ISO-8859-1').loc[::,0:9]
			data[[0,10]]=data[0].str.split(' ', expand=True)[[0,1]]
			 
			#Фильтрация значений (оставляем только строки, с обновлёнными данными от 17М23 и 540КА.3100)
			data=data.drop_duplicates(9).drop(index=0)
			 
			#Преобразование строчных значений полей и температуры в числа с плавающей точкой
			data.loc[::,1:8]=data.loc[::,1:8].replace(',','.',regex=True).astype(float)
			
			#Убрать строки, в которых не готовы температурные данные с МЦ (температура=-300)
			index_filter=data[8]==-300.0
			data=data.drop(index_filter[index_filter==True].index)
			
			#Данные 540КА.3100-0
			R=np.array(data.loc[::,5:7])
			#Данные 17М23 (перевод в нТл)
			B=np.array(data.loc[::,2:4])*8333
			#Проекция показаний 17М23 на оси МЦ
			B[::,1],B[::,2]=B[::,1]*(-1), B[::,2]*(-1)
			#Температура с датчика
			T=np.array(data.loc[::,8])
			
			try: 
				#Чтение данных по температуре
				self.file_name = filedialog.askopenfilename(initialdir = '/Desktop', 
															title = 'Выберите файл txt (данные при температурах)', 
															filetypes = (('txt file','*.txt'), 
																		('txt file','*.txt'))) 
				#Чтение данных по температуре
				dataT = pd.read_table(self.file_name, sep = ';', header = None, skiprows=2,encoding='ISO-8859-1').loc[::,0:10]
				dataT[[0,11]]=dataT[0].str.split(' ', expand=True)[[0,1]]
				#Убираю "дубликаты" измерений МЦ
				dataT=dataT.drop_duplicates(9).drop(index=0)
				#Убираю пустые строки и участки с поворотом подставки магнитометров
				index_filter=(dataT[10].astype(str).str.strip()=='')|(dataT[10].astype(str).str.strip()=='0')
				dataT=dataT.drop(index=index_filter[index_filter==True].index)
				#Перевод в числа с плавающей точкой
				dataT.loc[::,1:10]=dataT.loc[::,1:10].replace(',','.',regex=True).astype(float)
			
			except FileNotFoundError as e: 
				msg.showerror('Ошибка при работе с файлом', e) 
			try:
				#Читаю коэффициенты смещения
				result_termocam=pd.read_excel(Path("Коэффициенты смещения в термокамере.xlsx"))
			except FileNotFoundError as e: 
				msg.showerror('Отсутствует файл коэффициентов смещения в термокамере', e) 
			
			#Заполняется массив данных с учётом смещения в камере (Корректировка показаний эталона)
			B_temp=np.empty(shape=(0,3))
			for i in result_termocam.index:
				index_to_det=(dataT[10]==result_termocam.index[i]+1)
				a=dataT.loc[index_to_det[index_to_det==True].index,::]
				B_temp=np.concatenate((B_temp,np.array(a.loc[::,2:4])+np.array(result_termocam)[i]), axis=0)
			
			#Зависимость показаний от температуры в климатической камере
			temp_deviat (dataT)
			
			#Оси МЦ и 17М23 совпадают, поэтому проэцировать ничего никуда не нужно
			#"Сшиваем" оба массива данных (при НУ и температуре с учётом смещения эталонных показаний)
			B=np.concatenate((B,B_temp*8333), axis=0)
			R=np.concatenate((R,np.array(dataT.loc[::,5:7])), axis=0)
			T=np.concatenate((T,np.array(dataT.loc[::,8])), axis=0)

			A=np.sum(B, axis=0)
			C=np.sum([T[i]*B[i] for i in np.arange(np.shape(T)[0])], axis=0)
			G=np.sum([T[i]*R[i] for i in np.arange(np.shape(T)[0])], axis=0)
			H=np.sum(R, axis=0)
			L=np.sum([(T[i]**2)*R[i] for i in np.arange(np.shape(T)[0])], axis=0)

			M=np.array([])
			for l in np.arange(np.shape(R)[0]):
			    for i in np.arange(3):
			        for k in np.arange(3):
			            M=np.concatenate((M, [R[l][i]*R[l][k]]), axis=0)
			M=np.sum(np.reshape(M, (int(np.shape(M)[0]/9),3,3)), axis=0)

			P=np.array([])
			for l in np.arange(np.shape(R)[0]):
			    for i in np.arange(3):
			        for k in np.arange(3):
			            P=np.concatenate((P, [T[l]*R[l][i]*R[l][k]]), axis=0)
			P=np.sum(np.reshape(P, (int(np.shape(P)[0]/9),3,3)), axis=0)

			Q=np.array([])
			for l in np.arange(np.shape(R)[0]):
			    for i in np.arange(3):
			        for k in np.arange(3):
			            Q=np.concatenate((Q, [(T[l]**2)*R[l][i]*R[l][k]]), axis=0)
			Q=np.sum(np.reshape(Q, (int(np.shape(Q)[0]/9),3,3)), axis=0)

			Dd=np.array([])
			for l in np.arange(np.shape(R)[0]):
			    for i in np.arange(3):
			        for j in np.arange(3):
			            Dd=np.concatenate((Dd, [B[l][i]*R[l][j]]), axis=0)
			Dd=np.sum(np.reshape(Dd, (int(np.shape(Dd)[0]/9),3,3)), axis=0)

			F=np.array([])
			for l in np.arange(np.shape(R)[0]):
			    for i in np.arange(3):
			        for j in np.arange(3):
			            F=np.concatenate((F, [T[l]*B[l][i]*R[l][j]]), axis=0)
			F=np.sum(np.reshape(F, (int(np.shape(F)[0]/9),3,3)), axis=0)

			Rr=np.sum([T[i]**2 for i in np.arange(np.shape(T)[0])], axis=0)
			Tt=np.sum([T[i] for i in np.arange(np.shape(T)[0])], axis=0)
			N=np.shape(T)[0]

			AA1=np.reshape(np.array([
				[N,Tt,H[0],H[1],H[2],G[0],G[1],G[2]],
				[Tt,Rr,G[0],G[1],G[2],L[0],L[1],L[2]],
				
				[H[0],G[0],M[0][0],M[0][1],M[0][2],P[0][0],P[0][1],P[0][2]],
				[H[1],G[1],M[1][0],M[1][1],M[1][2],P[1][0],P[1][1],P[1][2]],
				[H[2],G[2],M[2][0],M[2][1],M[2][2],P[2][0],P[2][1],P[2][2]],
				
				[G[0],L[0],P[0][0],P[0][1],P[0][2],Q[0][0],Q[0][1],Q[0][2]],
				[G[1],L[1],P[1][0],P[1][1],P[1][2],Q[1][0],Q[1][1],Q[1][2]],
				[G[2],L[2],P[2][0],P[2][1],P[2][2],Q[2][0],Q[2][1],Q[2][2]],
				]), (8,8))

			AA2=np.reshape(np.array([
				[N,Tt,H[0],H[1],H[2],G[0],G[1],G[2]],
				[Tt,Rr,G[0],G[1],G[2],L[0],L[1],L[2]],
				
				[H[0],G[0],M[0][0],M[0][1],M[0][2],P[0][0],P[0][1],P[0][2]],
				[H[1],G[1],M[1][0],M[1][1],M[1][2],P[1][0],P[1][1],P[1][2]],
				[H[2],G[2],M[2][0],M[2][1],M[2][2],P[2][0],P[2][1],P[2][2]],
				
				[G[0],L[0],P[0][0],P[0][1],P[0][2],Q[0][0],Q[0][1],Q[0][2]],
				[G[1],L[1],P[1][0],P[1][1],P[1][2],Q[1][0],Q[1][1],Q[1][2]],
				[G[2],L[2],P[2][0],P[2][1],P[2][2],Q[2][0],Q[2][1],Q[2][2]],
				]), (8,8))

			AA3=np.reshape(np.array([
				[N,Tt,H[0],H[1],H[2],G[0],G[1],G[2]],
				[Tt,Rr,G[0],G[1],G[2],L[0],L[1],L[2]],
				
				[H[0],G[0],M[0][0],M[0][1],M[0][2],P[0][0],P[0][1],P[0][2]],
				[H[1],G[1],M[1][0],M[1][1],M[1][2],P[1][0],P[1][1],P[1][2]],
				[H[2],G[2],M[2][0],M[2][1],M[2][2],P[2][0],P[2][1],P[2][2]],
				
				[G[0],L[0],P[0][0],P[0][1],P[0][2],Q[0][0],Q[0][1],Q[0][2]],
				[G[1],L[1],P[1][0],P[1][1],P[1][2],Q[1][0],Q[1][1],Q[1][2]],
				[G[2],L[2],P[2][0],P[2][1],P[2][2],Q[2][0],Q[2][1],Q[2][2]],
				]), (8,8))

			Bb1=np.reshape(np.array([
				A[0],
				C[0],
				Dd[0][0], Dd[0][1], Dd[0][2],
				F[0][0], F[0][1], F[0][2]
				]),(8,1))

			Bb2=np.reshape(np.array([
				A[1],
				C[1],
				Dd[1][0], Dd[1][1], Dd[1][2],
				F[1][0], F[1][1], F[1][2]
				]),(8,1))

			Bb3=np.reshape(np.array([
				A[2],
				C[2],
				Dd[2][0], Dd[2][1], Dd[2][2],
				F[2][0], F[2][1], F[2][2]
				]),(8,1))

# 			result1=np.linalg.lstsq(AA1, Bb1, rcond=None)
# 			result2=np.linalg.lstsq(AA2, Bb2, rcond=None)
# 			result3=np.linalg.lstsq(AA3, Bb3, rcond=None)
# 			result=np.concatenate((result1[0], result2[0], result3[0]), axis=1)

			result1=solve(AA1, Bb1)
			result2=solve(AA2, Bb2)
			result3=solve(AA3, Bb3)
			result=np.concatenate((result1, result2, result3), axis=1)


			#Матрица перехода
			S = result[2:5].T
			#Матирица из трёх одинаковых dw по вертикали 
			Ks=result[5::].T
			Ks=np.eye(3)*np.diag(Ks) 
			b=result[0]
			kb=result[1]

			#Откалиброванные показания
			m_cal=np.array([(S+T[i]*Ks)@R[i]+b+kb*T[i] for i in np.arange(np.shape(T)[0])])

			#СКО от показаний эталона
			STD=np.sqrt(np.sum((m_cal-B)**2, axis=0)/np.shape(m_cal)[0])
			
			#Абсолютное отклонение
			ABS=m_cal-B
			
			#Поиск точек с ABS более 500 нТл
# 			indx=pd.DataFrame(ABS>500)
# 			indx_list=indx[(indx[0]==True)|(indx[1]==True)|(indx[2]==True)].index
			
			#Визуализация результатов
			visual(ABS, B, m_cal)
			
			
			result_to_excel=pd.concat([pd.DataFrame(S, columns=['Sx','Sy','Sz']),
							  pd.DataFrame(Ks, columns=['Ksx','Ksy','Ksz']), pd.DataFrame(b, columns=['b']),
							  pd.DataFrame(kb, columns=['kb']), pd.DataFrame(STD, columns=['СКО, нТл']),
							  pd.DataFrame(np.max(abs(ABS), axis=0), columns=['Макс. абс. откл, нТл']), pd.DataFrame(np.min(abs(ABS), axis=0), columns=['Мин. абс. откл, нТл'])],axis=1)
			result_to_excel.to_excel(str(datetime.date.today())+' Результат калибровки (каф.мат.).xlsx', index=False)
			

		except FileNotFoundError as e: 
				msg.showerror('Ошибка при работе с файлом', e) 

	def Without_Temp(self): 
		try: 
			self.file_name = filedialog.askopenfilename(initialdir = '/Desktop', 
														title = 'Выберите файл txt (данные при НУ)', 
														filetypes = (('txt file','*.txt'), 
																	('txt file','*.txt'))) 
			#Чтение файла для калибровки при нормальных условиях
			data = pd.read_table(self.file_name, sep = ';', header = None, skiprows=2,encoding='ISO-8859-1').loc[::,0:9]
			data[[0,10]]=data[0].str.split(' ', expand=True)[[0,1]]
			 
			#Фильтрация значений (оставляем только строки, с обновлёнными данными от 17М23 и 540КА.3100)
			data=data.drop_duplicates(9).drop(index=0)
			 
			#Преобразование строчных значений полей и температуры в числа с плавающей точкой
			data.loc[::,1:8]=data.loc[::,1:8].replace(',','.',regex=True).astype(float)
			
			#Убрать строки, в которых не готовы температурные данные с МЦ (температура=-300)
			index_filter=data[8]==-300.0
			data=data.drop(index_filter[index_filter==True].index)
			
			#Данные 540КА.3100-0
			R=np.array(data.loc[::,5:7])
			#Данные 17М23 (перевод в нТл)
			B=np.array(data.loc[::,2:4])*8333
			#Проекция показаний 17М23 на оси МЦ
			B[::,1],B[::,2]=B[::,1]*(-1), B[::,2]*(-1)
			#Температура с датчика
			T=np.array(data.loc[::,8])

			#Приводим вектор B к форме: [bx, by, bz, 1]
			B1=np.array([np.append(b, 1) for b in B])
			
			#Без температурных параметров
			x, residuals, rank, s=np.linalg.lstsq(B1.astype(float), R.astype(float), rcond=None)
			#Матрица перехода
			Mnu=inv(x[:3].T)
			#Смещение нуля
			Znu=x[3]
			#Расчёт показаний калибруемого магнитометра
			m_calnu = np.array([Mnu@(r-Znu) for r in R])
			
			#СКО от показаний эталона
			STD=np.sqrt(np.sum((m_calnu-B)**2, axis=0)/np.shape(m_calnu)[0])
			
			#Абсолютное отклонение
			ABS=m_calnu-B
			
			#Визуализация результатов
			visual(ABS, B, m_calnu)
			
			
			result_to_excel=pd.concat([pd.DataFrame(Mnu, columns=['Mx','My','Mz']), pd.DataFrame(Znu, columns=['Z']), pd.DataFrame(STD, columns=['СКО, нТл']), pd.DataFrame(np.max(abs(ABS), axis=0), columns=['Макс. абс. откл, нТл']), pd.DataFrame(np.min(abs(ABS), axis=0), columns=['Мин. абс. откл, нТл']),],axis=1)
			result_to_excel.to_excel(str(datetime.date.today())+' Результат калибровки без учёта температур.xlsx', index=False)
			

		except FileNotFoundError as e: 
				msg.showerror('Ошибка при работе с файлом', e) 

	def display_result(self): 
		try: 
			self.file_name = filedialog.askopenfilename(initialdir = '/Desktop', 
														title = 'Выбрать excel файл', 
														filetypes = (('excel файл','*.xlsx'), 
																	('excel файл','*.xlsx'))) 
			df = pd.read_excel(self.file_name) 
			
			if (len(df)== 0): 
				msg.showinfo('No records', 'No records') 
			else: 
				pass
				
			# Now display the DF in 'Table' object 
			# under'pandastable' module 
			self.f2 = Frame(self.root, height=200, width=300) 
			self.f2.pack(fill=BOTH,expand=1) 
			self.table = Table(self.f2, dataframe=df,read_only=True) 
			self.table.show() 
		
		except FileNotFoundError as e: 
			print(e) 
			msg.showerror('Ошибка при работе с файлом',e) 


# Driver Code 
root = Tk() 
root.title('GFG---Convert CSV to Excel File') 

obj = Calibration(root) 
root.geometry('800x600') 
root.mainloop() 
