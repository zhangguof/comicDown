# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup

import urllib2
import re, os, shutil

from utils import http_get

site_url = "http://www.tuku.cc"


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


def get_imgs_url(chp_url):
	html_data = http_get(chp_url)
	# print html_data
	soup = BeautifulSoup(html_data,features)
	scripts = soup.find_all("script",src="",type="text/javascript")
	script_texts = []
	for text in scripts:
		t = text.string
		if t and (t.find("var serverUrl = '';") != -1 or t.find("eval(function(p,a,c,k,e,d)") != -1):
			script_texts.append(t)
	script = u"".join(script_texts)

	js_ctx = PyV8.JSContext()
	js_ctx.enter()

	js_ctx.eval(script.encode("utf-8"))
	# print dict(js_ctx.locals)
	img_server = dict(js_ctx.locals.imageServerConf).values()[0]
	total_page = js_ctx.locals.pages
	js_get_img_url= js_ctx.locals.getImgUrl
	imgs_url = []
	for i in xrange(1,total_page+1):
		imgs_url.append(img_server + js_get_img_url(i))
	imgs_name = [s[s.rfind("/") + 1:] for s in imgs_url]
	return zip(imgs_name, imgs_url)