#!/usr/bin/env python
# coding: utf-8
#
# [FILE] covid19.js
#
# [DESCRIPTION]
#  新型コロナウィルスの感染状況を提示する関数を定義するファイル
#
#
import os
import math
from .http_get import httpGet
from .psql_get import psqlGet
from .covid19_comment import commentGet

# disease.shにアクセスするためのベースURL
BASE_URL=os.environ.get('BASE_URL')
if (BASE_URL == None):
    print("[環境変数未設定] BASE_URL")
# 選択メニューの項目数
NUM_MENUITEMS=os.environ.get('NUM_OF_MENU_ITEMS')
if (NUM_MENUITEMS == None):
  print("[環境変数未設定] NUM_OF_MENU_ITEMS")
numMenuItems = 20
if NUM_MENUITEMS != None:
  numMenuItems = int(NUM_MENUITEMS)

# ---------- Functions ----------

#
# [FUNCTION] translateCountryName()
#
# [DESCRIPTION]
#  国コードあるいは英語の国名を日本語に変換する
# 
# [INPUTS]
# 　country -  国コードあるいは英語の国名
# 
# [OUTPUTS]
#  成功: 翻訳された文字列
#  失敗or見つからない: None
# 
# [NOTE]
#　'Côte d'Ivoire'と'Lao People's Democrat...のように国名にシングルクォートがある場合、「'」の前に「'」を付ける
#
def translateCountryName(country):
  outText = None
  # シングルクォートを置換する
  dest = country.replace("'", "''")
  # countriesテーブルにアクセスし、入力する国名と合致する日本語名を取得する（大文字と小文字を無視する）
  sql = "SELECT name_ja FROM countries WHERE LOWER(iso_code)=LOWER('" + dest + "') OR LOWER(name_en)=LOWER('" + dest + "')"
  result = psqlGet(sql)
  #print(result)

  if result != None and len(result) > 0:
    outText = result[0][0] # Tupleより最初の要素を取り出す

  return outText

#
# [FUNCTION] getCountryInfo()
#
# [DESCRIPTION]
#  指定した国の新型コロナウィルス感染状況をSlack向けブロック構造として整形する
#
# [INPUTS]
#　country - 対象となる国名
#
# [OUTPUTS]
#  成功: {blocks:[<見出し>, <セクション>]}
#  失敗: {type:"plain_text", text:"<エラーメッセージ>"}
# 
# [NOTE]
#  アクセスするURL:
#   https://disease.sh/v3/covid-19/countries/<country>
#   あるいはcountryがallのときは
# 　https://disease.sh/v3/covid-19/all
# 
#  '{:,}'.format() は数値を三桁区切りにする。
#
def getCountryInfo(country):

  retVal = None
  # 対象URLにアクセスし、結果をJSONで取得する
  url = BASE_URL + "countries/" + country
  if country == 'all':
    url = BASE_URL + "all"
  result = httpGet(url)

  blocks = []
  if result != None:
    translated = translateCountryName(country) #日本語国名へ変換
    if translated == None:
      translated = country
    population = '{:,}'.format(int(result['population'])) #人口
    # 見出しの構造を生成する
    title = "[国名] " + translated + " [人口] " + population
    objheader = {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": title,
        #"emoji": True
      }
    }
    blocks.append(objheader)

    active    = '{:,}'.format(int(result['active']))    # 感染者数
    critical  = '{:,}'.format(int(result['critical']))  # 重病者数
    recovered = '{:,}'.format(int(result['recovered'])) # 退院・療養終了
    cases     = '{:,}'.format(int(result['cases']))     # 感染者累計
    deaths    = '{:,}'.format(int(result['deaths']))    # 死亡者累計
    tests     = '{:,}'.format(int(result['tests']))     # 検査数

    # 本体となるセクション構造を生成する
    objBody = {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*感染者数:* " + active
        },
        {
          "type": "mrkdwn",
          "text": "*重病者数:* " + critical
        },
        {
          "type": "mrkdwn",
          "text": "*退院・療養終了:* " + recovered
        },
        {
          "type": "mrkdwn",
          "text": "*感染者累計:* " + cases
        },
        {
          "type": "mrkdwn",
          "text": "*死亡者累計:* " + deaths
        },
        {
          "type": "mrkdwn",
          "text": "*検査数:* " + tests
        },
      ]
    }
    blocks.append(objBody)

    # 注釈を表示する
    comments = commentGet(country)
    if comments != None and len(comments) > 0:
      dt = comments[0][0] # comments[0]は(日時, コメント)のタプルから構成される
      formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
      objComment = {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*記入日時:* " + formatted
          },
          {
            "type": "mrkdwn",
            "text": "*注釈:* " + comments[0][1]
          },
        ]
      }
      blocks.append(objComment)

    # アクションを定義する
    objActions = {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "全世界",
            #"emoji": True
          },
          "style": "primary",
          "value": "all", # アクション関数action-get-info-all()に渡す引数
          "action_id": "action-get-info-all"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "推移グラフ",
            #"emoji": True
          },
          "style": "danger",
          "value": country, # アクション関数action-graph-history()に渡す引数
          "action_id": "action-graph-history"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "レポート作成",
            #"emoji": True
          },
          "style": "primary",
          "value": country, # アクション関数action-report-history()に渡す引数
          "action_id": "action-report-history"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "CSV出力",
            #"emoji": True
          },
          "style": "danger",
          "value": country, # アクション関数action-csv-generate()に渡す引数
          "action_id": "action-csv-generate"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "コメント",
            #"emoji": True
          },
          "style": "primary",
          "value": country, # アクション関数action-comment()に渡す引数
          "action_id": "action-comment"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "国名選択に戻る",
            #"emoji": True
          },
          "value": country, # アクション関数action-get-countries()に渡す引数
          "action_id": "action-get-countries"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "再表示",
            #"emoji": True
          },
          "value": country, # アクション関数action-get-info()に渡す引数
          "action_id": "action-get-info"
        }
      ]
    }
    blocks.append(objActions)

    # 区切り線
    objDivider = {
      "type": "divider"
    }
    blocks.append(objDivider)

    retVal = {
      "blocks": blocks
    }
  else:
    retVal = {
      "type": "plain_text",
      "text": country + "の情報は見つかりませんでした",
      #"emoji": True
    }

  return retVal

#
# [FUNCTION] getCountries()
#
# [DESCRIPTION]
#  Webサイトから利用可能な国名を抽出し、選択項目とする選択メニュー向けブロック構造として整形する
# 
# [INPUTS] 指定なし
# 
# [OUTPUTS]
#  成功: {blocks:[<見出し>, <セクション>]}
#  失敗: {type:"plain_text", text:"<エラーメッセージ>"}
# 
# [NOTE]
#  選択メニューは20カ国ごと（環境変数 NUM_OF_MENU_ITEMSで変更可能）に1つ作成する
#
def getCountries():
  retVal = None
  result = httpGet(BASE_URL + "countries")

  blocks = []
  if result != None and len(result) > 0:
    # 見出しの構造を生成する
    objheader = {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "国名一覧",
        #"emoji": True
      }
    }
    blocks.append(objheader)

    menu_num = math.ceil(len(result) / numMenuItems)
    n = 0
    m = 1
    while (m <= menu_num):
      # 項目トップの国名を日本語に変換
      translated = translateCountryName(result[n]['country'])
      if translated == None:
        translated = result[n]['country']

      # 選択メニューを形成するセクション構造を生成する
      objBody = {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "[" + str(m) + "] 国名: " + translated + "～"
        },
        "accessory": {
          "action_id": "action-select-country",
          "type": "static_select",
          "placeholder": {
            "type": "plain_text",
            "text": "国名を選択"
          },
          "options": []
        }
      }

      count = numMenuItems * m
      if m == menu_num:
        count = len(result) # 最後のメニュー
      while (n < count):
        # 表示名を日本語へ変換
        translated = translateCountryName(result[n]['country'])
        if translated == None:
          translated = result[n]['country']

        objOption = {
          "text": {
            "type": "plain_text",
            "text": translated
          },
          "value": result[n]['country'], # アクション関数action-select-country()に渡す引数
        }
        objBody['accessory']['options'].append(objOption)
        n += 1

      blocks.append(objBody)
      m += 1
      
    # 区切り線
    objDivider = {
      "type": "divider"
    }
    blocks.append(objDivider)

    retVal = {
      "blocks": blocks
    }

  else:
    retVal = {
      "type": "plain_text",
      "text": "国名は見つかりませんでした",
      #"emoji": True
    }

  return retVal

#
# END OF FILE
#