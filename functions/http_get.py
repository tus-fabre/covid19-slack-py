#!/usr/bin/env python
# coding: utf-8
#
#
# [FILE] http_get.js
#
# [DESCRIPTION]
#  HTTP URLにアクセスして値を取得する関数を定義するファイル
# 
# [NOTE]
# 
#/
import requests

#
# [FUNCTION] httpGet()
#
# [DESCRIPTION]
#  Access an HTTP URL to get a JSON value
# 
# [INPUTS]
#  url - 対象となるURL
# 
# [OUTPUTS]
#  対象となるURLに応じたJSON構造が返る。
#  失敗したら、Noneを返す。
# 
# [NOTE]
# 
#/
def httpGet(url):
    data = None

    try:
        result = requests.get(url)
        if result.status_code == 200:
            data = result.json() # JSONに変換する
            #print(data)
    except Exception as e:
        print(e)

    return data

#
# END OF FILE
#