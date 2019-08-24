# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup

import urllib2
import re, os, shutil

from utils import http_get
from utils import HttpReq

site_url = "http://www.buka.cn"


features = "html.parser"
try:
	import lxml
	features = "lxml"
except ImportError:
	pass

try:
	import PyV8
except ImportError:
	# print "in osx."
	from pyv8 import PyV8


def get_chapters(comic_url):
	if comic_url.startswith("/"):
		comic_url = site_url + comic_url
	html_data = http_get(comic_url)
	soup = BeautifulSoup(html_data,features)
	chapter_box = soup.find(class_="chapterBox")
	chps = {}  # name:url
	for link in  chapter_box.find_all("a"):
		chp_name = link.stripped_strings.next()
		chp_id = None
		m = re.match(u"第(\d+(.\d+)?)话",chp_name,re.UNICODE)

		if m:
			chp_id = m.group(1)
			chp_url = link['href']
			chps[chp_id] = site_url + chp_url
	return chps

def get_chps_from_first_chp(first_chp_url,req):
	if first_chp_url.startswith("/"):
		first_chp_url = site_url + first_chp_url
	chps = {}  # name:url
	next_url = first_chp_url
	while True:
		chp = parse_chp(next_url, req)
		chps[chp["id"]]=chp
		next_url = chp['next_url']
		if next_url == "":
			break
		# break
	return chps
		
def parse_chp(chp_url,req):
	print "try get chp data:%s"%chp_url
	html_data = req.req(chp_url)
	soup = BeautifulSoup(html_data,features)
	chp_str = soup.title.string
	next_url_btn = soup.find(class_="manga-btns-1")
	next_links = next_url_btn.find_all("a")
	next_url = None
	for link in next_links:
		if link.string == u"下一话":
			next_url = link.get('href',"")
			if next_url.startswith("/"):
				next_url = site_url + next_url
	chp = {"url":chp_url,"next_url":next_url} #key:id,url,imgs,next_url
	m = re.match(u"第(\d+(.\d+)?)话.*",chp_str,re.UNICODE)
	if m:
		chp_id = m.group(1)
		chp["id"] = chp_id
		chp["imgs"] = get_imgs_from_soup_data(soup)
	return chp

	

def get_imgs_from_soup_data(soup):
	imgs_box = soup.find(id="manga-imgs")
	imgs = imgs_box.find_all(class_="manga-c")
	imgs_url = []
	for img in imgs:
		url = img.img['src']
		if url.endswith("img-loading.gif"):
			url = img.img['data-original']
		imgs_url.append(url)
	imgs_name = [s[s.rfind("/") + 1:] for s in imgs_url]
	return zip(imgs_name, imgs_url)

def get_imgs_url(chp_url,httpreq):
	# html_data = http_get(chp_url)
	html_data = httpreq.req(chp_url)
	soup = BeautifulSoup(html_data,features)
	return get_imgs_from_soup_data(soup)


if __name__ == "__main__":
	httpreq = HttpReq()
	url = "http://www.buka.cn/view/221736/65537"
	url16 = "http://www.buka.cn/view/221736/65552"
	# imgs = get_imgs_url(ulr,httpreq)
	# print imgs,len(imgs)
	get_chps_from_first_chp(url,httpreq)
	# print parse_chp(url16,httpreq)