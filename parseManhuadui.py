# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup

import urllib2
import re, os, shutil

from utils import http_get

from Crypto.Cipher import AES
import binascii

site_url = "https://www.manhuadui.com"
res_host = "https://mhcdn.manhuazj.com"

aes_key = "123456781234567G"
aes_iv = "ABCDEF1G34123412"

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


def aes_decrypt(decry_text):
	text = binascii.a2b_base64(decry_text)
	# iv = text[0:AES.block_size]
	cryptor = AES.new(aes_key, AES.MODE_CBC, aes_iv)
	plaintext = cryptor.decrypt(text)
	return plaintext


def get_chapters(comic_url):
	if comic_url.startswith("/"):
		comic_url = site_url + comic_url
	html_data = http_get(comic_url)
	soup = BeautifulSoup(html_data,features)
	chapter_box = soup.find(id="chapter-list-1")
	chps = {}  # name:url
	
	for link in  chapter_box.find_all("a"):
		chp_name = link.stripped_strings.next()
		chp_id = None
		m = re.match(u"(\d+(.\d+)?)[页话](.*)",chp_name,re.UNICODE)

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

	js_ctx = PyV8.JSContext()
	js_ctx.enter()

	js_ctx.eval(script.encode("utf-8"))
	# print dict(js_ctx.locals)
	# img_server = dict(js_ctx.locals.imageServerConf).values()[0]
	chp_path = str(js_ctx.locals.chapterPath)
	img_name_aes_str = str(js_ctx.locals.chapterImages)
	
	print chp_path
	print img_name_aes_str
	names =  aes_decrypt(img_name_aes_str)
	if names.startswith("["):
		names = names[1:names.rfind("]")]
	names = names.split(",")
	
	img_name_list = []
	for name in names:
		if name.startswith('"'):
			img_name_list.append(name[1:-1])
	# print img_name_list,len(img_name_list),chp_path
	
	imgs_name = []
	imgs_url = [res_host+"/"+chp_path+name for name in img_name_list]

	imgs_name = [s[s.rfind("/") + 1:] for s in imgs_url]
	imgs_rename = []
	#rename:
	for i,s in enumerate(imgs_name):
		ext = s[s.rfind("."):]
		if ext!=".jpg" or ext!=".png":
			ext = ".jpg"
		imgs_rename.append(str(i)+ext)
		
	# imgs_rename = [str(i)+s[s.rfind("."):] for i,s in enumerate(imgs_name)]
	return zip(imgs_rename, imgs_url)

if __name__ == "__main__":
	pass
	l = get_chapters("/manhua/guimiezhiren/")
	# l.sort(key=attrgetter("chp_id"))
	chs = [(int(k),v) for k,v in l.items()]
	chs.sort(key=lambda a:a[0])
	keys = [int(k) for k in l]
	keys.sort()
	pprint.pprint(chs)
	print len(chs)
	
	# test_url = "https://www.manhuadui.com/manhua/guimiezhiren/8415.html"
	# imgs = get_imgs_url(test_url)
	# pprint.pprint(imgs)
	# print len(imgs)
	
	# en_str = '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'
	# print [aes_decrypt(en_str)]