from google.colab import auth
auth.authenticate_user()
print('Authenticated')

#Import Libs

!pip install --upgrade gspread
from oauth2client.client import GoogleCredentials

import pandas as pd
import numpy as np
import requests
import gspread
import time

from datetime import datetime

# Importing the dtExtractFromBQ.py from github, make sure you get the "Raw" version of the code
url = 'https://raw.githubusercontent.com/.../dtExtractFromBQ.py?token=...'
r = requests.get(url)

# make sure your filename is the same as how you want to import 
with open('dtExtractFromBQ.py', 'w') as f:
    f.write(r.text)

import dtExtractFromBQ as bq

# Importing the metricsHBPrio.py from github, make sure you get the "Raw" version of the code
url = 'https://raw.githubusercontent.com/.../metricsHBPrio.py?token=...'
r = requests.get(url)

# make sure your filename is the same as how you want to import 
with open('metricsHBPrio.py', 'w') as f:
    f.write(r.text)

# now we can import
import metricsHBPrio as mt

#APFD Analysis
"""

Product_Family = [...] #Hidden due to non-disclosure agreement
familyProducts = "'" + "', '".join(Product_Family) + "'" 
plans = [...] #Hidden due to non-disclosure agreement

def APFDResults(append_index, plan, date): 
  ro_med = 0
  mesmo_all, diferente_all = mt.CasesIdentifier(reorderedPlans,append_index,date)
  mesmo_fam, diferente_fam = mt.CasesIdentifier_fam(reorderedPlans,append_index,date,familyProducts)

  for x in range(0, 30):
      ro_med += mt.RandomlyOrdered()

  ro_med = round(ro_med/30, 2)
  otd = round(mt.OrderedTestDate(), 2)
  bo = round(mt.BestOrdered(), 2)
  nto = round(mt.NewToOlder(), 2)
  ohb_01 = round(mt.OrderedHistoryBase01(mesmo_all, diferente_all,), 2)
  ohb_02 = round(mt.OrderedHistoryBase02(mesmo_fam, diferente_fam, familyProducts), 2)

  df1 = pd.DataFrame({"Device": [mt.apfd_filtered['ProductCN'][0]],"TP Id": [plan],"# TCs": [mt.numCases],"# Failures":[mt.m],"Unique Cases": [mt.numUniqueCases],
                      "Same Cases":[mt.numSameCases],"Diff Cases":[mt.numDiffeCases],"History Size":[mt.history_size],"Optimal": [bo],"HB-all": [ohb_01],"Prio Time all" : [mt.ohb1_prio_time],
                      "Prep Time all" : [bq.all_prep_time],"All Cases hist. size" : [mt.history_size],"HB-fam": [ohb_02],"Prio Time fam" : [mt.ohb2_prio_time],"Prep Time fam" : [bq.fam_prep_time],
                      "Fam Cases hist. size" : [mt.history_size_fam],"RealOrd": [otd],"NewOld": [nto],"Rnd": [ro_med],"Initial Date": [date]},index=[append_index])

  global df2

  df2 = pd.DataFrame({
                      'Product': [mt.apfd_filtered['ProductCN'][0],'---','---','---','---','---'],
                      'TP Id': [plan,'---','---','---','---','---'],
                      'Approach': ['Optimal','HB-all','HB-fam','RealOrd','NewOld','Rnd'],
                      'APFD': [bo, ohb_01, ohb_02, otd, nto, ro_med],
                      'History Size':['---',mt.history_size,mt.history_size_fam,'---','---','---'],
                      'Prio Time': ['---',mt.ohb1_prio_time,mt.ohb2_prio_time,'---','---','---'],
                      'Prep Time': ['---',bq.all_prep_time,bq.fam_prep_time,'---','---','---']
                      },
                  index=['1','2','3','4','5','6'])

  #Product	TP_Id	Approach	Prio_Time	Prep_Time	Total_Time
  global df3

  df3 = pd.DataFrame({
                      'Product': [mt.apfd_filtered['ProductCN'][0],mt.apfd_filtered['ProductCN'][0]],
                      'TP Id': [plan,plan],
                      'Approach': ['HB-all','HB-fam'],
                      'Prio Time': [mt.ohb1_prio_time,mt.ohb2_prio_time],
                      'Prep Time': [bq.all_prep_time,bq.fam_prep_time],
                      'Total Time': [mt.ohb1_prio_time+bq.all_prep_time,mt.ohb2_prio_time+bq.fam_prep_time],
                      },
                  index=['1','2'])

  return df1  
# -- APFDResults

#Reorder plans from the initial date
PlansDateInfo = pd.DataFrame()
a=0
x=0

for i in plans:
  bq.getPlanInitDateQuery(i)
  df = bq.getPlanInitDate()
  df['PlanID'] = i
  
  df.rename(index={0:a},inplace=True)
  PlansDateInfo = PlansDateInfo.append(df)
  a+=1

PlansDateInfo['dataInicial'] = pd.to_datetime(PlansDateInfo['DateInit'])
PlansDateInfo = PlansDateInfo.sort_values(by='dataInicial', ascending=True)

reorderedPlans = PlansDateInfo['PlanID'].tolist()

FamilyTrial_df = pd.DataFrame()
FamilyTrial_R_data_df = pd.DataFrame()
FamilyTrial_R_data_time_df = pd.DataFrame()

dates = []
dates = PlansDateInfo['DateInit'].tolist()

for j in dates:
  bq.updateAllCasesQuery((PlansDateInfo['PlanID'].iloc[x]),(PlansDateInfo['DateInit'].iloc[x]))
  bq.updateFamilyQuery((PlansDateInfo['PlanID'].iloc[x]),(PlansDateInfo['DateInit'].iloc[x]),familyProducts)
  mt.preAPFD(bq.getPlanData())
  mt.preAPFD_fam(bq.getPlanDataFamily())
  df = APFDResults(x,(PlansDateInfo['PlanID'].iloc[x]),(PlansDateInfo['DateInit'].iloc[x]))
  x+=1
  FamilyTrial_df = FamilyTrial_df.append(df)
  FamilyTrial_R_data_df = FamilyTrial_R_data_df.append(df2)
  FamilyTrial_R_data_time_df = FamilyTrial_R_data_time_df.append(df3)

FamilyTrial_R_data_df['APFD'] = FamilyTrial_R_data_df['APFD'].astype(str)
FamilyTrial_R_data_df['History Size'] = FamilyTrial_R_data_df['History Size'].astype(str)

"""###Save output to HBPrio Trial Spreadsheet 

[HBPrio Trial Spreadsheet](https://docs.google.com/)
"""

gc = gspread.authorize(GoogleCredentials.get_application_default())

wbfullRecordData = gc.open_by_key("...")
today = datetime.now().strftime('%d/%m/%Y|%H:%M')

newSheetNameRecordData = 'Execution Record - '+ today+'(utc)'
newSheetNameRDataAPFD = 'R Data APFD - '+ today+'(utc)'
newSheetNameRDataTime = 'R Data Time - '+ today+'(utc)'

wbfullRecordData.duplicate_sheet(1426537970,new_sheet_name=newSheetNameRecordData)
wbfullRecordData.duplicate_sheet(1563854476,new_sheet_name=newSheetNameRDataAPFD)
wbfullRecordData.duplicate_sheet(296864002,new_sheet_name=newSheetNameRDataTime)

newSheetRecordData = wbfullRecordData.worksheet(newSheetNameRecordData)
newSheetRDataAPFD = wbfullRecordData.worksheet(newSheetNameRDataAPFD)
newSheetRDataTime = wbfullRecordData.worksheet(newSheetNameRDataTime)

plansInfosListRecordData = FamilyTrial_df.values.tolist()
plansInfosListRDataAPFD = FamilyTrial_R_data_df.values.tolist()
plansInfosListRDataTime = FamilyTrial_R_data_time_df.values.tolist()

newSheetRecordData.update('C3:W56',plansInfosListRecordData)
newSheetRDataAPFD.update('A2:G',plansInfosListRDataAPFD)
newSheetRDataTime.update('A2:F',plansInfosListRDataTime)