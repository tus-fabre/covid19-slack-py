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
#
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
#
def httpGet(url):
    data = None

    try:
        result = requests.get(url)
    except requests.exceptions.ConnectTimeout:
        print("[TIMEOUT]", url)
    else:
        if result.status_code == 200:
            data = result.json() # JSONに変換する
        else:
            print("[STATUS CODE]", result.status_code)

    return data

#
# END OF FILE
#