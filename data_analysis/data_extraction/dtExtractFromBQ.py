import pandas as pd
import time
from google.cloud import bigquery
from oauth2client.client import GoogleCredentials

# variables
5472_project = '5472-142717'
5472_bq_dataset = '32535'

# connections
client = bigquery.Client(project = 5472_project)
dataset = client.dataset(5472_bq_dataset)

# results to dataframe function, get BQ data and add to a local df
def 32535bq2df(sql):
	query = client.query(sql)
	results = query.result()
	return results.to_dataframe()


def updateAllCasesQuery(Plan_ID, date):
  planID = Plan_ID
  initDate = date
  global HistoryQueryAllCases, TestPlanAllQuery

  HistoryQueryAllCases = """DECLARE SearchedPlan STRING DEFAULT '""" + planID + """';
  DECLARE TestDateStart STRING DEFAULT '""" + initDate + """';

    SELECT 

    TEST_CASE_ID_CF AS TestCaseID,
        COUNTIF(TEST_RESULTS_CF = "Pass"AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart)) AS Pass,
        COUNTIF(TEST_RESULTS_CF = "Delete"AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart)) AS Deleted,
        COUNTIF(TEST_RESULTS_CF = "Blocked" AND BLOCKED_CR_NUMBER_CF IS NULL AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart)) AS BlockedNotCR,
        COUNTIF(TEST_RESULTS_CF = "Fail"AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart)) AS Fail,
        COUNTIF(TEST_RESULTS_CF = "Blocked" AND BLOCKED_CR_NUMBER_CF IS NOT NULL AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart)) AS BlockedByCR,

    FROM `5472-142717.32535.32535_data`
        WHERE TEST_CASE_ID_CF in (SELECT TEST_CASE_ID_CF 
                                        FROM `5472-142717.32535.32535_data` 
                                        WHERE TEST_PLAN_CR_CF = SearchedPlan)
    GROUP BY TEST_CASE_ID_CF
    ORDER BY TEST_CASE_ID_CF DESC"""
  # This order by desc is to match default 32535 ordination

  TestPlanAllQuery = """DECLARE SearchedPlan STRING DEFAULT '""" + planID + """'; \n\nSELECT
    TEST_PLAN_CR_CF AS TestPlanID, 
    TEST_CASE_ID_CF AS TestCaseID,
        SPLIT(TEST_CASE_ID_CF, "-")[OFFSET(1)] AS TC_ID_Only,
    issue_key AS Issuekey, 
    summary,
    affected_versions AS AffectsVersion, 
    PRODUCT_CF AS Product,
    TEST_DATE_CF AS TestDate,
    TEST_RESULTS_CF AS TestResults,
    BLOCKED_CR_NUMBER_CF AS BlockedCRNumber, 
    REMOTE_DEFECT_CR_CF AS RemoteDefectCR, 
    
  FROM `5472-142717.32535.32535_data`
      WHERE issue_key in (SELECT issue_key 
                              FROM `5472-142717.32535.32535_data` 
                                  WHERE TEST_PLAN_CR_CF = SearchedPlan)
  ORDER BY TEST_CASE_ID_CF DESC"""
  # This order by desc is to match default 32535 ordination
# -- updateAllCasesQuery()


def updateFamilyQuery(Plan_ID, date, familyProductsString):
  planID = Plan_ID
  initDate = date
  global HistoryQuerybyFamily, TestPlanFamilyQuery

  HistoryQuerybyFamily = """DECLARE SearchedPlan STRING DEFAULT '""" + planID + """';
  DECLARE TestDateStart STRING DEFAULT '""" + initDate + """';

    SELECT 

    TEST_CASE_ID_CF AS TestCaseID,
        COUNTIF(TEST_RESULTS_CF = "Pass"AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart) AND PRODUCT_CF IN(""" + familyProductsString + """)) AS Pass,
        COUNTIF(TEST_RESULTS_CF = "Delete"AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart) AND PRODUCT_CF IN(""" + familyProductsString + """)) AS Deleted,
        COUNTIF(TEST_RESULTS_CF = "Blocked" AND BLOCKED_CR_NUMBER_CF IS NULL AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart)AND PRODUCT_CF IN(""" + familyProductsString + """)) AS BlockedNotCR,
        COUNTIF(TEST_RESULTS_CF = "Fail"AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart) AND PRODUCT_CF IN(""" + familyProductsString + """)) AS Fail,
        COUNTIF(TEST_RESULTS_CF = "Blocked" AND BLOCKED_CR_NUMBER_CF IS NOT NULL AND PARSE_DATE('%d-%b-%y',TEST_DATE_CF) <= PARSE_DATE('%d-%b-%y',TestDateStart) AND PRODUCT_CF IN(""" + familyProductsString + """)) AS BlockedByCR,

    FROM `5472-142717.32535.32535_data`
        WHERE TEST_CASE_ID_CF in (SELECT TEST_CASE_ID_CF 
                                        FROM `5472-142717.32535.32535_data` 
                                        WHERE TEST_PLAN_CR_CF = SearchedPlan)
    GROUP BY TEST_CASE_ID_CF
    ORDER BY TEST_CASE_ID_CF DESC"""
  # This order by desc is to match default 32535 ordenation

  TestPlanFamilyQuery = """DECLARE SearchedPlan STRING DEFAULT '""" + planID + """'; \n\nSELECT
    TEST_PLAN_CR_CF AS TestPlanID, 
    TEST_CASE_ID_CF AS TestCaseID,
        SPLIT(TEST_CASE_ID_CF, "-")[OFFSET(1)] AS TC_ID_Only,
    issue_key AS Issuekey, 
    summary,
    affected_versions AS AffectsVersion, 
    PRODUCT_CF AS Product,
    TEST_DATE_CF AS TestDate,
    TEST_RESULTS_CF AS TestResults,
    BLOCKED_CR_NUMBER_CF AS BlockedCRNumber, 
    REMOTE_DEFECT_CR_CF AS RemoteDefectCR, 
    
  FROM `5472-142717.32535.32535_data`
      WHERE issue_key in (SELECT issue_key 
                              FROM `5472-142717.32535.32535_data` 
                                  WHERE TEST_PLAN_CR_CF = SearchedPlan)
  ORDER BY TEST_CASE_ID_CF DESC"""
  # This order by desc is to match default 32535 ordination
# -- updateFamilyQuery()

def getPlanInitDateQuery(Plan_ID):
  planID = Plan_ID
  global GetMinDateQuery

  GetMinDateQuery = """DECLARE SearchedPlan STRING DEFAULT '""" + planID + """';

    SELECT MIN(TEST_DATE_CF) AS DateInit
        FROM `5472-142717.32535.32535_data`  
            WHERE TEST_PLAN_CR_CF = SearchedPlan"""
# -- getPlanInitDateQuery()


def getPlanData():

  global all_prep_time 
  all_init_time = time.clock()

  history_df = 32535bq2df(HistoryQueryAllCases)
  history_df = history_df.assign(FailuresPercentage = round((history_df.Fail + history_df.BlockedByCR)/(history_df.Pass + history_df.Deleted + history_df.BlockedNotCR + history_df.Fail + history_df.BlockedByCR), 2))
  history_df = history_df.assign(HistorySize = history_df.Pass + history_df.Deleted + history_df.BlockedNotCR + history_df.Fail + history_df.BlockedByCR)
  test_plan_df = 32535bq2df(TestPlanAllQuery)

  planData = pd.merge(test_plan_df, history_df, on="TestCaseID")

  all_end_time = time.clock()
  all_prep_time = round(all_end_time - all_init_time, 2) #tempo

  return planData
# -- getPlanData()


def getPlanDataFamily():

  global fam_prep_time 
  fam_init_time = time.clock()
  
  history_df = 32535bq2df(HistoryQuerybyFamily)
  history_df = history_df.assign(FailuresPercentage = round((history_df.Fail + history_df.BlockedByCR)/(history_df.Pass + history_df.Deleted + history_df.BlockedNotCR + history_df.Fail + history_df.BlockedByCR), 2))
  history_df = history_df.assign(HistorySize = history_df.Pass + history_df.Deleted + history_df.BlockedNotCR + history_df.Fail + history_df.BlockedByCR)
  test_plan_df = 32535bq2df(TestPlanFamilyQuery)

  planData = pd.merge(test_plan_df, history_df, on="TestCaseID")

  fam_end_time = time.clock()
  fam_prep_time = round(fam_end_time - fam_init_time, 2) #tempo

  return planData
# -- getPlanDataFamily()

def getPlanInitDate():
  df_planos_datas = 32535bq2df(GetMinDateQuery)
  return df_planos_datas

#NOTES

# Both time.time() and time.clock() show that the wall-clock time passed approximately one second. Unlike Unix, time.clock() does not return the CPU time, instead it returns the wall-clock
# time with a higher precision than time.time().

# Given the platform-dependent behavior of time.time() and time.clock(), which one should we use to measure the "exact" performance of a program? Well, it depends. If the program is expected
# to run in a system that almost dedicates more than enough resources to the program, i.e., a dedicated web server running a Python-based web application, then measuring the program using 
# time.clock() makes sense since the web application probably will be the major program running on the server. If the program is expected to run in a system that also runs lots of other 
# programs at the same time, then measuring the program using time.time() makes sense. Most often than not, we should use a wall-clock-based timer to measure a program's performance since 
# it often reflects the productions environment.