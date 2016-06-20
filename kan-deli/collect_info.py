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
REGS['title'] = u'headline_title">.*?<h2>(.*?)</h2>'
REGS['author'] = u'投稿者：(.*?)<span>.*?投稿レポ総数：(.*?)</span>'
REGS['store'] = u'店舗名：(.*?)</h3>'
REGS['time'] = u'<p class="date">(.*?)</p>'
REGS['look'] = u'ルックス</th><td>(.*?)</td>'
REGS['figure'] = u'スタイル</th><td>(.*?)</td>'
REGS['play'] = u'プレイ</th><td>(.*?)</td>'
REGS['total'] = u'総合評価</th><td>(.*?)</td>'
REGS['comment'] = u'<div id="gphoto">.*?<img src="./(.*?)".*?</div>(.*?)</div>'
REGS['g_age'] = u'推定年齢</th><td>(.*?)</td>'
REGS['g_height'] = u'推定身長</th><td>(.*?)</td>'
REGS['g_weight'] = u'推定体重</th><td>(.*?)</td>'
REGS['bodytype'] = u'体型</th><td>(.*?)</td>'
REGS['g_cup'] = u'推定カップ</th><td>(.*?)</td>'
REGS['under'] = u'アンダーヘア</th><td>(.*?)</td>'
REGS['jap'] = u'日本語のスキル</th><td>(.*?)</td>'
REGS['eng'] = u'英語のスキル</th><td>(.*?)</td>'
REGS['smoke'] = u'喫煙</th><td>(.*?)</td>'

class Comment(object):
    def __init__(self):
        self.title = ''
        self.author = ''
        self.store = ''
        self.time = ''
        self.look = ''
        self.figure = ''
        self.play = ''
        self.total = ''
        self.comment = ''
        self.g_age = ''
        self.g_height = ''
        self.g_weight = ''
        self.bodytype = ''
        self.g_cup = ''
        self.under = ''
        self.jap = ''
        self.eng = ''
        self.smoke = ''

    def __str__(self):
        attrs = ['%s: %s' % (x, getattr(self, x)) for x in self.__dict__.keys() if x[:1] != '_']
        return '\n'.join(attrs)

def download_pic(s, picurl):
    pic = s.get(picurl, stream=True)
    if not os.path.exists('data/%s' % view_id):
        os.makedirs('data/%s' % view_id)
    src = 'data/%s/%s' % (view_id, os.path.basename(picurl))
    with open(src, 'wb') as out_file:
        shutil.copyfileobj(pic.raw, out_file)
    del pic

view_id = sys.argv[1]

with requests.session() as s:
    ret01 = s.get(url01 % view_id)
    text = ret01.text
    
    if NOT_EXIST in text:
        print('[ERROR] view_id doesn\'t exixt')
    else:
        cmt = Comment()
        for key in REGS:
            m = re.search(REGS[key], text, re.DOTALL)
            if not m:
                continue
            if key == 'author':
                value = m.group(1).encode('utf-8').strip() + ' 総数：' + m.group(2).encode('utf-8').strip()
            elif key == 'comment':
                picurl = home + m.group(1)
                value = m.group(2).encode('utf-8').strip()
                download_pic(s, picurl)
            else:
                value = m.group(1).encode('utf-8').strip()
            setattr(cmt, key, value)
        print(cmt)
