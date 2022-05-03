import dtExtractFromBQ as bq
import pandas as pd
import numpy as np
import time

product = ""
numCases = 0
numUniqueCases = 0
numSameCases = 0
numDiffeCases = 0

dataframe_collection_all = []
testplanid_collection_all = [] 

dataframe_collection_fam = []
testplanid_collection_fam = [] 

#Product Data Dictionary#

ProductsMidTier = { ... } # Hidden due to non-disclosure agreement


def preAPFD(df):
  global n, m, apfd_filtered, history_size

  apfd_filtered = df.filter(items=['TestPlanID','TestCaseID','TC_ID_Only','Summary','AffectsVersion','Product','TestResults',
    'RemoteDefectCR','BlockedCRNumber','BlockedReason','TestDate','FailuresPercentage','HistorySize'])
  apfd_filtered['TestDate'] = pd.to_datetime(apfd_filtered['TestDate'])
  apfd_filtered['ProductCN'] = [ProductsMidTier[i] for i in apfd_filtered.Product]

  # HistorySizeTotal
  history_size = apfd_filtered['HistorySize'].sum()

  # TestCasesTotal
  n = apfd_filtered['TestCaseID'].size

  TCsFail = apfd_filtered.where(apfd_filtered.TestResults == 'Fail').dropna(how='all')
  TCsBlockedByCR = apfd_filtered.where(apfd_filtered.BlockedReason == '[CR] Known Product CR').dropna(how='all')
  mergeData = [TCsFail,TCsBlockedByCR]
  allCrs = pd.concat(mergeData, ignore_index=True, sort=False)

  uniqueBlockedCrs = allCrs["BlockedCRNumber"].dropna().unique()
  uniqueFailCrs = allCrs["RemoteDefectCR"].dropna().unique()
  uniqueCrs = [*uniqueBlockedCrs, *uniqueFailCrs]
  
  # using native method to remove duplicated from list 
  res = []
  for i in uniqueCrs:
      if i not in res:
          res.append(i)

  #NumIssues
  m = len(res)  
# -- preAPFD()


def preAPFD_fam(df):
  global n_fam, m_fam, apfd_filtered_fam, history_size_fam

  apfd_filtered_fam = df.filter(items=['TestPlanID','TestCaseID','TC_ID_Only','Summary','AffectsVersion','Product','TestResults',
    'RemoteDefectCR','BlockedCRNumber','BlockedReason','TestDate','FailuresPercentage','HistorySize'])
  apfd_filtered_fam['TestDate'] = pd.to_datetime(apfd_filtered_fam['TestDate'])
  apfd_filtered_fam['ProductCN'] = [ProductsMidTier[i] for i in apfd_filtered_fam.Product]

  # HistorySizeTotal
  history_size_fam = apfd_filtered_fam['HistorySize'].sum()

  # TestCasesTotal
  n_fam = apfd_filtered_fam['TestCaseID'].size

  TCsFail = apfd_filtered_fam.where(apfd_filtered_fam.TestResults == 'Fail').dropna(how='all')
  TCsBlockedByCR = apfd_filtered_fam.where(apfd_filtered_fam.BlockedReason == '[CR] Known Product CR').dropna(how='all')
  mergeData = [TCsFail,TCsBlockedByCR]
  allCrs = pd.concat(mergeData, ignore_index=True, sort=False)

  uniqueBlockedCrs = allCrs["BlockedCRNumber"].dropna().unique()
  uniqueFailCrs = allCrs["RemoteDefectCR"].dropna().unique()
  uniqueCrs = [*uniqueBlockedCrs, *uniqueFailCrs]
  
  # using native method to remove duplicated from list 
  res = []
  for i in uniqueCrs:
      if i not in res:
          res.append(i)

  #NumIssues
  m_fam = len(res)  
# -- preAPFD_fam()


# Let T be a test suite containing n test cases and let F be a
# set of m faults revealed by T. Let TFi be the first test case in
# ordering T0 of T which reveals fault i. The APFD for test
# suite T0 is given by the equation:

def APFD(TotalExecOrd, CasesTotal, NumIssues):
    apfd = 1 - (TotalExecOrd/(CasesTotal*NumIssues)) + (1/(2*CasesTotal))
    return apfd
# -- APFD()


def IsolateUniquesCRs(df):
  
  uniCrs = []
  data = pd.DataFrame(columns=['TestPlanID','TestCaseID','TC_ID_Only','Summary','AffectsVersion','Product','TestResults',
    'RemoteDefectCR','BlockedCRNumber','BlockedReason','TestDate','ExecOrd','FailuresPercentage','HistorySize'])

  for index, row in df.iterrows():
    aux = row.name
    
    if df.iloc[aux]['TestResults'] == "Fail":
      cr = row['RemoteDefectCR']

      if cr not in uniCrs:
        uniCrs.append(cr)  
        data.loc[aux] = row

    if df.iloc[aux]['TestResults'] == "Blocked":
      cr = row['BlockedCRNumber']

      if cr not in uniCrs:
        uniCrs.append(cr)     
        data.loc[aux] = row

  TFj = data['ExecOrd'].sum()
  
  return TFj
# -- IsolateUniquesCRs()


def SeparateFailures(df):

  auxFail = df.where(df.TestResults == 'Fail').dropna(how='all')
  auxBlocked = df.where(df.BlockedReason == '[CR] Known Product CR').dropna(how='all')
  mergeData = [auxFail,auxBlocked]
  allFailures = pd.concat(mergeData, ignore_index=True, sort=False)

  return allFailures
# -- SeparateFailures()

def CalcAPFD(df):
  count = 0
  for index, row in df.iterrows():
    count += 1
    df.loc[index,'ExecOrd'] = count

  allFailureOtd = SeparateFailures(df)

  # TotalExecOrd
  tfj = IsolateUniquesCRs(allFailureOtd)

  apfd = APFD(tfj,n,m)
  return apfd
 # -- CalcAPFD


def CalcAPFD_fam(df):
  count = 0
  for index, row in df.iterrows():
    count += 1
    df.loc[index,'ExecOrd'] = count

  allFailureOtd = SeparateFailures(df)

  # TotalExecOrd
  tfj = IsolateUniquesCRs(allFailureOtd)

  apfd = APFD(tfj,n_fam,m_fam)
  return apfd
 # -- CalcAPFD


def CasesIdentifier(listaPlansIDs,pos,date):
  initDate = date

  global numCases, numUniqueCases, numSameCases, numDiffeCases
  MainPlan = pd.DataFrame() #MainPlan
  ComparedPlans = pd.DataFrame() #ComparedPlans

  numUniqueCases = 0
  auxList = []
  aux = 0

  #plano 01
  bq.updateAllCasesQuery(listaPlansIDs[pos],initDate)
  MainPlan = bq.getPlanData()

  dataframe_collection_all.append(MainPlan)
  testplanid_collection_all.append(MainPlan['TestPlanID'][0]) 

  list01 = MainPlan['TestCaseID'].tolist()
  a01 = set(list01)

  product = MainPlan['Product'][0]
  numCases = len(list01)

  if pos == 0:
    #list02 = list01
    a02 = set(list01)
  else:
    for i in listaPlansIDs:
      #plano 02
      if listaPlansIDs[aux] in testplanid_collection_all:
        ComparedPlans = dataframe_collection_all[aux]
      else:
        bq.updateAllCasesQuery(listaPlansIDs[aux],initDate)
        ComparedPlans = bq.getPlanData()

      list02 = ComparedPlans['TestCaseID'].tolist()
      auxList = auxList+list02
      aux+=1

      if aux == (pos+1):
        break

    auxList = list(dict.fromkeys(auxList)) # remove dup
    a02 = set(auxList)

    numUniqueCases = len(auxList)   
    
  ls_common = a02.intersection(a01)
  ls_not_common = a02.difference(a01)

  sameCases = list(ls_common)
  numSameCases = len(sameCases)
  diffeCases = list(ls_not_common)
  numDiffeCases = len(diffeCases)

  return sameCases, diffeCases;
# -- CasesIdentifier


def CasesIdentifier_fam(listaPlansIDs,pos,date,familyProducts):
  initDate = date

  global numCases_fam, numUniqueCases_fam, numSameCases_fam, numDiffeCases_fam
  MainPlan_fam = pd.DataFrame() #MainPlan
  ComparedPlans_fam = pd.DataFrame() #ComparedPlans

  numUniqueCases_fam = 0
  auxList_fam = []
  aux_fam = 0

  #plano 01
  bq.updateFamilyQuery(listaPlansIDs[pos],initDate,familyProducts)
  MainPlan_fam = bq.getPlanData()

  dataframe_collection_fam.append(MainPlan_fam)
  testplanid_collection_fam.append(MainPlan_fam['TestPlanID'][0]) 

  list01 = MainPlan_fam['TestCaseID'].tolist()
  a01 = set(list01)

  product = MainPlan_fam['Product'][0]
  numCases_fam = len(list01)

  if pos == 0:
    #list02 = list01
    a02 = set(list01)
  else:
    for i in listaPlansIDs:
      #plano 02
      if listaPlansIDs[aux_fam] in testplanid_collection_fam:
        ComparedPlans_fam = dataframe_collection_fam[aux_fam]
      else:
        bq.updateFamilyQuery(listaPlansIDs[aux_fam],initDate,familyProducts)
        ComparedPlans_fam = bq.getPlanData()

      list02 = ComparedPlans_fam['TestCaseID'].tolist()
      auxList_fam = auxList_fam+list02
      aux_fam+=1

      if aux_fam == (pos+1):
        break

    auxList_fam = list(dict.fromkeys(auxList_fam)) # remove dup
    a02 = set(auxList_fam)

    numUniqueCases_fam = len(auxList_fam)   

  ls_common = a02.intersection(a01)
  ls_not_common = a02.difference(a01)

  sameCases = list(ls_common)
  numSameCases_fam = len(sameCases)
  diffeCases = list(ls_not_common)
  numDiffeCases_fam = len(diffeCases)

  return sameCases, diffeCases;
# -- CasesIdentifier_fam

""" ================================================================================================================================================= """
# Different APFDs Results based on its TCs ordination
""" ================================================================================================================================================= """

def OrderedTestDate():
# Ordered by Test Date = otd 
# Here we are following the dates that testers used to execute the plan, without any specific prioritization.

  apfd_otd = apfd_filtered.sort_values(by='TestDate')
  apfd_otd['ExecOrd'] = 'NaN'

  otd = CalcAPFD(apfd_otd)
  return otd
# -- OrderedTestDate


def RandomlyOrdered():
# Randomly Ordered = ro

  apfd_ro = apfd_filtered.reindex(np.random.permutation(apfd_filtered.index))
  apfd_ro['ExecOrd'] = 'NaN'

  ro = CalcAPFD(apfd_ro)
  return ro
# -- RandomlyOrdered


def BestOrdered():
# Best Ordered = bo
# In this scenario, the 'fail' and 'blocked by CR' cases are added at the beginning of the list, as if they were executed first.

  tempdf = apfd_filtered

  auxFail = tempdf.where(tempdf.TestResults == 'Fail').dropna(how='all')
  auxBlocked = tempdf.where(tempdf.BlockedReason == '[CR] Known Product CR').dropna(how='all')
  # df.query('c != [1, 2]')
  auxOtherResults = tempdf.query('TestResults != ["Fail","Blocked"]')
  
  allCases = [auxFail,auxBlocked,auxOtherResults]
  apfd_bo = pd.concat(allCases, ignore_index=True, sort=False)

  apfd_bo['ExecOrd'] = 'NaN'

  bo = CalcAPFD(apfd_bo)
  return bo
# -- BestOrdered


def OrderedHistoryBase01(same_cases, diff_cases):
# Ordered by History Base = ohb 
# This is the first trial of our heuristic, where the cases are being ordered
# putting on top the cases with the higher failure percentage average
  global ohb1_prio_time
  ohb1_init_time = time.clock()

  SameCasesDF = pd.DataFrame({"TestCaseID": same_cases})
  DiffCasesDF = pd.DataFrame({"TestCaseID": diff_cases})

  #result = pd.merge(left, right, on="key")
  SameCasesDF = pd.merge(SameCasesDF,apfd_filtered, on="TestCaseID")
  SameCasesDF = SameCasesDF.sort_values(by='FailuresPercentage', ascending=False)

  DiffCasesDF = pd.merge(DiffCasesDF,apfd_filtered, on="TestCaseID")
  DiffCasesDF = DiffCasesDF.sort_values(by='TC_ID_Only', ascending=False) #mais novo > mais velho

  apfd_ohb1 = SameCasesDF.append(DiffCasesDF)
  apfd_ohb1['ExecOrd'] = 'NaN'

  # HistorySizeTotal
  ohb1_hist_size = apfd_ohb1['HistorySize'].sum()

  ohb1 = CalcAPFD(apfd_ohb1)

  ohb1_end_time = time.clock()
  ohb1_prio_time = round(ohb1_end_time - ohb1_init_time, 2) #tempo

  return ohb1
# -- OrderedHistoryBase


def OrderedHistoryBase02(same_cases, diff_cases, familyProducts):
# Ordered by History Base = ohb 
# This is the first trial of our heuristic, where the cases are being ordered
# putting on top the cases with the higher failure percentage average
  global ohb2_prio_time
  ohb2_init_time = time.clock()

  SameCasesDF = pd.DataFrame({"TestCaseID": same_cases})
  DiffCasesDF = pd.DataFrame({"TestCaseID": diff_cases})

  #result = pd.merge(left, right, on="key")
  SameCasesDF = pd.merge(SameCasesDF,apfd_filtered_fam, on="TestCaseID")
  SameCasesDF = SameCasesDF.sort_values(by='FailuresPercentage', ascending=False)

  DiffCasesDF = pd.merge(DiffCasesDF,apfd_filtered_fam, on="TestCaseID")
  DiffCasesDF = DiffCasesDF.sort_values(by='TC_ID_Only', ascending=False) #mais novo > mais velho

  apfd_ohb2 = SameCasesDF.append(DiffCasesDF)
  apfd_ohb2['ExecOrd'] = 'NaN'

  # HistorySizeTotal
  ohb2_hist_size = apfd_ohb2['HistorySize'].sum()

  ohb2 = CalcAPFD_fam(apfd_ohb2)

  ohb2_end_time = time.clock()
  ohb2_prio_time = round(ohb2_end_time - ohb2_init_time, 2) #tempo

  return ohb2
# -- OrderedHistoryBase02


def NewToOlder():
# Case Criation Order = New case to Old case 
# Follows the order of the case criation, from new to older cases.

  apfd_nto = apfd_filtered.sort_values(by='TC_ID_Only', ascending=False)
  apfd_nto['ExecOrd'] = 'NaN'

  nto = CalcAPFD(apfd_nto)
  return nto
# -- NewToOlder