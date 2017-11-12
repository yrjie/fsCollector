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
replyList = "http://fujoho.jp/index.php?p=report_ouen&id=%s"

REGS = {}
REGS['getNum1'] = u'(\d+)件'
REGS['getNum2'] = u'(\d+)人'
REGS['getNum3'] = u'この口コミへの応援コメント<span>（(\d+)件'
REGS['girlList'] = "(p=shop_girl_list&id=(\d+))"
REGS['girlLink'] = "(p=girl&id=(\d+))"
REGS['girlPic'] = "<td><img src=\"(http://img.fujoho.jp/public/img_girl/.*?.jpg)\" class=\"girl-sub-img\""
REGS['cmtLink'] = "(p=report&id=(\d+))"


def writeHTML(text, fname):
    fout = open(fname, 'w')
    fout.write(text)
    fout.close()

def downloadPic(s, picurl, dir):
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
            shopDir = 'data/%s' % shopId
            if not os.path.exists(shopDir):
                os.makedirs(shopDir)
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
                    girlDir = '%s/girl_%s' % (shopDir, girlId)
                    if not os.path.exists(girlDir):
                      os.makedirs(girlDir)

                    textG = s.get(home+girlLink).text
                    pics = re.findall(REGS['girlPic'], textG)
                    for pic in pics:
                        downloadPic(s, pic, girlDir)
                    writeHTML(textG, "%s/%s.html" % (girlDir, girlId))
                gp += 1

            cmtPages = 1
            cp = 0
            while cp<cmtPages:
                cLink = (cmtList+"&b=%d") % (shopId, cp)
                text1 = s.get(cLink).text
                numCmts = int(re.findall(REGS['getNum1'], text1)[0])
                cmtPages = int((numCmts-1)/CmtPsize)+1
                if cp == 0:
                    log("%d comments in shop %s" % (numCmts, shopId))
                cmtsInPage = re.findall(REGS['cmtLink'], text1)
                for (cmtLink, cmtId) in cmtsInPage:
                    textC = s.get(home+cmtLink).text
                    writeHTML(textC, "%s/%s.html" % (shopDir, cmtId))
                    temp1 = re.findall(REGS['getNum3'], textC)
                    if len(temp1)>0:
                        numReply = int(temp1[0])
                    else:
                        numReply = 0
                    log("%d replies in comment %s" % (numReply, cmtId))
                    if numReply>0:
                        replyPages = int((numReply-1)/ReplyPsize)+1
                        rp = 0
                        while rp<replyPages:
                            textR = s.get((home+replyList+"&b=%d") % (cmtId, rp)).text
                            writeHTML(textR, "%s/%s_%d.html" % (shopDir, cmtId, rp))
                            rp += 1
                cp += 1
        shopP += 1


