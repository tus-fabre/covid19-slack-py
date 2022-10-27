#!/usr/bin/env python
# coding: utf-8
#
# [FILE] covid19_model.py
#
# [DESCRIPTION]
#  新型コロナウィルス感染者数予測にかかわる関数を定義するファイル
#
# [NOTES]
#
import os
import datetime

from .http_get import httpGet
# disease.shにアクセスするためのベースURL
BASE_URL=os.environ.get('BASE_URL')

#
# [FUNCTION] getHistoricalData()
#
# [DESCRIPTION]
#  指定した日数分の新型コロナウィルスの新規感染者数と死亡者数を取得する
# 
# [INPUTS]
#  country  - 対象となる国名
#  lastdays - 今日から何日前までの情報を取得するか日数を指定する。'all'のときはすべてのデータを対象とする。
# 
# [OUTPUTS]
#  次の出力用引数には初期設定として空リストを関数に与えておく
#  dateL  - 日付のリスト
#  caseL  - 新規感染者数のリスト
#  deathL - 死亡者数のリスト
#  
#  関数が成功すればtrue、失敗したらfalseを返す
# 
# [NOTES]
#  アクセスするURL
#    https://disease.sh/v3/covid-19/historical/<Country>?lastdays=<日数 or all>
#
#  countryがallの場合,　結果の直下にcasesとdeathsのキーが存在する。
#  それ以外の場合、結果の下にtimelineが現れ、その下にcasesとdeathsのキーが存在する。
#
def getHistoricalData(country, lastdays, dateL, caseL, deathL):
  status = False

  if country == "":
    return status

  url = BASE_URL + "historical/" + country + "?lastdays=" + lastdays
  print(url)
  result = httpGet(url)
  if result != None:
    
    # 新たな感染者数を前日との差分として集める
    if country == 'all':
      cases = result["cases"]
    else:
      cases = result["timeline"]["cases"]
      
    previous_value = -1
    for key in cases: # keyは日付：m/d/YY
      num_cases = int(cases[key])
      if previous_value >= 0:
        date_value = convertDateFormat(key) # M/D/YY -> YYYY-MM-DD
        dateL.append(date_value)
        caseL.append(num_cases-previous_value)
      previous_value = num_cases

    # 新たな死亡者数を前日との差分として集める
    if country == 'all':
      deaths = result["deaths"]
    else:
      deaths = result["timeline"]["deaths"]
      
    previous_value = -1
    for key in deaths:
      num_deaths = int(deaths[key])
      if previous_value >= 0:
        deathL.append(num_deaths-previous_value)
      previous_value = num_deaths
      
    status = True
      
  return status

#
# [FUNCTION] convertDateFormat()
#
# [DESCRIPTION]
#  https://disease.shが返す日付形式を標準形式に変換する
# 
# [INPUTS]
#  date  - 変換対象の日付（M/D/YY形式の文字列）
# 
# [OUTPUTS]
#  Dateオブジェクト
#
def convertDateFormat(date):
  list = date.split('/')
  month = int(list[0])
  day = int(list[1])
  year = int("20" + list[2]) # YY -> YYYY
  
  date_obj = datetime.date(year, month, day)
  
  #return date_obj.strftime('%Y-%m-%d')
  return date_obj
  
#
# END OF FILE
#