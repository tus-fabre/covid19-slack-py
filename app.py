#!/usr/bin/env python
# coding: utf-8
#
# [FILE] app.py
#
# [DESCRIPTION]
#  Lesson Final - Slack APIプログラミング (Python版)
#
# [NOTES]
#
import os
import sys
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from functions.covid19 import getCountryInfo, getCountries, translateCountryName
from functions.covid19_comment import commentModalView, commentInsert
from functions.covid19_csv import csvGenerateFile
from functions.covid19_chart import chartMonthlyConfiguration, chartWeeklyConfiguration
from functions.covid19_pdf import pdfGenerateFile
from functions.current_time import currentTime, currentHour

# Botトークンからアプリの初期化
app = None
bot_token = os.environ.get('SLACK_BOT_TOKEN')
if (bot_token == None):
    print("[環境変数未設定] SLACK_BOT_TOKEN")
else:
    app = App(token=bot_token)

if app == None:
    print('⚡️Boltアプリは起動できません')
    sys.exit()

# 仮のファイル保存フォルダー
local_folder = os.environ.get("LOCAL_FOLDER")
if (bot_token == None):
    print("[環境変数未設定] LOCAL_FOLDER")

pyEnv=os.environ.get('PY_ENV')
if pyEnv == 'development':
  print("開発モードで起動します")

print("アプリを起動します")
datetime = currentTime()
print("現在の時刻", datetime)

#
# ---------- Message Listeners ----------
#
 
#
# [MESSAGE LISTENER] hello
#
# [DESCRIPTION]
#  メッセージ'hello'を受け取ったときに起動する関数
# [INPUTS]
#  command - 利用しない
#
# [OUTPUTS]
#  respond - 'こんにちは <ユーザー名>!'
#
# [NOTE]
#  イベントがトリガーされたチャンネルに say() でメッセージを送信する
#
@app.message("hello")
def message_hello(message, say):
    # messageの内容を確認する
    if pyEnv == 'development':
        print(message)
    #メッセージを返信する
    say(f"こんにちは <@{message['user']}>!")

#
# [EVENT] message
#
# [DESCRIPTION]
#  次のメッセージを受信したときのリスナー関数
#   Unhandled request ({'type': 'event_callback', 'event': {'type': 'message', 'subtype': 'file_share'}})
#
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

#
# ---------- Slash Commands ----------
#

#
# [SLASH COMMAND] /hello
#
# [DESCRIPTION]
#  /helloで起動する関数。
#  現在時間（hour）に応じて、あいさつが異なる。
# 
# [INPUTS]
#  command - 利用しない
# 
# [OUTPUTS]
#  respond
#    現在時間が4以上10未満のとき、'おはよう <ユーザー名>!'
#    現在時間が10以上18未満のとき、'こんにちは <ユーザー名>!'
#    それ以外（現在時間が18以上23未満、0以上4未満）、'こんばんは <ユーザー名>!'
#    その後に今週の感染状況を折れ線グラフで表示する
# 
@app.command("/hello")
def command_hello(ack, command, respond):
    # 予め返信しておく
    ack()
    # commandの内容を確認する
    if pyEnv == 'development':
        print(command)
    # 現在時間を取得する
    hour = currentHour()
    # あいさつの初期値
    message = "こんばんは"
    if 4 <= hour and hour < 10:
        message = "おはよう"
    elif 10 <= hour and hour < 18:
        message = "こんにちは"
    message += "!\n"
    message += "今週の感染状況です"
    # コマンドに返答する
    respond(message)

    # 現在のSlackチャネルIDを取得する
    channel = command['channel_id']
    # 画像ファイルを生成し、アップロードする
    file_name = "simple-graph.png"
    file_path = local_folder + "/" + file_name
    try:
        status = chartWeeklyConfiguration(file_path)
        if status == True:
            result = app.client.files_upload(
                channels=channel, # Current Channel ID
                #title="Generated PNG File",
                file=file_path,
                initial_comment="画像ファイルを添付します",
            )
            os.remove(file_path)
            if pyEnv == 'development':
                print(result)
        else:
            respond(f'画像ファイルは作成できませんでした。')
    except Exception as e:
        print(e)
        respond(f'エラーが発生しました。')

#
# [SLASH COMMAND] /covid19
#
# [DESCRIPTION]
#  スラッシュコマンド/covid19のリスナー関数
#  指定した国（英語名）の一年の感染者実数と感染者予測結果をグラフで表現する
#
# [NOTES]
#
@app.command("/covid19")
def command_covid19(ack, command, respond):
    # 予め返信しておく
    ack()
    # commandの内容を確認する
    if pyEnv == 'development':
        print(command)
    # 対象とする国名を引数から取得する
    country = command['text']

    result = None
  # 引数が指定されていなければ、選択メニューから国名を選択する
    if country == '':
        result = getCountries()
    else: # 指定した国の感染状況を取得する
        result = getCountryInfo(country)

    # 開発モードのとき、出力の内容を表示する
    if pyEnv == 'development':
        print(result)
    # コマンドに返答する
    respond(result)

#
# [SLASH COMMAND] /translate
#
# [DESCRIPTION]
#  指定した国コードあるいは英語の国名を日本語に変換する
# 
# [INPUTS]
#  command.text - 対象となる国名
# 
# [OUTPUTS]
#  respond - JSON構造: {blocks:[<見出し>,<セクション>]}
# 
@app.command("/translate")
def command_translatge(ack, respond, command):
    # 予め返信しておく
    ack()
    # commandの内容を確認する
    if pyEnv == 'development':
        print(command)
    # 対象とする国名を引数から取得する
    country = command['text']
    # 出力構造の初期設定
    result = {
        #"type": "plain_text",
        "text": country + "は見つかりませんでした",
        #"emoji": True
    }
    # 国名を翻訳する
    translated = translateCountryName(country)
    if translated != None:
        result['text'] = "[入力した国名] " + country + " [日本語の国名] " + translated

    # 開発モードのとき、出力の内容を表示する
    if pyEnv == 'development':
        print(result)
    # コマンドに返答する
    respond(result)

#
# ---------- Actions ----------
#

#
# [ACTION METHOD] action-comment
#
# [DESCRIPTION]
#  注釈（コメント）をデータベースに登録するモーダルビューを表示するアクション
# 
# [INPUTS]
#  body.actions[0].value - 選択した国名
# 
# [OUTPUTS]
#  respond - JSON構造: {blocks:[<見出し>,<セクション>]}
#
@app.action("action-comment")
def action_comment(body, ack, client):
    # 予め返信しておく
    ack()

    # 対象とする国名、現在のチャネルID、ユーザー名をJSONとして保持する
    parameters = {}
    parameters['country'] = body['actions'][0]['value']
    parameters['channel'] = body['channel']['id']
    parameters['user'] = body['user']['username']
    message = parameters['country'] + "にコメントを追加します"

    # モーダルビュー向けJSON構造を生成する
    objModal = commentModalView("コメント登録", message, parameters)
    try:
        client.views_open(trigger_id=body['trigger_id'], view=objModal) # モーダルビューを開く
    except Exception as e:
        print(e)

#
# [ACTION METHOD] action-csv-generate
#
# [DESCRIPTION]
#  対象とする国の感染状況をCSVファイルに保存した後、ファイルをSlackにアップロードする
# 
# [INPUTS]
#  body.actions[0].value - ファイル生成対象とする国名
#  body.channel.id - 現在のSlackチャネルID
# 
# [OUTPUTS]
#  respond - ファイルアップロードに成功したか失敗したかのメッセージ
# 
@app.action('action-csv-generate')
def action_csv_generate(body, ack, respond):
    # 予め返信しておく
    ack()
    # 対象とする国名
    country = body['actions'][0]['value']
    # SlackチャネルIDを取得する
    channel = body['channel']['id']
    respond('ファイルを作成中です...')

    # 国名を選択するメニューを構成する
    result = getCountryInfo(country)
    if pyEnv == 'development':
        print(result)
    respond(result)

    # CSVファイルを生成する
    csv_file = csvGenerateFile(country)
    message = ''
    if csv_file != None:
        try:
            result = app.client.files_upload(
                channels=channel, # Current Channel ID
                #title="Generated CSV File",
                file=csv_file,
                initial_comment="CSVファイルを添付します",
            )
            os.remove(csv_file)
            if pyEnv == 'development':
                print(result)
        except Exception as e:
            print(e)
            message = 'ファイルをアップロードできません。'
    else:
        message = 'ファイルを作成できません。'

    # エラーメッセージがあれば返答する
    if message != '':
        respond(message)


#
# [ACTION METHOD] action-get-countries
#
# [DESCRIPTION]
#  国名を選択するメニューを表示するアクション
# 
# [INPUTS]
#  body.actions[0].value - 選択した国名、しかし利用しない
# 
# [OUTPUTS]
#  respond - JSON構造: {blocks:[<見出し>,<セクション>]}
#
@app.action('action-get-countries')
def action_get_countries(body, ack, respond):
    # 予め返信しておく
    ack()
    # 選択した国名
    country = body['actions'][0]['value']
    # 国名を選択するメニューを構成する
    result = getCountries()
    # 開発モードのとき、出力の内容を表示する
    if pyEnv == 'development':
        print(result)
    # アクションに返答する
    respond(result)

#
# [ACTION METHOD] action-get-info
#
# [DESCRIPTION]
#  新型コロナウィルス感染状況をSlack画面上で再表示するアクション
#  「再表示」ボタンから起動される
# 
# [INPUTS]
#  body.actions[0].value - 選択した国名
# 
# [OUTPUTS]
#  respond - JSON構造: {blocks:[<見出し>,<セクション>]}
#
@app.action('action-get-info')
def action_get_info(body, ack, respond):
    # 予め返信しておく
    ack()
    # 選択した国名
    country = body['actions'][0]['value']
    # 国名を選択するメニューを構成する
    result = getCountryInfo(country)
    # 開発モードのとき、出力の内容を表示する
    if pyEnv == 'development':
        print(result)
    # アクションに返答する
    respond(result)

#
# [ACTION METHOD] action-get-info-all
#
# [DESCRIPTION]
#  全世界の新型コロナウィルス感染状況をSlack画面上で表示するアクション
#  「全世界」ボタンから起動される
# 
# [INPUTS]
#  body.actions[0].value - all
# 
# [OUTPUTS]
#  respond - JSON構造: {blocks:[<見出し>,<セクション>]}
#
@app.action('action-get-info-all')
def action_get_info_all(body, ack, respond):
    # 予め返信しておく
    ack()
    # 選択した国名
    country = body['actions'][0]['value']
    # 選択した国の感染状況を取得する
    result = getCountryInfo(country)
    # 開発モードのとき、出力の内容を表示する
    if pyEnv == 'development':
        print(result)
    # アクションに返答する
    respond(result)

#
# [ACTION METHOD] action-graph-history
#
# [DESCRIPTION]
#  30日間の新型コロナウィルス新規感染者数を棒グラフ、死亡者数を折れ線グラフで表示する画像を作成する
# 
# [INPUTS]
#  body.actions[0].value - 選択した国名
#  body.channel.id - 現在のSlackチャネルID
# 
# [OUTPUTS]
#  respond - getCountryInfo()からのJSON構造（国名選択に戻る）
# 
@app.action('action-graph-history')
def action_graph_history(body, ack, respond):
    # 予め返信しておく
    ack()
    # 選択した国名
    country = body['actions'][0]['value']
    # 現在のSlackチャネルIDを取得する
    channel = body['channel']['id']
    respond('グラフを作成中です...')

    # 国名を選択するメニューを構成する
    result = getCountryInfo(country)
    if pyEnv == 'development':
        print(result)
    respond(result)

    # 画像ファイルを生成し、アップロードする
    file_name = country + ".png"
    file_path = local_folder + "/" + file_name
    try:
        status = chartMonthlyConfiguration(country, file_path)
        if status == True:
            result = app.client.files_upload(
                channels=channel, # Current Channel ID
                #title="Generated PNG File",
                file=file_path,
                initial_comment="画像ファイルを添付します",
            )
            os.remove(file_path)
            if pyEnv == 'development':
                print(result)
        else:
            respond(f'画像ファイルは作成できませんでした。')
    except Exception as e:
        print(e)
        respond(f'エラーが発生しました。')

#
# [ACTION METHOD] action-report-history
#
# [DESCRIPTION]
#  新型コロナウィルスの感染状況をPDFファイルで表示する
# 
# [INPUTS]
#  body.actions[0].value - 選択した国名
#  body.channel.id - 現在のSlackチャネルID
# 
# [OUTPUTS]
#  respond - getCountryInfo()からのJSON構造（国名選択に戻る）
# 
@app.action('action-report-history')
def action_report_history(body, ack, respond):
    # 予め返信しておく
    ack()
    # 選択した国名
    country = body['actions'][0]['value']
    # 現在のSlackチャネルIDを取得する
    channel = body['channel']['id']
    respond('レポートを作成中です...')

    # 国名を選択するメニューを構成する
    result = getCountryInfo(country)
    if pyEnv == 'development':
        print(result)
    respond(result)

    # 画像ファイルを生成し、アップロードする
    file_name = country + ".png"
    png_file = local_folder + "/" + file_name
    try:
        status = chartMonthlyConfiguration(country, png_file)
        if status == True:
            now = currentTime()
            pdf_file = pdfGenerateFile(now, country, png_file)
            if pdf_file != None:
                result = app.client.files_upload(
                    channels=channel, # Current Channel ID
                    #title="Generated PDF File",
                    file=pdf_file,
                    initial_comment="PDFファイルを添付します",
                )
                os.remove(pdf_file)
            else:
                respond(f'PDFファイルは作成できませんでした。')
            os.remove(png_file)
        else:
            respond(f'画像ファイルは作成できませんでした。')
    except Exception as e:
        print(e)
        respond(f'エラーが発生しました。')

#
# [ACTION METHOD] action-select-country
#
# [DESCRIPTION]
#  選択メニューから選択した国名から新型コロナウィルス感染状況をSlack画面上に表示するアクション
# 
# [INPUTS]
#  body.actions[0].selected_option.value - 選択した国名
# 
# [OUTPUTS]
#  respond - JSON構造: {blocks:[<見出し>,<セクション>]}
#
@app.action('action-select-country')
def action_select_country(body, ack, respond):
    # 予め返信しておく
    ack()
    # 対象とする国名を選択項目から取得する
    country = body['actions'][0]['selected_option']['value']
    # 選択した国の感染状況を取得する
    result = getCountryInfo(country)
    # 開発モードのとき、出力の内容を表示する
    if pyEnv == 'development':
        print(result)
    # アクションに返答する
    respond(result)

#
# ---------- Callback Functions for Views ----------
#

#
# [ACTION METHOD] callback-put-comment
#
# [DESCRIPTION]
#  注釈レコードを登録するコールバック関数
# 
# [INPUTS]
#  view.state.values.comment_block.comment.value - コメント
#  view.private_metadata - {country:<国名>, channel:<チャネルID>, user:<ユーザー名>}
# 
# [OUTPUTS] なし
#
@app.view('callback-put-comment')
def callback_put_comment(ack, view, client):
    # 予め返信しておく
    ack()
    # private_metadataからJSON文字列を取得する
    json_text = view['private_metadata']
    # 文字列をJSONに変換する
    parameters = json.loads(json_text)
    # コメントを取得する
    comment = view['state']['values']['comment_block']['comment']['value']

    now = currentTime() # 現在の時刻
    # 注釈をデータベースに登録する
    status = commentInsert(parameters['country'], now, parameters['user'], comment)

    msg = parameters['country'] + "へコメントが登録"
    if status == True:
        msg += "されました"
    else:
        msg += "できませんでした"

    try:
        result = client.chat_postMessage(
            channel=parameters['channel'], # Slachコマンドを起動したチャネルID
            text=msg
        )
        if pyEnv == 'development':
            print(result)
    except Exception as e:
        print(e)

#
# サーバーを起動する
#
if __name__ == "__main__":

    app_token = os.environ["SLACK_APP_TOKEN"]
    if app_token == None:
        print("[環境変数未設定] SLACK_APP_TOKEN")
        print('⚡️Boltアプリは起動できません')
    else:
        print('⚡️Boltアプリが起動しました')
        SocketModeHandler(app, app_token).start()

#
# END OF FILE
#