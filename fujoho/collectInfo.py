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
from time import gmtime, strftime

if len(sys.argv)<1:
    print('Usage: auto script')
    exit(1)

ShopPsize = 100
GirlPsize = 100
CmtPsize = 50
ReplyPsize = 20

home = "http://fujoho.jp/index.php?"
shopList = "http://fujoho.jp/index.php?p=shop_list&t=13&b=%d"
cmtList = "http://fujoho.jp/index.php?p=shop_repo_list&id=%s"

REGS = {}
REGS['getNum1'] = u'(\d+)件'
REGS['getNum2'] = u'(\d+)人'
REGS['girlList'] = "(p=shop_girl_list&id=(\d+))"
REGS['girlLink'] = "(p=girl&id=(\d+))"
REGS['girlPic'] = "<td><img src=\"(http://img.fujoho.jp/public/img_girl/.*?.jpg)\" class=\"girl-sub-img\""
REGS['cmtLink'] = "(p=report&id=(\d+))"
REGS['replyList'] = "(p=report_ouen&id=(\d+))"

def downloadPic(s, picurl, dir):
    # log(picurl)
    pic = s.get(picurl, stream=True)
    src = '%s/%s' % (dir, os.path.basename(picurl))
    with open(src, 'wb') as out_file:
        shutil.copyfileobj(pic.raw, out_file)
    del pic

def log(msg):
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print("%s %s" % (time, str(msg)))


with requests.session() as s:
    shopPages = 1
    shopP = 0
    while shopP<shopPages:
        ret0 = s.get(shopList % shopP)
        text = ret0.text
        shopPages = int((int(re.findall(REGS['getNum1'], text)[0])-1)/ShopPsize)+1
        log("now in shoppage %d/%d" % (shopP+1, shopPages))
        girlLists = re.findall(REGS['girlList'], text)
        for (girls, shopId) in girlLists:
            if not os.path.exists('data/%s' % shopId):
                os.makedirs('data/%s' % shopId)
            girlPages = 1
            gp = 0
            while gp<girlPages:
                text1 = s.get((home+girls+"&b=%d") % gp).text
                numGirls = int(re.findall(REGS['getNum2'], text1)[0])
                girlPages = int((numGirls-1)/GirlPsize)+1
                if gp == 0:
                    log("%d girls in shop %s" % (numGirls, shopId))
                girlsInPage = re.findall(REGS['girlLink'], text1)
                for (girlLink, girlId) in girlsInPage:
                    girlDir = 'data/%s/girl_%s' % (shopId, girlId)
                    if not os.path.exists(girlDir):
                      os.makedirs(girlDir)
                      
                    textG = s.get(home+girlLink).text
                    pics = re.findall(REGS['girlPic'], textG)
                    for pic in pics:
                        downloadPic(s, pic, girlDir)
                    fout = open("%s/%s.html" % (girlDir, girlId), 'w')
                    fout.write(textG)
                    fout.close()
                gp += 1
        shopP += 1


