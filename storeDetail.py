import requests
import time
import random
from lxml import etree
import sqlite3 as sql

def get_pageUrl():
	conn = sql.connect('lille_yelp.db')
	cursor = conn.cursor()
	cursor.execute('select * from restaurant')
	results = cursor.fetchall()

	code = []
	href = []
	name = []
	for result in results:
		code.append(result[0])
		href.append('https://www.yelp.com'+result[1])
		name.append(result[2])

	return {'code':code,'href':href,'name':name}

def download_html(infos):
	time.sleep(random.randint(1,10))

	for i in range(21, len(infos['code'])):
		code = infos['code'][i]
		href = infos['href'][i]
		name = infos['name'][i]
		time.sleep(random.randint(1,10))
		print(code)
		res = requests.get(href)
		if res.status_code == 200:

			html_data = etree.HTML(res.text)

			dataset = get_detail(html_data)
			insert_data(code, href, name, dataset)


def get_detail(html_data):

	priceText = html_data.xpath('//dd[@class="nowrap price-description"]/text()')
	if len(priceText)>0:
		priceRange = str(priceText)
		if priceRange.find('c')>0:
			newprice = str(priceRange.split('c')[1])
			price = newprice.split('\\')[0]
		else:
			newprice = str(priceRange.replace(' ',''))
			price = newprice.replace('\n','')
	else:
		price=''

	openDate = html_data.xpath('//table[@class="table table-simple hours-table"]/tbody/tr/td')
	week =[]
	if len(openDate) > 0:
		for i in range(0,len(openDate),2):

			openDateText = etree.tostring(openDate[i])
			if openDateText.find('Closed') > 0:
				week.append('closed')
			else:
				openDateHtml = etree.HTML(openDateText)
				openTime = openDateHtml.xpath('//span/text()')
				week.append(openTime[0]+'-'+openTime[1])
	else:
		week.append('','','','','','','')
	business = []
	businessInfo = html_data.xpath('//div[@class="short-def-list"]/dl/dd/text()')
	if len(businessInfo) > 0:
		for eachbusiness in businessInfo:
			newbusiness = eachbusiness.replace(' ','')
			business.append(newbusiness.replace('\n',''))
	else:
		business.append('','','','','','','','','','','','','','','','')

	return {'price':price, 'mon':week[0],'tue':week[1], 'wed':week[2],'thu':week[3],'fri':week[4],'sat':week[5],'sun':week[6], 'reservation': business[0],'delivery': business[1],'takeout': business[2],'acceptCreditCard': business[3],'parking': business[4],'bikeParking': business[5],'goodForKids': business[6],'goodForGroups': business[7],'attire': business[8],'ambience': business[9], 'noiseLevel': business[10],'alcohol': business[11],'outdoorSeating': business[12],'wifi': business[13],'hasTv': business[14],'caters': business[15]}

def insert_data(code, href, name,dataset):
	conn = sql.connect('lille_yelp.db')
	c = conn.cursor()

	sqlrequest = '''INSERT INTO restaurantDetail (code, href, name, price,mon,tue,wed,thu,fri,sat,sun,reservation,delivery,takeout,acceptCreditCard,parking,bikeParking,goodForKids,goodForGroups,attire,ambience,noiseLevel,alcohol,outdoorSeating,wifi,hasTv,caters) values ("%s","%s", "%s", "%s", "%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")''' %(code, href, name,dataset['price'],dataset['mon'],dataset['tue'],dataset['wed'],dataset['thu'],dataset['fri'],dataset['sat'],dataset['sun'],dataset['reservation'],dataset['delivery'],dataset['takeout'],dataset['acceptCreditCard'],dataset['parking'],dataset['bikeParking'],dataset['goodForKids'],dataset['goodForGroups'],dataset['attire'],dataset['ambience'],dataset['noiseLevel'],dataset['alcohol'],dataset['outdoorSeating'],dataset['wifi'],dataset['hasTv'],dataset['caters'])
	c.execute(sqlrequest)
	conn.commit()
	print('Records created successfully')
	conn.close()


if __name__ == '__main__':
	infos = get_pageUrl()
	download_html(infos)