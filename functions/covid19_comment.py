#!/usr/bin/env python
# coding: utf-8
#
# [FILE] covid19_comment.js
#
# [DESCRIPTION]
#  モーダルビューを用いたコメント機能に関わる関数を定義するファイル
# 
# [NOTES]
#
import os
import json
from .psql_get import psqlGet, psqlInsert
from dotenv import load_dotenv
load_dotenv()

pyEnv=os.environ.get('PY_ENV')

#
# [FUNCTION] commentModalView
#
# [DESCRIPTION]
#  コメントを登録するためモーダルビューを表示するためのJSON構造を生成する
# 
# [INPUTS]
#  title - モーダル画面の見出し
#  text  - モーダル画面のテキスト
#  parameters - {country:<国名>, channel:<チャネルID>, user:<ユーザー名>}
# 
# [OUTPUTS]
#  JSON構造：{trigger_id:<ID>, {type:modal, title:<...>}}
#
def commentModalView(title, text, parameters):

  json_text = json.dumps(parameters) # JSONを文字列に変換する

  objView = {
    "type": "modal",
    "callback_id": "callback-put-comment", # 起動するコールバック関数
    "title": {
      "type": "plain_text",
      "text": title
    },
    "submit": {
      "type": "plain_text",
      "text": "登録"
    },
    "close": {
      "type": "plain_text",
      "text": "閉じる"
    },
    "private_metadata": json_text, # 国名、チャネル名、ユーザー名を保持する
    "blocks": [
		  {
			  "type": "input",
        "block_id": "comment_block",
			  "element": {
				  "type": "plain_text_input",
				  "action_id": "comment"
			  },
			  "label": {
				  "type": "plain_text",
				  "text": text
			  }
		  }
    ]
  }
 
  return objView

#
# [FUNCTION] commentInsert()
#
# [DESCRIPTION]
#  注釈をannotationレコードとして登録する
# 
# [INPUTS]
#  country  - 国名
#  datetime - 登録日時
#  user - ユーザー名
#  comment - 注釈
#
# [OUTPUTS]
#  成功: true
#  失敗: false
# 
# [NOTES]
#　'Côte d'Ivoire'と'Lao People's Democrat...のように国名にシングルクォートがある場合、「'」の前に「'」を付ける
#
def commentInsert(country, datetime, user, comment):
    retVal = False

    # 引数の存在チェック
    if country == None or datetime == None or user == None or comment == None:
      return retVal

    # 国名からID番号を取得する（小文字としてチェックする）
    country_id = None
    # シングルクォートを置換する
    dest = country.replace("'", "''")
    query = "SELECT id FROM countries WHERE LOWER(name_en)=LOWER('" + dest + "')"
    result = psqlGet(query)
    if result != None:
      #print(result)
      country_id = result[0][0] # 最初のタプルからCountry IDを取得
    else:
      return retVal

    # 注釈を登録する
    query = "INSERT INTO annotation (country_id,datetime,user_name,comment) VALUES (" + str(country_id) + ",'" + datetime + "','" + user + "','" + comment + "')"
    if pyEnv == 'development':
      print(query)
    psqlInsert(query)
    retVal = True
    
    return retVal

#
# [FUNCTION] commentGet()
#
# [DESCRIPTION]
#  指定した国の注釈を最新の順序で取得する
# 
# [INPUTS]
#  country - 国名
#
# [OUTPUTS]
#  {datetime:<日時>, comment:<注釈>}の配列
# 
# [NOTES]
#　'Côte d'Ivoire'と'Lao People's Democrat...のように国名にシングルクォートがある場合、「'」の前に「'」を付ける
#
def commentGet(country):

  if country == None:
    return None

  # シングルクォートを置換する
  dest = country.replace("'", "''")
  # countriesとannotationテーブルを結合して注釈を取得する
  query = "SELECT datetime, comment FROM annotation as a inner join countries as c ON LOWER(c.name_en)=LOWER('" + dest + "') AND a.country_id = c.id ORDER BY datetime DESC"
  result = psqlGet(query)
  
  return result

#
# END OF FILE
#