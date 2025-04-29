#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests


# In[2]:


dfDATA = pd.read_excel (r'PartToCompare.xlsx')
print (dfDATA)

listOfPart=dfDATA[dfDATA.columns[1]].values.tolist()
listOfPartToCompare=[]
k=1
for i in listOfPart:   
    for j in listOfPart[k:]:
        listTemp=[i,j]
        listOfPartToCompare.append(listTemp)
    k+=1
print(listOfPartToCompare)


# In[3]:


def dfFromURL(partNumber):
    #TO MUCH INFOurl="http://hou1web.net.fmcti.com/cgi-bin/search/part_bom.cgi?part="+partNumber+"&status=released&%22indent=plus&sorder=part:rev:pstatus:desc:family_members:model:modelr:qm:sections:qspecs:especs:weld:documents:quantity:weight%22"

    url="http://hou1web.net.fmcti.com/cgi-bin/search/part_bom.cgi?part="+partNumber+"&status=released&%22indent=plus&sorder=level:part:desc:model:modelr:qm:sections:qspecs:especs:quantity%22"
    kings = requests.get(url)
    df = pd.read_html(kings.text.replace('<br>',' '), index_col=False)[0]
    headers = df.iloc[0]
    df  = pd.DataFrame(df.values[1:], columns=headers)
    df['Part'] = df['Part'].map(lambda x: x.lstrip('+ ').rstrip(' '))
    return df


def stackIBOMtoDf(i):
    df0=dfFromURL(i[0])
    df1=dfFromURL(i[1])

    df0 = df0.add_suffix('_0')
    df1 = df1.add_suffix('_1')
    return [df0,df1]   

def stackIBOMtoDfList(listOfParts):
    listDf=[]
    j=0
    for i in listOfParts:
        listDf.append((dfFromURL(i).add_suffix('_'+str(j))))
        #print(listDf[j])
        j+=1

    return listDf 

def generateArrangedDF(listOfParts):
    listDFnonTemp=stackIBOMtoDfList(listOfParts)
    #print(len(listDFnonTemp)-1)
    for i in range(len(listDFnonTemp)-1):
        

        
        listDF=listDFnonTemp
                
        # concat first main - part numbers
        fl1_df=listDF[i][:1]
        fl2_df=listDF[i+1][:1]
        firstline_df=pd.concat([fl1_df.iloc[:, 0], fl2_df.iloc[:, 0]],axis=1)
        
        for j in range(1,len(listDF[i].columns)):
            firstline_df=pd.concat([firstline_df, fl1_df.iloc[:1].iloc[:, j]],axis=1)
            firstline_df=pd.concat([firstline_df, fl2_df.iloc[:1].iloc[:, j]],axis=1)
        #print(firstline_df)
        #firstline_df=firstline_df[:0]
        #print(firstline_df)
        listDF[i]=listDF[i].iloc[1: , :]
        listDF[i+1]=listDF[i+1].iloc[1: , :]
        
        #stack this same part numbers
        dfP=listDF[i][listDF[i]['Part_'+str(i)].isin(listDF[i+1]['Part_'+str(i+1)])]
        dfP=dfP.sort_values(by=['Part_'+str(i)]).reset_index(drop=True)
        
        dfPnext=listDF[i+1][listDF[i+1]['Part_'+str(i+1)].isin(listDF[i]['Part_'+str(i)])]
        dfPnext=dfPnext.sort_values(by=['Part_'+str(i+1)]).reset_index(drop=True)
        
        #drop this same row
        #listDF[i+1]=listDF[i+1][~listDF[i+1]['Part_'+str(i+1)].isin(dfPnext['Part_'+str(i+1)])]
        #listDF[i]=listDF[i][~listDF[i]['Part_'+str(i)].isin(dfP['Part_'+str(i)])]
        
        #stack this same model numbers
        dfM=listDF[i][listDF[i]['Model_'+str(i)].isin(listDF[i+1]['Model_'+str(i+1)])]
        dfM=dfM[dfM['Model_'+str(i)] != 'NO-DWG'].sort_values(by=['Model_'+str(i)]).reset_index(drop=True)
        
        dfMnext=listDF[i+1][listDF[i+1]['Model_'+str(i+1)].isin(listDF[i]['Model_'+str(i)])]
        dfMnext=dfMnext[dfMnext['Model_'+str(i+1)] != 'NO-DWG'].sort_values(by=['Model_'+str(i+1)]).reset_index(drop=True)
        
        #drop this same row
        #istDF[i+1]=listDF[i+1][~listDF[i+1]['Model_'+str(i+1)].isin(dfMnext['Model_'+str(i+1)])]
        #listDF[i]=listDF[i][~listDF[i]['Model_'+str(i)].isin(dfM['Model_'+str(i)])]
        
        #print(listDF)

        # concat part numbers
        part_df=pd.concat([dfP.iloc[:, 0], dfPnext.iloc[:, 0]],axis=1)
        for j in range(1,len(dfP.columns)):
            part_df=pd.concat([part_df, dfP.iloc[:, j]],axis=1)
            part_df=pd.concat([part_df, dfPnext.iloc[:, j]],axis=1)
        #print(part_df)
        # concat model numbers
        model_df=pd.concat([dfM.iloc[:, 0], dfMnext.iloc[:, 0]],axis=1)
        for j in range(1,len(dfM.columns)):
            model_df=pd.concat([model_df, dfM.iloc[:, j]],axis=1)
            model_df=pd.concat([model_df, dfMnext.iloc[:, j]],axis=1)
        #print(model_df)
        #print(listDF[i].iloc[0])

        if i<1:
            end_DF= pd.concat([firstline_df, part_df, model_df, listDF[i].iloc[0:],listDF[i+1].iloc[0:]], ignore_index=True, sort=False)
        else:
            end_DFtemp= pd.concat([firstline_df, part_df, model_df, listDF[i].iloc[0:],listDF[i+1].iloc[0:]], ignore_index=True, sort=False)
            end_DF= pd.concat([end_DF, end_DFtemp], axis=1, ignore_index=True, sort=False)
        listIdentityCoefficient=[part_df.shape[0]+model_df.shape[0]]*end_DF.shape[0]
        end_DF.insert(0, "Identity Coefficient", listIdentityCoefficient, True)
    return end_DF


# In[4]:


listDFinSheets=[]
print('Amount of pair to compare: ' +str(len(listOfPartToCompare)))
j=0
for i in listOfPartToCompare:
    j+=1
    listDFinSheets.append(generateArrangedDF(i))
    print(str(j)+' - '+str(i)+' pair compared')

def getIdentityCoefficient(df):
    key=df.iloc[0, df.columns.get_loc('Identity Coefficient')]
    #print(key)
    return key
listDFinSheets.sort(key=getIdentityCoefficient, reverse=True)


# In[5]:


from pandas import ExcelWriter
# from pandas.io.parsers import ExcelWriter
from pathlib import Path
print(Path.cwd())

def highlightCells(df_):
    styles_df = pd.DataFrame('', index=df_.index, columns=df_.columns)
    # Color cells yellow when Model_0==Model_1
    styles_df[df_['Model_0'] == df_['Model_1']] = 'background-color: #FDFFCC'
    # Color cells green when Part_0==Part_1
    styles_df[df_['Part_0'] == df_['Part_1']] = 'background-color: #D3EFC2'
    return styles_df



#df.style.apply(HIGHLIGHT, subset=['Part_0', 'Part_1','Model_0','Model_1'], axis=1)

def save_xls(list_dfs, xls_path):
    with ExcelWriter(xls_path) as writer:
        dfDATA.to_excel(writer,'sheet%s' % 0)
        for n, df in enumerate(list_dfs):
            m=n+1
            #df.style.apply(HIGHLIGHT, subset=['Part_0', 'Part_1'], axis=1)
            df.style.apply(highlightCells, axis=None).to_excel(writer,'sheet%s' % m)
            
save_xls(listDFinSheets,'ComparisonOfMultipleParts_inPairs.xlsx')


# In[ ]:





# In[ ]:




