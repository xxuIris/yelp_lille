import requests
import time
import random
from lxml import etree
import sqlite3 as sql

def download_html(pageNum):
	time.sleep(random.randint(1,10))
	url = 'https://www.yelp.com/search?find_loc=lille&start=' + str(pageNum *10)
	r = requests.get(url)
	if r.status_code == 200:
		print pageNum
		res = etree.HTML(r.text)
		return res
	else:
		return null

def get_infos(res):
	result = etree.tostring(res, pretty_print = True)
	html = result.encode('utf-8')
	html_data = etree.HTML(html)
	code = []
	href = []
	name = []
	review =[]
	category = []
	neighborhood = []
	address = []
	phone =[]

	codes = html_data.xpath('//span[@class="indexed-biz-name"]/text()')
	for i in range(0, 19, 2):
		code.append(codes[i].replace(' ',''))

	hrefs = html_data.xpath('//span[@class="indexed-biz-name"]/a/@href')
	for eachhref in hrefs:
		href.append(eachhref)

	names = html_data.xpath('//span[@class="indexed-biz-name"]/a/span/text()')
	for eachname in names:
		name.append(eachname.encode('ascii','ignore'))

	reviews = html_data.xpath('//span[@class = "review-count rating-qualifier"]/text()')
	for eachreview in reviews:
		review.append(eachreview)

	categories = html_data.xpath('//span[@class="category-str-list"]/a/text()')
	for eachcategory in categories:
		category.append(eachcategory)

	neighborhoods = html_data.xpath('//span[@class="neighborhood-str-list"]/text()')
	for eachneighborhood in neighborhoods:
		newneighborhood = eachneighborhood.replace(' ','')
		newneighborhood = newneighborhood.replace('\n','')
		neighborhood.append(newneighborhood)

	addresses = html_data.xpath('//address/text()')
	for eachaddress in addresses:
		newaddress = eachaddress.encode('ascii','ignore')
		newaddress = newaddress.replace(' ','')
		newaddress = newaddress.replace('\n','')
		address.append(newaddress)

	phones = html_data.xpath('//span[@class="biz-phone"]/text()')
	for eachphone in phones:
		eachphone = eachphone.replace(' ','')
		eachphone = eachphone.replace('\n','')
		phone.append(eachphone)
	return {'code': code, 'href':href, 'name':name, 'review':review, 'category':category, 'neighborhood':neighborhood, 'address':address, 'phone':phone}

def upload_sql(infos):
	conn = sql.connect('lille_yelp.db')
	c = conn.cursor()

	for code, href, name, review, category, neighborhood, address, phone in zip(infos['code'], infos['href'], infos['name'], infos['review'], infos['category'], infos['neighborhood'], infos['address'], infos['phone']):
		sqlrequest = '''INSERT INTO restaurant (code,href,name,review,category,neighborhood,address,phone) values ("%s", "%s", "%s", "%s","%s","%s","%s","%s")''' %(code, href, name,review, category, neighborhood, address,phone)
		c.execute(sqlrequest)
	conn.commit()
	print('Records created successfully')
	conn.close()

if __name__ == '__main__':

	for i in range(100,101):
		print i
		res = download_html(i)
		result = get_infos(res)
		upload_sql(result)
