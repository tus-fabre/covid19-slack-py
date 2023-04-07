#!/usr/bin/env python
# coding: utf-8
#
# [FILE] covid19_charts.js
#
# [DESCRIPTION]
#  新型コロナウィルスの感染状況をグラフとして描画する関数を定義するファイル
#  ただし、Node.js版と異なり、折れ線グラフのスムージングはない。
# 
# グラフ表示のライブラリとグラフ表示で日本語を表示するためのライブラリを読み込む
import matplotlib
# バックエンドを指定
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import japanize_matplotlib

from .covid19_history import getHistoricalData
from .covid19 import translateCountryName

#
# [FUNCTION] chartMonthlyConfiguration()
#
# [DESCRIPTION]
#  指定した国の30日間の新型コロナウィルス新規感染者数を棒グラフ、
#  新たな死亡者数を折れ線グラフとしてファイル保存する
# 
# [INPUTS]
#  country - 対象となる国名
#  filename - 保存する画像ファイル名(フォルダ名を含む)
# 
# [OUTPUTS]
#  成功: True
#  失敗: False
# 
# [NOTES]
#  アクセスするURL:
#     https://disease.sh/v3/covid-19/historical/<Country>?lastdays=31
#
def chartMonthlyConfiguration(country, filename):
  status = False
  if country == '':
    return status

  # 関数getHistoricalData()に与える変数を初期化する
  dateL  = []
  caseL  = []
  deathL = []
  status = getHistoricalData(country, '31', dateL, caseL, deathL)
  if status == True:
    translated = translateCountryName(country) #日本語国名へ変換
    if translated == None:
      translated = country
      
    # グラフを表示する領域をfigとする
    fig = plt.figure(figsize=(12,8))

    # 領域のどこを使用するかを設定する
    # 1行x1列のグリッド、最初のサブプロット
    fig, ax1 = plt.subplots(1,1,figsize=(10,8))
    ax2 = ax1.twinx()

    # グラフ見出し、軸ラベルを設定する
    title = '新規感染者数・死者数の推移 (' + country + ')'
    ax1.set_title(title, fontsize=18)
    ax1.set_xlabel('日付', fontsize=12)
    ax1.set_ylabel('感染者数 (人)', fontsize=12)
    ax2.set_ylabel('死亡者数 (人)', fontsize=12)
    # 棒グラフ（感染者数）の設定
    ax1.bar(dateL, caseL, color='teal', label='感染者数')
    handles1, labels1 = ax1.get_legend_handles_labels()
    # 線グラフ（死亡者数）の設定
    ax2.plot(dateL, deathL, color='magenta', label='死亡者数')
    handles2, labels2 = ax2.get_legend_handles_labels()
    # 上限・下限値を設定する
    #ax1.set_ylim(100, 10000)
    #ax2.set_ylim(0, 500)
    # 凡例 - 2つのラベルを結合し、上中央に2列で配置する
    ax1.legend(handles1 + handles2, labels1 + labels2, ncols=2, loc='upper center')
    # グリッド線
    ax1.grid()
  
    # 画像を保存する
    fig.savefig(filename)
    status = True
    
  return status

#
# [FUNCTION] chartWeeklyConfiguration()
#
# [DESCRIPTION]
#  日本での新型コロナウィルス新規感染者数を一週間分を折れ線グラフとしてファイル保存する
# 
# [INPUTS]
#  filename - 保存する画像ファイル名(フォルダ名を含む)
# 
# [OUTPUTS]
#  成功: True
#  失敗: False
# 
# [NOTES]
#  アクセスするURL:
#     https://disease.sh/v3/covid-19/historical/Japan?lastdays=8
#
def chartWeeklyConfiguration(filename):

  status = False

  # 関数getHistoricalData()に与える変数を初期化する
  dateL  = []
  caseL  = []
  deathL = []
  status = getHistoricalData('Japan', '8', dateL, caseL, deathL)
  if status == True:     
    # グラフを表示する領域をfigとする
    fig = plt.figure(figsize=(12,8))

    # 領域のどこを使用するかを設定する
    # 1行x1列のグリッド、最初のサブプロット
    ax = fig.add_subplot(111)

    # グラフを設定する - 感染者数(line) blue
    title = '今週の新規感染者数'
    ax.set_title(title, fontsize=18)
    ax.set_xlabel('日付', fontsize=12)
    ax.set_ylabel('感染者数 (人)', fontsize=12)
    ax.fill_between(dateL, caseL, color="blue", alpha=0.5) # 線の下を塗りつぶす
    ax.plot(dateL, caseL)
    ax.legend(['感染者数'], loc='upper left') # 凡例
    ax.grid()
  
    # 画像を保存する
    fig.savefig(filename)
    status = True
    
  return status

#
# END OF FILE
#