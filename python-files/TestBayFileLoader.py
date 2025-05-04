import sys, os
import time
import xlrd
import win32com.client
from datetime import datetime
import sqlite3
excel = win32com.client.Dispatch('Excel.Application')
root = "G:/QC/"
path = os.path.join(root, "Test Reports")
SQL_TestBay='C://AQTS_Design//TestResults.db'

############################################################################################################
# Noload Current and Loss
def CHECK_CHECK(Check):
    if  Check==None:
        Check='None'
    try:
        No=float(Check)
        Check='None' 
    except:
       ok=1
    return Check 

def Add_Info(X,Info):
    Info.append(work_sheets.Cells(X+6,3).value) 
    Info.append(work_sheets.Cells(X+2,5).value)  
    Info.append(work_sheets.Cells(X+3,5).value) 
    Info.append(work_sheets.Cells(X+4,5).value) 
    Info.append(work_sheets.Cells(X+5,5).value) 
    Info.append(work_sheets.Cells(X+2,7).value)   
    Info.append(work_sheets.Cells(X+3,7).value)  
    Info.append(work_sheets.Cells(X+4,7).value) 
    Info.append(work_sheets.Cells(X+5,7).value) 
    Info.append(work_sheets.Cells(X+6,5).value)   
    done=1
    return done,Info

def NoLoadCurrentLoss(Info):
    done=0
    Check=work_sheets.Cells(22,2).value
    Check=CHECK_CHECK(Check)   
    A0='EXCITATION LOSS AND CURRENT TEST'
    A1='EXCITATION LOSS AND CURRENT TEST 100%'
    A2='EXCITATION'
    A3='Excitation'
    A4='EXCITATION LOSS AND CURRENT TEST @ 60 Hz'
    A5='EXCITATION LOSS AND CURRENT TEST (@ 50 Hz)'
    A6='*EXCITATION LOSS AND CURRENT TEST'
    
    if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check or A6 == Check:
        X=22
        done,Info=Add_Info(X,Info)
    if done==0:
        Check=work_sheets.Cells(23,2).value
        Check=CHECK_CHECK(Check)    
        if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check or A6 == Check:
             X=23
             done,Info=Add_Info(X,Info)
    if done==0:
        Check=work_sheets.Cells(26,2).value
        Check=CHECK_CHECK(Check)  
        if A0 == Check or A1 == Check or A2 == Check or  A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
            X=26
            done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(25,2).value
       Check=CHECK_CHECK(Check)
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
           X=25
           done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(29,2).value
       Check=CHECK_CHECK(Check) 
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=29
          done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(30,2).value
       Check=CHECK_CHECK(Check) 
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=30
          done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(31,2).value
       Check=CHECK_CHECK(Check)   
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check or A6 == Check:
          X=31
          done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(32,2).value
       Check=CHECK_CHECK(Check)    
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=32
          done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(33,2).value
       Check=CHECK_CHECK(Check)   
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=33
          done,Info=Add_Info(X,Info)
    if done==0:
        Check=work_sheets.Cells(34,2).value
        Check=CHECK_CHECK(Check)  
        if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
           X=34
           done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(36,2).value
       Check=CHECK_CHECK(Check)   
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=36
          done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(28,2).value
       Check=CHECK_CHECK(Check)   
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=28
          done,Info=Add_Info(X,Info)
    if done==0:
        Check=work_sheets.Cells(23,1).value
        Check=CHECK_CHECK(Check) 
        if A0 in Check or A1 in Check or A2 in Check or  A3 in Check or A4 in Check or A5 in Check  or A6 in Check:
           X=23
           done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(28,1).value
       Check=CHECK_CHECK(Check)
       if A0 in Check or A1 in Check or A2 in Check or  A3 in Check or A4 in Check or A5 in Check  or A6 in Check:
          X=28
          done,Info=Add_Info(X,Info)
    if done==0:
        Check=work_sheets.Cells(27,1).value
        Check=CHECK_CHECK(Check)   
        if A0 in Check or A1 in Check or A2 in Check or  A3 in Check or A4 in Check or A5 in Check  or A6 in Check:
           X=27
           done,Info=Add_Info(X,Info)
    if done==0:
        Check=work_sheets.Cells(30,1).value
        Check=CHECK_CHECK(Check) 
        if A0 in Check or A1 in Check or A2 in Check or  A3 in Check or A4 in Check or A5 in Check  or A6 in Check:
           X=30
           done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(27,2).value
       Check=CHECK_CHECK(Check)  
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=27
          done,Info=Add_Info(X,Info)
    if done==0:
       Check=work_sheets.Cells(42,2).value
       Check=CHECK_CHECK(Check) 
       if A0 == Check or A1 == Check or A2 == Check or A3 == Check or A4 == Check or A5 == Check  or A6 == Check:
          X=42
          done,Info=Add_Info(X,Info)
    if done==0:
       Info.append(0) 
       Info.append(0)  
       Info.append(0) 
       Info.append(0) 
       Info.append(0) 
       Info.append(0)   
       Info.append(0)  
       Info.append(0) 
       Info.append(0) 
       Info.append(0) 
       
   
    return Info
############################################################################################################
## Load Loss and Impedance

def LoadLossImpedance(Info):
    Check=work_sheets.Cells(28,10).value
    done=0
    if  Check==None:
        Check='None'
    if 'LOAD LOSS AND IMPEDANCE TEST' == Check:     
         Info.append(work_sheets.Cells(36,14).value) 
         Info.append(work_sheets.Cells(37,14).value) 
         Info.append(work_sheets.Cells(38,16).value) 
         Info.append(work_sheets.Cells(38,14).value) 
         Info.append(0) 
         Info.append(0) 
         Info.append(0) 
         done=1
    if done==0:
       Check=work_sheets.Cells(27,10).value
       if  Check==None:
           Check='None'
       if 'LOAD LOSS AND IMPEDANCE TEST' == Check:  
            if work_sheets.Cells(45,14).value!=None:
                Info.append(work_sheets.Cells(45,14).value) 
                Info.append(work_sheets.Cells(46,14).value) 
                Info.append(work_sheets.Cells(46,15).value) 
                Info.append(work_sheets.Cells(47,14).value) 
                Info.append(work_sheets.Cells(48,14).value) 
                Info.append(work_sheets.Cells(49,14).value) 
                Info.append(work_sheets.Cells(50,14).value) 
                done=1 
    if done==0:
       Check=work_sheets.Cells(27,10).value
       if  Check==None:
           Check='None'
       if 'LOAD LOSS AND IMPEDANCE TEST' == Check and work_sheets.Cells(34,14).value!="@ temp.":
             Info.append(work_sheets.Cells(38,15).value) 
             Info.append(work_sheets.Cells(39,15).value) 
             Info.append(work_sheets.Cells(40,16).value) 
             Info.append(work_sheets.Cells(40,15).value) 
             Info.append(0) 
             Info.append(0) 
             Info.append(0)
             done=1   
    
    if done==0:
       Check=work_sheets.Cells(27,10).value
       if  Check==None:
           Check='None'
       if 'LOAD LOSS AND IMPEDANCE TEST' == Check and work_sheets.Cells(34,14).value=="@ temp.": 
             Info.append(work_sheets.Cells(35,14).value) 
             Info.append(work_sheets.Cells(36,14).value) 
             Info.append(work_sheets.Cells(37,16).value) 
             Info.append(work_sheets.Cells(37,14).value) 
             Info.append(0) 
             Info.append(0) 
             Info.append(0)
             done=1   
    if done==0:
       Check=work_sheets.Cells(27,10).value
       if  Check==None:
           Check='None'
       if 'LOAD LOSS AND IMPEDANCE TEST' == Check and work_sheets.Cells(38,14).value!="@ temp.":
             Info.append(work_sheets.Cells(38,14).value) 
             Info.append(work_sheets.Cells(39,14).value) 
             Info.append(work_sheets.Cells(40,16).value) 
             Info.append(work_sheets.Cells(40,14).value) 
             Info.append(0) 
             Info.append(0) 
             Info.append(0)
             done=1   
    if done==0:
        Check=work_sheets.Cells(27,10).value
        if  Check==None:
            Check='None'
        if 'LOAD LOSS AND IMPEDANCE TEST' == Check and work_sheets.Cells(34,14).value!="@ temp.":
              Info.append(work_sheets.Cells(35,14).value) 
              Info.append(work_sheets.Cells(36,14).value) 
              Info.append(work_sheets.Cells(37,16).value) 
              Info.append(work_sheets.Cells(37,14).value) 
              Info.append(0) 
              Info.append(0) 
              Info.append(0)
              done=1           
    if done==0:
      Check=work_sheets.Cells(30,10).value
      if  Check==None:
          Check='None'
      if 'LOAD LOSS AND IMPEDANCE TEST' == Check: 
            Info.append(work_sheets.Cells(38,14).value) 
            Info.append(work_sheets.Cells(39,14).value) 
            Info.append(work_sheets.Cells(40,16).value) 
            Info.append(work_sheets.Cells(40,14).value) 
            Info.append(0) 
            Info.append(0) 
            Info.append(0)
            done=1   
    if done==0:
       Check=work_sheets.Cells(29,10).value
       if  Check==None:
           Check='None'
       if 'LOAD LOSS AND IMPEDANCE TEST' == Check: 
             Info.append(work_sheets.Cells(37,14).value) 
             Info.append(work_sheets.Cells(38,14).value) 
             Info.append(work_sheets.Cells(39,16).value) 
             Info.append(work_sheets.Cells(39,14).value) 
             Info.append(0) 
             Info.append(0) 
             Info.append(0)
             done=1           
    if done==0:
       Check=work_sheets.Cells(31,10).value
       if  Check==None:
           Check='None'
       if 'LOAD LOSS AND IMPEDANCE TEST' == Check: 
             Info.append(work_sheets.Cells(39,14).value) 
             Info.append(work_sheets.Cells(40,14).value) 
             Info.append(work_sheets.Cells(41,16).value) 
             Info.append(work_sheets.Cells(41,14).value) 
             Info.append(0) 
             Info.append(0) 
             Info.append(0)
             done=1   
             done=1   
    if done==0:
        Check=work_sheets.Cells(32,10).value
        if  Check==None:
            Check='None'
        if 'LOAD LOSS AND IMPEDANCE TEST' == Check: 
              Info.append(work_sheets.Cells(40,14).value) 
              Info.append(work_sheets.Cells(41,14).value) 
              Info.append(work_sheets.Cells(42,16).value) 
              Info.append(work_sheets.Cells(42,14).value) 
              Info.append(0) 
              Info.append(0) 
              Info.append(0)
              done=1            
    if done==0:
       Check=work_sheets.Cells(28,10).value
       if  Check==None:
           Check='None'
       if 'LOAD LOSS AND IMPEDANCE TEST' == Check: 
             Check=work_sheets.Cells(29,35).value
             if  Check==None:
                 Check='None'
             if '@ temp.' in Check: 
                 Info.append(work_sheets.Cells(30,35).value) 
                 Info.append(work_sheets.Cells(31,35).value) 
                 Info.append(work_sheets.Cells(32,37).value) 
                 Info.append(work_sheets.Cells(32,35).value) 
                 Info.append(0) 
                 Info.append(0) 
                 Info.append(0)
                 done=1            
    if done==0:
             Info.append(0) 
             Info.append(0) 
             Info.append(0)
             Info.append(0) 
             Info.append(0) 
             Info.append(0) 
             Info.append(0)
             done=1   
  
    return Info
############################################################################################################
def FileCheck1(File):
    conn = sqlite3.connect(SQL_TestBay)
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM TestBayFiles where File = """+  "'"+File+"'")
    FileCheck = cursor.fetchall()
    conn.commit()
    cursor.close()
    CHECK=len(FileCheck)
    return CHECK

       
        
def FileCheck(File):
    conn = sqlite3.connect(SQL_TestBay)
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM TestBayFiles where File = """+  "'"+File+"'")
    FileCheck = cursor.fetchall()
    conn.commit()
    cursor.close()
    CHECK=len(FileCheck)
    if CHECK!=0:
        conn = sqlite3.connect(SQL_TestBay)
        cursor=conn.cursor()
        cursor.execute("""SELECT * FROM TestBayDesignResult where File = """+  "'"+File+"'")
        FileCheck = cursor.fetchall()
        conn.commit()
        cursor.close()
        if len(FileCheck)!=0:
            if FileCheck[0][44]==8:
               conn = sqlite3.connect(SQL_TestBay)
               cursor=conn.cursor()
               cursor.execute("""Delete FROM TestBayFiles where File = """+  "'"+File+"'")
               cursor.execute("""Delete FROM TestBayDesignResult where File = """+  "'"+File+"'")
               conn.commit()
               cursor.close() 
               CHECK=0
    return CHECK

 
Counter0=0    
Counter1=0    
LastSynDate="2025:04:07"     

conn = sqlite3.connect(SQL_TestBay)
cursor=conn.cursor()
cursor.execute("""SELECT * FROM SynDate""")
Info = cursor.fetchall()
conn.commit()
cursor.close()
LastSynDate=Info[0][0]  

print(LastSynDate)
print(datetime.now().strftime("%Y:%m:%d"))
print(datetime.now())
D1=datetime.now()     
for path, subdirs, files in os.walk(path):
    if len(subdirs)!=0:
        F0=round(Counter0/len(subdirs)*100,3)
    if len(subdirs)==0:
        F0=0
    Counter0=Counter0+1
    Counter1=0 
    for file in files:
        if  datetime.fromtimestamp(os.path.getmtime(path+'/'+file)).strftime("%Y:%m:%d") >= datetime.now().strftime(LastSynDate):
            F1=round(Counter1/len(files)*100,3)
            print(path,file,F0,'--',F1,'%',' : ',datetime.fromtimestamp(os.path.getmtime(path+'/'+file)).strftime("%Y:%m:%d"))
            Counter1=Counter1+1
            if ".xls" not in file and ".xlsx" not in file and ".db" not in file and  '~$' not in file  and "Shortcut.lnk" not in file  and ".lnk" not in file: 
                CHECK=FileCheck1(file)
                if CHECK==0:    
                    dt = datetime.fromtimestamp(os.path.getmtime(path+'/'+file))
                    readable_time=dt.date()
                    conn = sqlite3.connect(SQL_TestBay)
                    cursor=conn.cursor()
                    cursor.execute("""INSERT INTO TestBayFiles VALUES(?,?,?,?)""",(
                                                      os.path.join(path),
                                                      file,
                                                      readable_time,
                                                      'N/D'))
                    conn.commit()
                    cursor.close
            if (".xls" in file or ".xlsx" in file) and "Shortcut.lnk" not in file :    
                DesignNo='N/D'
                CHECK=FileCheck(file)
                if CHECK==0 and  '~$' not in file and "Shortcut.lnk" not in file:
                    Info=[]
                    dt = datetime.fromtimestamp(os.path.getmtime(path+'/'+file))
                    readable_time=dt.date()
                    excel.AskToUpdateLinks = False
                    excel.DisplayAlerts = False
                    sheets = excel.Workbooks.open(path+'/'+file) 
                    NoClose=0
                    try:
                        work_sheets = sheets.Worksheets[0]
                        Check=work_sheets.Cells(7,1).value
                        #print('DSG',file,work_sheets.Cells(7,1).value)
                        if Check==None:
                            Check='None' 
                            DesignNo='N/D'
                            CHECK=FileCheck(file)
                    except AttributeError:
                        Check='None' 
                        DesignNo='N/D'
                        NoClose=1
                    if  ('MTC DN:' == Check or 'AQ DN:' == Check or 'AQTS DN:' == Check or 'MTC DN' == Check or 'AQ DN' == Check or 'AQTS DN' == Check):
                        DesignNo=work_sheets.Cells(7,3).value 
                        if  DesignNo==None:
                            DesignNo='N/D'
                        try:
                            float(DesignNo)
                            DesignNo='N/D'
                        except ValueError:
                            Number=False 
                        if DesignNo[:1]=='3' and  DesignNo!='N/D' :
                            Check=work_sheets.Cells(6,1).value
                            done=0
                            if  'MTC JN:' == Check or  'AQ JN:' == Check or 'AQTS JN:' == Check or 'MTC JN' == Check or  'AQ JN' == Check or 'AQTS JN' == Check:
                                Info.append(work_sheets.Cells(6,3).value) 
                                done=1
                            if done==0:
                                Info.append(0)  
                            done=0    
                            Check=work_sheets.Cells(8,1).value
                            if  'Customer:'== Check or 'CUSTOMER:'== Check or 'Customer'== Check or 'CUSTOMER'== Check:
                                Info.append(work_sheets.Cells(8,3).value) 
                                done=1
                            if done==0:
                                Info.append(0)  
                            done=0    
                            Check=work_sheets.Cells(9,1).value
                            if  'USER:' == Check or  'USER' == Check or 'User:' == Check or  'User' == Check:
                               Info.append(work_sheets.Cells(9,3).value) 
                               done=1
                            if done==0:
                                Info.append(0)  
                            done=0    
                            Check=work_sheets.Cells(10,1).value
                            if  'Cust. PO:' == Check or 'Cust. PO' == Check:
                              Info.append(work_sheets.Cells(10,3).value) 
                              done=1
                            if done==0:
                                Info.append(0)  
                            done=0    
                            Check=work_sheets.Cells(6,7).value
                            if  'kVA' == Check or 'KVA' == Check:
                                Info.append(work_sheets.Cells(6,8).value)
                                done=1
                            if done==0:
                                Info.append(0)  
                            done=0    
                            Check=work_sheets.Cells(7,7).value
                            if  'Frequency' == Check:
                                Info.append(work_sheets.Cells(7,8).value)
                                done=1
                            if done==0:
                                Info.append(0)  
                            done=0    
                            Check=work_sheets.Cells(8,7).value
                            if  'Temp Rise' == Check:
                                Info.append(work_sheets.Cells(8,8).value)
                                done=1
                            if done==0:
                                Info.append(0)  
                            done=0    
                            Check=work_sheets.Cells(9,7).value
                            if  'Wndg Mat' == Check:
                                Info.append(work_sheets.Cells(9,8).value)  
                                done=1
                            if done==0:
                                Info.append(0)  
                            Check=work_sheets.Cells(5,11).value
                            ### 6 Pulse
                            if  Check==None: 
                                Check=work_sheets.Cells(6,11).value
                                done=0
                                if  'Primary Volts' == Check or 'HV Volts' == Check:
                                     Info.append(work_sheets.Cells(6,12).value)  
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0    
                                Check=work_sheets.Cells(7,11).value
                                if  'Connection' ==  Check:
                                     Info.append(work_sheets.Cells(7,12).value) 
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0      
                                Check=work_sheets.Cells(8,11).value
                                if  'kVBil' == Check or  'KVBil' == Check:
                                     Info.append(work_sheets.Cells(8,12).value)  
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0      
                                Check=work_sheets.Cells(9,11).value
                                if  'Amps' == Check:
                                     Info.append(work_sheets.Cells(9,12).value)
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0      
                                Check=work_sheets.Cells(6,15).value
                                if  'Secondary Volts' == Check or 'LV Volts' == Check:
                                     Info.append(work_sheets.Cells(6,16).value)   
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0      
                                Check=work_sheets.Cells(7,15).value
                                if  'Connection' == Check:
                                     Info.append(work_sheets.Cells(7,16).value) 
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0      
                                Check=work_sheets.Cells(8,15).value
                                if  'kVBil' == Check or 'KVBil' == Check:
                                     Info.append(work_sheets.Cells(8,16).value) 
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0      
                                Check=work_sheets.Cells(9,15).value
                                if  'Amps' == Check:
                                     Info.append(work_sheets.Cells(9,16).value) 
                                     done=1
                                if done==0:
                                    Info.append(0)  
                                done=0 
                                Info.append(0)   
                                Info.append('N/D')    
                                Info.append(0)    
                                Info.append(0) 
                                Info=NoLoadCurrentLoss(Info)
                                Info=LoadLossImpedance(Info)
                                Check=work_sheets.Cells(46,2).value
                                done=0
                                if Check==None:
                                   Check='None' 
                                if  'MEASURED TEMPERATURE RISE' == Check:     
                                     Info.append(work_sheets.Cells(48,3).value)
                                     Info.append(work_sheets.Cells(49,3).value)
                                     Info.append(0)     
                                     done=1
                                if done==0:
                                   Check=work_sheets.Cells(62,2).value
                                   if Check==None:
                                      Check='None' 
                                   if  'MEASURED TEMPERATURE RISE' == Check:     
                                        Info.append(work_sheets.Cells(64,3).value)
                                        Info.append(work_sheets.Cells(65,3).value)
                                        Info.append(work_sheets.Cells(66,3).value)
                                        done=1     
                                if  done==0:     
                                     Info.append(0) 
                                     Info.append(0)     
                                     Info.append(0)     
                            conn = sqlite3.connect(SQL_TestBay)
                            cursor=conn.cursor()
                            cursor.execute("""INSERT INTO TestBayDesignResult VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                                                              DesignNo,
                                                              os.path.join(path),
                                                              file,
                                                              readable_time,
                                                              Info[0],
                                                              Info[1],
                                                              Info[2],
                                                              Info[3],
                                                              Info[4],
                                                              Info[5],
                                                              Info[6],
                                                              Info[7],
                                                              Info[8],
                                                              Info[9],
                                                              Info[10],
                                                              Info[11],
                                                              Info[12],
                                                              Info[13],
                                                              Info[14],
                                                              Info[15],
                                                              Info[16],
                                                              Info[17],
                                                              Info[18],
                                                              Info[19],
                                                              Info[20],
                                                              Info[21],
                                                              Info[22],
                                                              Info[23],
                                                              Info[24],
                                                              Info[25],
                                                              Info[26],
                                                              Info[27],
                                                              Info[28],
                                                              Info[29],
                                                              Info[30],
                                                              Info[31],
                                                              Info[32],
                                                              Info[33],
                                                              Info[34],
                                                              Info[35],
                                                              Info[36],
                                                              Info[37],
                                                              Info[38],
                                                              Info[39],
                                                              '0'
                                                              ))
                                                              
                            conn.commit()
                            cursor.close
                            print(os.path.join(path, file),readable_time,DesignNo,Info,len(Info))
                    if NoClose==0:        
                        sheets.Close(True)
                    conn = sqlite3.connect(SQL_TestBay)
                    cursor=conn.cursor()
                    cursor.execute("""INSERT INTO TestBayFiles VALUES(?,?,?,?)""",(
                                                      os.path.join(path),
                                                      file,
                                                      readable_time,
                                                      DesignNo))
                                                      
                    conn.commit()
                    cursor.close
             
conn = sqlite3.connect(SQL_TestBay)
cursor=conn.cursor()
cursor.execute("""Delete FROM SynDate""")
conn.commit()
cursor.close()
Datum=datetime.now().strftime("%Y:%m:%d")
conn = sqlite3.connect(SQL_TestBay)
cursor=conn.cursor()
cursor.execute("""INSERT INTO SynDate VALUES(?)""",(Datum,))
conn.commit()
cursor.close() 
print(D1)
print(datetime.now())

