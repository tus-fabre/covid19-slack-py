#!/usr/bin/env python
# coding: utf-8
#
# [FILE] covid19_pdf.py
#
# [DESCRIPTION]
#  新型コロナウィルスの感染状況をPDFファイルとして出力する関数を定義するファイル
#  Pythonのreportlabを用いる
#
import os
from .http_get import httpGet
from .covid19 import translateCountryName
from .covid19_comment import commentGet
from functions.current_time import currentTimeStamp

# reportlabモジュール
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase.ttfonts import TTFont

from dotenv import load_dotenv
load_dotenv()

BASE_URL=os.environ.get("BASE_URL")
LOCAL_FOLDER = os.environ.get("LOCAL_FOLDER")
FONT_FILE = './fonts/ipaexg.ttf'
FONT_NAME = 'IPAexGothic'

#
# [FUNCTION] pdfGenerateFile()
#
# [DESCRIPTION]
#  新型コロナウィルスの感染状況の内容をPDFドキュメントファイルとして作成する
# 
# [INPUTS]
#  datetime - 日時
#  country - 対象となる国名
#  image_file - PDFファイルに追加する画像ファイル
# 
# [OUTPUTS]
#  成功: 作成されたPDFファイル名
#  失敗: null
# 
# [NOTES]
#  アクセスするURL:
#   https://disease.sh/v3/covid-19/countries/<Country>
#   countryが'all'の場合
#   https://disease.sh/v3/covid-19/all
#
# '{:,}'.format() は数値を三桁区切りにする。
#
def pdfGenerateFile(datetime, country, image_file):
  output_file = None
  if image_file == '':
    return output_file

  url = BASE_URL + "countries/" + country
  if country == 'all':
    url = BASE_URL + "all"

  result = httpGet(url)
  if result != None:
    # PDFファイルを生成する
    timestamp = currentTimeStamp()
    output_file = LOCAL_FOLDER + "/Report-" + country + "-" + str(timestamp) + ".pdf"
    pdf = canvas.Canvas(output_file, pagesize=portrait(A4), bottomup=True) # PDFを生成, サイズはA4, 左上が0.0
    pdf.saveState() # セーブ
  
    # ファイル情報を設定する
    pdf.setAuthor('TUS')
    pdf.setTitle('新型コロナウイルス感染状況レポート')
    pdf.setSubject('新型コロナウイルス感染状況レポート')

    #フォント、サイズを設定
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
    pdf.setFont(FONT_NAME, 24)

    width, height = A4  # A4用紙のサイズ
    
    # 大見出しを表示
    pdf.drawCentredString(width/2, height - 2*cm, 'COVID-19 レポート')

    # 作成日時を表示
    pdf.setFont(FONT_NAME, 16)
    pdf.drawString(10*cm, height - 3*cm, '作成時刻: ' + datetime)

    # 対象国の情報を表として定義する
    translated = translateCountryName(country) #日本語国名へ変換
    if translated == None:
      translated = country
  
    population = '{:,}'.format(int(result['population'])) #人口
    info_elements = [['国名', '人口'],[translated, population]]
    info_table = Table(info_elements)
    info_table.setStyle(TableStyle([
      ('FONT', (0, 0), (-1, -1), FONT_NAME, 14),
      ('BOX', (0, 0), (-1, -1), 1, colors.black),
      ('TEXTCOLOR',(0, 0),(1, -1), colors.black),
      # 四角の内側に格子状の罫線を引いて、0.25の太さ
      ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
      # セルの縦文字位置を、TOP/MIDDLE/BOTTOMにする
      ('VALIGN', (0, 0), (-1, -1), 'TOP'),
      ('BACKGROUND', (0, 0), (1, 0), '#eeeeff'),
      ]))
    # tableを描き出す位置を指定
    info_table.wrapOn(pdf, 20*mm, height - 50*mm)
    info_table.drawOn(pdf, 20*mm, height - 50*mm)

    # 感染状況を表示する
    pdf.setFont(FONT_NAME, 20)
    pdf.drawString(1*cm, height - 60*mm, '感染状況：')
    
    active    = '{:,}'.format(int(result['active']))    # 感染者数
    critical  = '{:,}'.format(int(result['critical']))  # 重病者数
    recovered = '{:,}'.format(int(result['recovered'])) # 退院・療養終了
    cases     = '{:,}'.format(int(result['cases']))     # 感染者累計
    deaths    = '{:,}'.format(int(result['deaths']))    # 死亡者累計
    tests     = '{:,}'.format(int(result['tests']))     # 検査数

    status_elements = [['感染者数', active],
      ['重病者数', critical],
      ['退院・療養終了', recovered],
      ['感染者累計', cases],
      ['死亡者累計', deaths],
      ['検査数', tests]]
    status_table = Table(status_elements)
    status_table.setStyle(TableStyle([
      ('FONT', (0, 0), (-1, -1), FONT_NAME, 14),
      ('BOX', (0, 0), (-1, -1), 1, colors.black),
      ('TEXTCOLOR',(0, 0),(1, -1), colors.black),
      # 四角の内側に格子状の罫線を引いて、0.25の太さ
      ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
      # セルの縦文字位置を、TOP/MIDDLE/BOTTOMにする
      ('VALIGN', (0, 0), (-1, -1), 'TOP'),
      ('BACKGROUND', (0, 0), (0, 5), '#eeeeff'),
    ]))
    # tableを描き出す位置を指定
    status_table.wrapOn(pdf, 20*mm, height - 115*mm)
    status_table.drawOn(pdf, 20*mm, height - 115*mm)

    # 感染履歴グラフを表示
    if image_file != None:
      pdf.setFont(FONT_NAME, 20)
      pdf.drawString(10*mm, height - 125*mm, '感染履歴グラフ： ')
      # 画像を添付する: 1000pt x 800pt
      pdf.drawInlineImage(image_file, 10*mm, 10*mm, 200*mm, 160*mm) 
    
    # 注釈があれば表示する
    comments = commentGet(country)
    if comments != None and len(comments) > 0:
      pdf.showPage() # 改ページ
      pdf.setFont(FONT_NAME, 20)
      pdf.drawString(10*mm, height - 2*cm, 'コメント: ')

      comment_elements = [['日時', 'コメント']]
      for i in range(len(comments)):
        dt = comments[i][0] # comments[0]は(日時, コメント)のタプルから構成される
        formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
        comment_elements.append([formatted, comments[i][1]]) # [日時, 注釈]
        
      comment_table = Table(comment_elements, colWidths=(50*mm, 140*mm,), rowHeights=8*mm)
      comment_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), FONT_NAME, 12),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TEXTCOLOR',(0, 0),(1, -1), colors.black),
        #四角の内側に格子状の罫線を引いて、0.25の太さ
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        # セルの縦文字位置を、TOP/MIDDLE/BOTTOMにする
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (1, 0), '#eeeeff'),
      ]))
      # tableを描き出す位置を指定
      y_pos = len(comments) * 8 + 30 # 30 means margin (mm)
      comment_table.wrapOn(pdf, 10*mm, height - y_pos*mm)
      comment_table.drawOn(pdf, 10*mm, height - y_pos*mm)

    # ドキュメントの内容をPDFファイルとして出力する
    pdf.save()
    print("[INFO] ", output_file, 'has been saved.')

  return output_file

#
# END OF FILE
#