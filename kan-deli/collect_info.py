#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import sys, os
import requests
import getpass
import shutil
import json
import time
import datetime
import re

if len(sys.argv)<2:
    print('Usage: view_id')
    exit(1)

home = 'http://www.kan-deli.net/'
url01 = 'http://www.kan-deli.net/view.php?view=%s'
NOT_EXIST = u'記事が存在しません'

REGS = {}
REGS['a0_title'] = u'headline_title">.*?<h2>(.*?)</h2>'
REGS['a1_author'] = u'投稿者：(.*?)<span>.*?投稿レポ総数：(.*?)</span>'
REGS['a2_store'] = u'店舗名：(.*?)</h3>'
REGS['a3_time'] = u'<p class="date">(.*?)</p>'
REGS['a4_look'] = u'ルックス</th><td>(.*?)</td>'
REGS['a5_figure'] = u'スタイル</th><td>(.*?)</td>'
REGS['a6_play'] = u'プレイ</th><td>(.*?)</td>'
REGS['a7_overall'] = u'総合評価</th><td>(.*?)</td>'
REGS['a8_comment'] = u'<div id="gphoto">.*?<img src="./(.*?)".*?</div>(.*?)</div>'
REGS['a9_g_age'] = u'推定年齢</th><td>(.*?)</td>'
REGS['b0_g_height'] = u'推定身長</th><td>(.*?)</td>'
REGS['b1_g_weight'] = u'推定体重</th><td>(.*?)</td>'
REGS['b2_bodytype'] = u'体型</th><td>(.*?)</td>'
REGS['b3_g_cup'] = u'推定カップ</th><td>(.*?)</td>'
REGS['b4_under'] = u'アンダーヘア</th><td>(.*?)</td>'
REGS['b5_jap'] = u'日本語のスキル</th><td>(.*?)</td>'
REGS['b6_eng'] = u'英語のスキル</th><td>(.*?)</td>'
REGS['b7_smoke'] = u'喫煙</th><td>(.*?)</td>'

class Comment(object):
    def __init__(self):
        self.a0_title = ''
        self.a1_author = ''
        self.a2_store = ''
        self.a3_time = ''
        self.a4_look = ''
        self.a5_figure = ''
        self.a6_play = ''
        self.a7_overall = ''
        self.a8_comment = ''
        self.a9_g_age = ''
        self.b0_g_height = ''
        self.b1_g_weight = ''
        self.b2_bodytype = ''
        self.b3_g_cup = ''
        self.b4_under = ''
        self.b5_jap = ''
        self.b6_eng = ''
        self.b7_smoke = ''

    def __str__(self):
        attrs = []
        keys = self.__dict__.keys()
        keys.sort()
        for x in keys:
            if x[:1] != '_':
                name = x[3:]
                now = '%s: %s' % (name, getattr(self, x))
                if name=='time' or name=='overall' or name=='comment':
                    now += '\n'
                attrs.append(now)
        return '\n'.join(attrs)

def download_pic(s, picurl):
    pic = s.get(picurl, stream=True)
    src = 'data/%s/%s' % (view_id, os.path.basename(picurl))
    with open(src, 'wb') as out_file:
        shutil.copyfileobj(pic.raw, out_file)
    del pic

view_id = sys.argv[1]

with requests.session() as s:
    ret01 = s.get(url01 % view_id)
    text = ret01.text
    
    if NOT_EXIST in text:
        print('[ERROR] view_id %s doesn\'t exixt' % view_id)
    else:
        if not os.path.exists('data/%s' % view_id):
            os.makedirs('data/%s' % view_id)
        fout = open('data/%s/%s.txt' % (view_id, view_id), 'w')
        cmt = Comment()
        for key in REGS:
            m = re.search(REGS[key], text, re.DOTALL)
            if not m:
                continue
            if 'author' in key:
                value = m.group(1).encode('utf-8').strip() + ' 総数：' + m.group(2).encode('utf-8').strip()
            elif 'comment' in key:
                picurl = home + m.group(1)
                value = m.group(2).encode('utf-8').strip()
                download_pic(s, picurl)
            else:
                value = m.group(1).encode('utf-8').strip()
            setattr(cmt, key, value)
        fout.write(str(cmt))
        fout.close()
