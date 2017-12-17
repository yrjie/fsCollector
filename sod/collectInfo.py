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


if len(sys.argv)<2:
    print('Usage: autoscript')
    exit(1)


allAreas = ["/area/chiba",
"/area/ginza",
"/area/gotanda",
"/area/higashi-tokyo",
"/area/ikebukuro",
"/area/kanagawa",
"/area/kawasaki",
"/area/nishi-tokyo",
"/area/saitama",
"/area/shibuya",
"/area/shinjuku",
"/area/ueno",
"/area/yokohama",
"/area/yoshiwara"]

homeUrl = "https://fuzoku.sod.co.jp"


def log(msg):
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print("%s %s" % (time, str(msg)))


visitedListFile = "vis.txt"
fvis = open(visitedListFile)
visited = set([x.strip() for x in fvis.readlines()])
log("%d shops visited" % len(visited))
fvis.close()

fvisW = open(visitedListFile, "a")


REGS = {}
REGS['getPageNum'] = u'page='
REGS['getShopUrl'] = u'<div class="rank_item__headbox__shop_name"><a href="(.*?)">'
REGS['shopName'] = u'<title>(.*?) \|'
REGS['allCmts'] = '<dl class="commentList">(.*?)</dl>'
REGS['singleCmt'] = '<dd>(.*?)</dd>'
REGS['reportLink'] = 'girl-info__name girls-list__profile__name"><a href="(.*?)">'
REGS['girlId'] = '<a href="/girls/himelog_detail/(.*?)">'
REGS['nameAge'] = '<p class="girl-info__name name">(.*?) <span class="girl-info__age">\((.*?)\)</span></p>'
REGS['figure'] = '<p class="health">(.*?) </p>'
REGS['CP'] = u'点数<span>(.*?)</span>'
REGS['looks'] = u'ルックス点</span><p class="girls-rank-star__star(.*?)">'
REGS['pose'] = u'接客姿勢点数</span><p class="girls-rank-star__star(.*?)">'
REGS['tech'] = u'テクニック総合点</span><p class="girls-rank-star__star(.*?)">'
REGS['sm'] = u'女性のSM度 M度</span><p class="girls-rank-star__smstar(.*?)">'
REGS['reportContent'] = '<section class="sectionInner">(.*?)</section>'
REGS['img'] = '<img class="tmb" src="(.*?)"'


def writeHTML(text, fname):
    fout = open(fname, 'w')
    fout.write(text)
    fout.close()

def downloadPic(s, picurl, dir, filename=""):
    pic = s.get(picurl, stream=True)
    if not filename:
      filename = os.path.basename(picurl)
    src = '%s/%s' % (dir, filename)
    with open(src, 'wb') as out_file:
        shutil.copyfileobj(pic.raw, out_file)
    del pic

def headOrElse(arr, default):
  if len(arr)==0:
    return default
  else:
    return arr[0]

with requests.session() as s:
    for ar in allAreas:
      areaHome = homeUrl+ar
      temp = s.get(areaHome).text
      numPage = len(re.findall(REGS['getPageNum'], temp))
      for p in range(1, 1+numPage):
        areaP = s.get(areaHome+"?page="+str(p)).text
        shopsUrl = re.findall(REGS['getShopUrl'], areaP)
        for su in shopsUrl:
          temp = [x for x in su.split("/") if x]
          shopId = temp[-1]
          if shopId in visited:
            log("shop %s visited, skipped" % shopId)
            continue
          shopPage = s.get("%s/%s" % (homeUrl, su)).text
          shopDir = 'data/%s' % shopId
          shopInfoFile = '%s/shop_%s.txt' % (shopDir, shopId)
          if not os.path.exists(shopDir):
            os.makedirs(shopDir)
          shopNames = re.findall(REGS['shopName'], shopPage)
          sName = headOrElse(shopNames, "noShopName")
          fshop = open(shopInfoFile, "w")
          fshop.write(sName + "\n")
          allCmtTxt = headOrElse(re.findall(REGS['allCmts'], shopPage, re.DOTALL), "")
          allCmts = re.findall(REGS['singleCmt'], allCmtTxt, re.DOTALL)
          for c in allCmts:
            fshop.write("\n\n" + c)
          fshop.close()

          allReportLinks = set(re.findall(REGS['reportLink'], shopPage))
          for rlink in allReportLinks:
            temp = [x for x in rlink.split("/") if x]
            reportId = temp[-1]
            reportPage = s.get(rlink).text
            girlId = headOrElse(re.findall(REGS['girlId'], reportPage), "noId")
            imgLink = headOrElse(re.findall(REGS['img'], reportPage), "")
            if imgLink.endswith(".jpg.jpg"):
              imgLink = imgLink.replace(".jpg.jpg", ".jpg")
            if imgLink:
              downloadPic(s, homeUrl+imgLink, shopDir, girlId+".jpg")

            (gname, gage) = headOrElse(re.findall(REGS['nameAge'], reportPage), ("noName", "noAge"))
            figure = headOrElse(re.findall(REGS['figure'], reportPage), "noFigure")
            cpValue = headOrElse(re.findall(REGS['CP'], reportPage), "noCP")
            looks = headOrElse(re.findall(REGS['looks'], reportPage), "noLooks")
            pose = headOrElse(re.findall(REGS['pose'], reportPage), "noPose")
            tech = headOrElse(re.findall(REGS['tech'], reportPage), "noTech")
            sm = headOrElse(re.findall(REGS['sm'], reportPage), "noSm")
            content = headOrElse(re.findall(REGS['reportContent'], reportPage, re.DOTALL), "noContent")
            reportFile = "%s/report_%s.txt" % (shopDir, reportId)
            freport = open(reportFile, "w")
            toWrite = "%s\n%s %s %s\n" % (girlId, gname, gage, figure)
            toWrite += "CP: %s\n" % cpValue
            toWrite += "looks: %s\n" % looks
            toWrite += "pose: %s\n" % pose
            toWrite += "tech: %s\n" % tech
            toWrite += "sm: %s\n" % sm
            toWrite += "\n%s\n" % content
            freport.write(toWrite)
            freport.close()

          fvisW.write(shopId+"\n")


fvisW.close()