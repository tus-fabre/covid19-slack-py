#!/usr/bin/env python
# coding: utf-8
#
# [FILE] psql_get.js
#
# [DESCRIPTION]
#  PostgreSQLにアクセスして値を取得する関数を定義するファイル
#  環境変数DB_URLが定義されていない場合、すべての関数はNoneを返却する。
#
import os
import psycopg2
import urllib.parse
from dotenv import load_dotenv
load_dotenv()

# データベース接続先を取得
dbUrl = os.environ.get('DB_URL')

#
# [FUNCTION] getConnection()
#
# [DESCRIPTION]
#  環境変数DB_URLの内容をパーズして、PostgreSQLに接続する
# 
# [INPUTS] なし
# 
# [OUTPUTS] 
#  Connectionオブジェクト
# 
# [NOTES]
#
def getConnection():
  if (dbUrl == None):
    return None

  urllib.parse.uses_netloc.append("postgres")
  url = urllib.parse.urlparse(dbUrl)
  conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
  )
  return conn
  
#
# [FUNCTION] psqlGet()
#
# [DESCRIPTION]
#  指定したSQL文を実行して、その結果をJSON構造で取得する
# 
# [INPUTS]
#  query - 実行するSQL文
# 
# [OUTPUTS] 
#  対象となるSQL文に応じたJSON構造（リスト）が返る。
#  失敗したら、Noneを返す。
# 
# [NOTES]
#
def psqlGet(query):
  results = None

  if (dbUrl == None):
    return results
  
  try:
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(query)
  except psycopg2.Error as e:
    print("[DATABASE ERROR]")
    print(format(e))
  else:
    results = cur.fetchall()
    cur.close()
    conn.close()

  return results

#
# [FUNCTION] psqlInsert()
#
# [DESCRIPTION]
#  指定したINSERT文を実行して、レコードを登録する
# 
# [INPUTS]
#  query - 実行するSQL文
# 
# [OUTPUTS] なし
# 
# [NOTES]
#
def psqlInsert(query):

  if (dbUrl == None):
    return
  
  try:
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(query)
    cur.close()
    conn.commit()
    conn.close()
  except Exception as e:
    print(format(e))

#
# END OF FILE
#