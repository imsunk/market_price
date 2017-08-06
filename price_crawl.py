# -*- coding: utf-8 -*-
import re
import pandas as pd
from datetime import datetime
import requests
import datetime
import pymysql
import codecs
from urllib.parse import urlencode, quote_plus
import os

BINDIR = os.getcwd()
REALTIME_URL = "http://apis.data.go.kr/B552895/openapi/service/OrgPriceAuctionService/getRealMarketPriceList"
PRICE_URL = "http://apis.data.go.kr/B552895/openapi/service/OrgPriceAuctionService/getExactProdPriceList"
svcKey="eBSENI1zA5JHeaLdyssY0bQ7VbtZjIqrgslC1BlBqUW5wcqmg1hnGdZx3t%2BSb4U8DZV1M2GP0vWCNodNCGXzTA%3D%3D"

queryParams = '?' + urlencode({'ServiceKey': k, quote_plus('pageNo'):'1', 
                              quote_plus('numOfRows'):'1000', quote_plus('delngDe'):'20170805',
                              quote_plus('prdlstCd'):'0614'})
#req = requests.get(priceUrl+queryParams)
######
import xml.etree.ElementTree as ET
import codecs
prodFile = codecs.open(BINDIR+"/productCode.xml",mode='r',encoding='utf-8')
tree = ET.parse(prodFile)
root = tree.getroot()
prodList={}

for row in root.findall('Row'):
    if row.find("구품목코드").text not in prodList:
        prodList[row.find("구품목코드").text]={}
        prodList[row.find("구품목코드").text]["itemName"] = row.find("구품목명").text
        prodList[row.find("구품목코드").text]['subItems'] = []
    prodList[row.find("구품목코드").text]['subItems'].append(
        {"subItemName":row.find("품종명").text, "subItemCode":row.find("구품종코드").text})
del prodList['stdPrdlstCode']


conn = pymysql.connect(host='webzook.net', user='smile2x', passwd="0173", db='nbnote',use_unicode=True,charset='utf8')
cursor = conn.cursor()
for prod in prodList:
    itemName=prodList[prod]["itemName"]
    for sub in prodList[prod]['subItems']:
        print (prod, itemName, sub['subItemCode'],sub['subItemName'])
        sql = "INSERT INTO price_day ('itemCode','itemName','subItemCode','subItemName', 'market', 'quality','quantity', 'unit','md') VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(prod, itemName, sub['subItemCode'],sub['subItemName']) 
        cursor.execute(sql)
conn.close()


