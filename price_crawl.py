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
import xml.etree.ElementTree as ET
import codecs

'''
print (item.find("sbidTime").text) ##경매시간
print (item.find("whsalMrktCode").text) ### 시장코드
print (item.find("whsalMrktNm").text) ### 시장이름
print (item.find("insttNewNm").text) ### 법인명(가게이름)
print (item.find("stdPrdlstCode").text) ###구품목코드 
print (item.find("stdPrdlstNm").text)  ###구품목명 
print (item.find("stdSpciesCode").text) ###구품종코드 
print (item.find("stdSpciesNm").text)  ###구품종명
print (item.find("delngPrut").text)  ###거래단량(거래되는 단위)
print (item.find("stdUnitNewNm").text)  ###단위명 (kg,)
print (item.find("stdFrmlcNewNm").text)  ###포장상태 (박스)
print (item.find("stdMgNewNm").text)  ###크기명
print (item.find("stdQlityNewNm").text)  ###등급명 (농산물9등급)
print (item.find("sbidPric").text) ###거래가격
print (item.find("cprMtcCode").text)  ###구산지코드
print (item.find("cprMtcNm").text) ###구산지명
print (item.find("delngQy").text) ###거래량
'''

BINDIR = os.getcwd()
REALTIME_URL = "http://apis.data.go.kr/B552895/openapi/service/OrgPriceAuctionService/getRealMarketPriceList"
PRICE_URL = "http://apis.data.go.kr/B552895/openapi/service/OrgPriceAuctionService/getExactProdPriceList"
svcKey="eBSENI1zA5JHeaLdyssY0bQ7VbtZjIqrgslC1BlBqUW5wcqmg1hnGdZx3t%2BSb4U8DZV1M2GP0vWCNodNCGXzTA%3D%3D"

'''
queryParams = '?' + urlencode({'ServiceKey': k, quote_plus('pageNo'):'1', 
                              quote_plus('numOfRows'):'1000', quote_plus('delngDe'):'20170805',
                              quote_plus('prdlstCd'):'0614'})
'''
today=datetime.datetime.today().strftime("%Y%m%d")

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

dataCnt = 0
dataList = []
conn = pymysql.connect(host='webzook.net', user='smile2x', passwd="0173", db='nbnote',use_unicode=True,charset='utf8')
cursor = conn.cursor()

sql = "INSERT INTO price_day ('aucTime','marketCode','marketName','corpName', 'itemCode', 'itemName','subItemCode', 'subItemName','dealQuantity', 'unit', 'packing', 'size','quality','price','fromCode','originPlaceCode','originPlaceName','dealQuantity') VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"
queryParams = "?ServiceKey=%s&pageNo=1&numOfRows=100000&delngDe=%s&prdlstCd=" %(svcKey,today)
for pid in prodList:
	queryParam = queryParam+pid
	req = requests.get(priceUrl+queryParams)
	reqRoot = ET.fromstring(req)
	for item in reqRoot[1][0]:
		try:
			dataList.append((item.find("sbidTime").text,item.find("whsalMrktCode").text,item.find("whsalMrktNm").text,item.find("insttNewNm").text,item.find("stdPrdlstCode").text,item.find("stdPrdlstNm").text,item.find("stdSpciesCode").text,
			item.find("stdSpciesNm").text, item.find("delngPrut").text,item.find("stdUnitNewNm").text,item.find("stdFrmlcNewNm").text,item.find("stdMgNewNm").text,item.find("stdQlityNewNm").text,item.find("sbidPric").text,item.find("cprMtcCode").text,
			item.find("cprMtcNm").text,item.find("delngQy").text))
		except AttrubuteError:
			continue	

		if dataCnt%3000==0:
			cursor.executemany(sql,dataList)
			cursor.commit()
			dataList = []
		dataCnt+=1
		
cursor.executemany(sql,dataList)
cursor.commit()
conn.close()

