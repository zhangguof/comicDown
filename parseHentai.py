# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup

import urllib2
import re, os, shutil

from utils import http_get

site_url = "https://hentaihere.com"


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


def get_chapters(comic_url, html_data=None):
	if html_data is None:
		if comic_url.startswith("/"):
			comic_url = site_url + comic_url
		html_data = http_get(comic_url)
	soup = BeautifulSoup(html_data,features)
	chapter_blocks = soup.find_all(id="chapterBlock")
	chps = {}  # name:url
	for link in chapter_blocks:
		chp_name =  link.stripped_strings.next()
		chp_url = link['href']
		chps[chp_name] = chp_url
	return chps

#<img id="arf-reader-img" src="https://hentaicdn.com/hentai/14159/1/hcdn0002.jpg" alt="Sweet Guy"/>
url_re = re.compile(r"(?P<img_url>https://.+/hentai/(?P<comic_id>\d+)/(?P<chp_id>\d+))/(?P<img_name>(?P<name_pre>[a-zA-Z]+)(?P<name_num>\d+)(?P<img_ext>\.\w+))$")
def get_imgs_url(chp_url, html_data = None):
	if html_data is None:
		html_data = http_get(chp_url)
	# print html_data
	soup = BeautifulSoup(html_data,features)
	imgs = soup.find(class_="dropdown-menu text-center list-inline")
	img_pages = imgs.find_all(class_="rdrPage")
	img_url = soup.find(id="arf-reader-img")
	link = img_url['src']
	total_page = len(img_pages)
	m = url_re.match(link)
	if m:
		base_url = m.group("img_url")
		img_name_pre = m.group("name_pre")
		img_ext = m.group("img_ext")
		name_num = m.group("name_num")
		num_len = len(name_num)
		img_num_str = "%%0%dd" % num_len

		imgs_url = []
		for i in xrange(1,total_page+1):
			img_num = img_num_str % i
			url = "%s/%s%s%s"%(base_url,img_name_pre,img_num,img_ext)
			print url
			imgs_url.append(url)
		imgs_name = [s[s.rfind("/") + 1:] for s in imgs_url]
		return zip(imgs_name, imgs_url)
	else:
		raise Exception("get_img_err!"), chp_url


if __name__=="__main__":
	# with open("test/Sweet Guy (Original) - by at HentaiHere.com.html", "rb") as f:
	# 	html = f.read()
	# chps = get_chapters("",html)
	# print chps
	imgs = get_imgs_url("https://hentaihere.com/m/S14159/1/2/")
	print imgs
