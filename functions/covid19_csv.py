#!/usr/bin/env python
# coding: utf-8
#
# [FILE] covid19_csv.js
#
# [DESCRIPTION]
#  新型コロナウィルスの感染状況をCSVファイルに保存する関数を定義するファイル
# 
# [NOTE]
#  生成するCSVファイルは環境変数LOCAL_FOLDERに設定されたフォルダーに保存される。
#
import os
import csv
from .current_time import currentTimeStamp
from .covid19_history import getHistoricalData
# ファイルを保存するフォルダー名
LOCAL_FOLDER = os.environ.get("LOCAL_FOLDER")

#
# [FUNCTION] csvGenerateFile()
#
# [DESCRIPTION]
#  日々の新型コロナウィルス新規感染者数と死亡者数をCSVファイルに保存する
# 
# [INPUTS]
#  country - 対象となる国名
# 
# [OUTPUTS]
#  成功: 作成されたCSVファイル名
#  失敗: None
# 
# [NOTE]
#  アクセスするURL:
#     https://disease.sh/v3/covid-19/historical/<Country>?lastdays=all
#
def csvGenerateFile(country):
  output_file = None # Output variable

  # 関数getHistoricalData()に与える変数を初期化する
  dateL  = [] # 日付のリスト
  caseL  = [] # 新規感染者数のリスト
  deathL = [] # 死亡者数のリスト
  status = getHistoricalData(country, 'all', dateL, caseL, deathL)
  if status == True:
    # ファイルを上書きしないようにタイムスタンプを名前に付与する
    timestamp = currentTimeStamp()
    output_file = LOCAL_FOLDER + "/" + country + "-all-" + str(timestamp) + ".csv"
    try:
      with open(output_file, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(['Date', 'Cases', 'Deaths']) # ファイルヘッダー
        # レコードごとにファイルに書き込む
        for i in range(len(dateL)):
           writer.writerow([dateL[i], caseL[i] , deathL[i]]) 
      print("[INFO] ", output_file, 'は保存されました')
    except Exception as e:
      print(e)
      output_file = None

  return output_file

#
# END OF FILE
#