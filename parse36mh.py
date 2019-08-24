# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup

import urllib2
import re, os, shutil

from utils import http_get

site_url = "http://www.36mh.com"
res_host = "https://img001.yayxcc.com"

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
	
import pprint


def get_chapters(comic_url):
	if comic_url.startswith("/"):
		comic_url = site_url + comic_url
	html_data = http_get(comic_url)
	soup = BeautifulSoup(html_data,features)
	chapter_box = soup.find(class_="chapter-body")
	chps = {}  # name:url
	for link in  chapter_box.find_all("a"):
		chp_name = link.stripped_strings.next()
		chp_id = None
		m = re.match(u"第(\d+(.\d+)?)[页话](.*)",chp_name,re.UNICODE)

		if m:
			chp_id = m.group(1)
			chp_url = link['href']
			chps[chp_id] = site_url + chp_url
	return chps

#https://img001.yayxcc.com/images/comic/137/273195/1535430065Gnj6kb-ODUvjLhfj.jpg
def get_imgs_url(chp_url):
	html_data = http_get(chp_url)
	# print html_data
	soup = BeautifulSoup(html_data,features)
	scripts = soup.find_all("script")
	script_texts = []
	for text in scripts:
		t = text.string
		if t and (t.find("var chapterImages") != -1):
			script_texts.append(t)
			break
	script = u"".join(script_texts)
	# pprint.pprint(script)

	js_ctx = PyV8.JSContext()
	js_ctx.enter()

	js_ctx.eval(script.encode("utf-8"))
	# print dict(js_ctx.locals)
	# img_server = dict(js_ctx.locals.imageServerConf).values()[0]
	chp_path = str(js_ctx.locals.chapterPath)
	img_name_list = list(js_ctx.locals.chapterImages)
	
	# print img_name_list,len(img_name_list),chp_path
	
	# print dict(js_ctx.locals)
	# img_server = dict(js_ctx.locals.imageServerConf).values()[0]
	# total_page = js_ctx.locals.pages
	# js_get_img_url= js_ctx.locals.getImgUrl
	
	imgs_url = [res_host+"/"+chp_path+name for name in img_name_list]
	# for i in xrange(1,total_page+1):
	# 	imgs_url.append(img_server + js_get_img_url(i))
	imgs_name = [s[s.rfind("/") + 1:] for s in imgs_url]
	#rename:
	imgs_rename = [str(i)+s[s.rfind("."):] for i,s in enumerate(imgs_name)]
	return zip(imgs_rename, imgs_url)

if __name__ == "__main__":
	# l = get_chapters("/manhua/heisesiyecao")
	# # l.sort(key=attrgetter("chp_id"))
	# chs = [(int(k),v) for k,v in l.items()]
	# chs.sort(key=lambda a:a[0])
	# keys = [int(k) for k in l]
	# keys.sort()
	# pprint.pprint(chs)
	# print len(chs)
	imgs = get_imgs_url("https://www.36mh.com/manhua/heisesiyecao/273195.html#p=1")
	pprint.pprint(imgs)
	print len(imgs)