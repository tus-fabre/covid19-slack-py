#!/usr/bin/env python
# coding: utf-8
#
# [FILE] current_time.js
#
# [DESCRIPTION]
#  現在の時刻を表示する関数を定義するファイル
# 
# [NOTES]
#
import datetime

#
# [FUNCTION] currentTime()
#
# [DESCRIPTION]
#  現在の時刻を表示する関数
# 
# [INPUTS] なし
# 
# [OUTPUTS]
#  YYYY-MM-DD HH24:MI:SS
# 
# [NOTES]
#
def currentTime():
    dt = datetime.datetime.now()
    formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
    return formatted

#
# [FUNCTION] currentTimeStamp()
#
# [DESCRIPTION]
#  現在のタイムスタンプを表示する関数
# 
# [INPUTS] なし
# 
# [OUTPUTS]
#  YYYYMMDDHH24MISS
# 
# [NOTES]
#
def currentTimeStamp():
    dt = datetime.datetime.now()
    formatted = dt.strftime("%Y%m%d%H%M%S")
    return formatted

#
# [FUNCTION] currentHour()
#
# [DESCRIPTION]
#  現在の時間(hour)を取得する関数
# 
# [INPUTS] なし
# 
# [OUTPUTS]
#  現在の時間：0 ～ 24
# 
# [NOTES]
#
def currentHour():
    dt = datetime.datetime.now()
    hour = dt.hour
    
    return hour


#
# END OF FILE
#