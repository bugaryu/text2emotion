# Import the modules
import csv
from email import header
import re
from fileinput import filename
from tkinter.tix import Tree
import text2emotion as te
# print(te.__file__)

# Pandasをインポート
import pandas as pd
import json
# from pandas.io.json import json_normalize

import deepl


def translate(text):

    auth_key = "7616ab4c-0a79-0d00-cd56-1747f4689a4a:fx"  # Replace with your key
    translator = deepl.Translator(auth_key)

    result = translator.translate_text(text, target_lang="EN-US")
    # print(result.text)  # "Bonjour, le monde !"
    return result


def get_split_text(filename="tanizaki.txt"):
    """
    改行区切りで文字を取得
    """

    f = open(filename, 'r', encoding='shift_jis')
    text = f.read()
    # print(text)
    formatted_text = text_formatt(text)
    sentences = formatted_text.split('\n')
    f.close()
    return sentences


# ファイル整形


def text_formatt(text):
    """
    テキストの事前処理
    """

    # タイトルの保持
    title = re.split('\-{5,}', text)[0]
    words = re.split('\n', text)
    title = '『' + words[0] + '』' + words[1]

    # ヘッダ部分の除去
    text = title + re.split('\-{5,}', text)[2]
    # フッタ部分の除去
    text = re.split('底本：', text)[0]
    # | の除去
    text = text.replace('｜', '')
    # ルビの削除
    text = re.sub('《.+?》', '', text)
    # 入力注の削除
    text = re.sub('［＃.+?］', '', text)

    # 題名の削除
    text = re.sub('[一二三四五六七八九]、.+\n\n', '', text)
    text = re.sub('\n[一二三四五六七八九〇]+\n', '', text)

    # 空行の削除
    text = re.sub('\n\n', '\n', text)
    text = re.sub('\r', '', text)
    # text = re.sub('\n', '', text)

    # 全角スペースを削除する
    text = re.sub(r'\u3000', '', text)

    # ！？で改行する
    text = re.sub('！', '！\n', text)
    # text = re.sub('？', '？\n', text)

    # カッコで改行する
    # text = re.sub('「', '\n「', text)
    # text = re.sub('」', '」\n', text)

    # 「。」で改行する
    text = re.sub('。', '。\n', text)
    text = re.sub('\n\n', '\n', text)
    return text


def get_text_block(text):
    """
    3文区切りでまとめた文章を生成
    """
    DIVISION_CNT = 5

    sentences = ''
    text_block = []

    strCount = 0
    isDialogue = False

    for i, sentence in enumerate(text):
        sentence.strip()

        if sentence == '':
            continue
        elif '「' in sentence or '（' in sentence:
            isDialogue = True
            strCount = 0

            # カッコは一区切り
            if len(sentences) > 0:
                text_block.append(sentences.strip())
                sentences = ''

        sentences += '\n' + sentence

        if isDialogue:
            if '」' in sentence or '）' in sentence:
                isDialogue = False
                strCount = 3

                sentences = re.sub('\n', '', sentences)
                parts = sentences.split('」')

                # 閉じカッコの後が"と〜"で続く場合は結合する
                if len(parts) > 1 and len(parts[1]) > 0 and parts[1][0] != 'と':
                    text_block.append(parts[0].strip() + '」')
                    sentences = parts[1]
                    strCount = 1
        else:
            strCount += 1

        if strCount >= DIVISION_CNT:
            text_block.append(sentences.strip())
            sentences = ''
            strCount = 0

    if sentences != '':
        text_block.append(sentences.strip())

    return text_block


def get_emotion(text):
    # print("\n===== text =====")
    # print(data)

    # Call to the function
    emotion = te.get_emotion(text)

    # print("===== emotion =====")
    # print(emotion)
    # print("===================")
    return emotion


def open_csv(filename, title):
    """
    csvをオープンし、ヘッダーを書き込む
    """
    with open(out_filename, 'w') as f:
        writer = csv.writer(f)
        # writer.writerow(['t','en'].extend(get_emotion('').keys()))

        header = {title: '',
                  'En_text': ''}
        header.update(get_emotion(''))

        writer.writerow(header)


def export_to_csv(data, filename='out.csv'):
    # CSV書き込み
    # df = pd.read_json('target.json')
    # print(df)

    # read_jsonした結果だとネストしたjsonを展開できないのでnormalizeで展開させる
    # df_json = json_normalize(df['data'])
    df_json = pd.json_normalize(data)
    df_json.to_csv('csv/' + filename, encoding='utf-8')


def update_to_csv(data, filename='out.csv'):
    with open(filename, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        writer.writerow(data)


# file_name = 'tanizaki.txt'
inputPath = 'novel_text/'
# file_name = 'hashire_merosu.txt'
# file_name = 'gingatetsudono_yoru.txt'
file_name = 'sanshiro.txt'

print('\n==========')
print('File name: ' + file_name)

out_filename = 'csv/out_' + file_name.split('.')[0] + '.csv'


splitText = get_split_text(inputPath + file_name)
title = splitText.pop(0)
sentences = get_text_block(splitText)

data_list = []

open_csv(out_filename, title)

print('Number of lines: ' + str(len(sentences)))
print('lodaing')

for sentence in sentences:
    print('.', end="")
    if sentence == '':
        continue

    # sentence_en = sentence
    sentence_en = translate(sentence).text
    data = {"text": sentence,
            "en_text": sentence_en}
    emotion = get_emotion(sentence_en)
    data.update(emotion)
    # data_list.append(data)
    # 一行書き出し
    update_to_csv(data, out_filename)


# export_to_csv(data_list, out_filename)
print('\nOut file name: ' + out_filename)
print('finish export!!!')
print('==========')
