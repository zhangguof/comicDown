# -*- coding:utf-8 -*-
from gevent import monkey; monkey.patch_all()
import gevent

from utils import http_get
from bs4 import BeautifulSoup

import urllib2
import re, os, shutil
import utils

import parseTuku as Parse

conf = {
	"comic_name": u"政宗君的复仇",
	"comic_url": "/comic/10533/",
}
download_path = "comics"

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

import gevent


def dowload_chaper_by_gevent(imgs_url,dst_dir):
	if not os.path.exists(dst_dir):
		if not os.path.exists(dst_dir):
			os.makedirs(dst_dir)
	greents = []
	for img_url in imgs_url:
		img_name = img_url[img_url.rfind("/") + 1:]
		img_path = os.path.join(dst_dir, img_name)

		if os.path.exists(img_path):
			print "skip:%s" % img_path
			continue
		greents.append(gevent.spawn(utils.down_and_save, img_url, img_path))
	gevent.joinall(greents)


def download_chaper(imgs_url,dst_dir):
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	# imgs_url = Parse.get_imgs_url(chp_url)
	for img_url in imgs_url:

		img_name = img_url[img_url.rfind("/") + 1:]
		img_path = os.path.join(dst_dir, img_name)

		if os.path.exists(img_path):
			print "skip:%s"%img_path
			continue

		img_context = http_get(img_url)

		with open(img_path,"wb") as f:
			f.write(img_context)
		print "download %s:%s"%(img_url, img_path)

def down_comic_by_gevent(comic_conf):
	comic_name = comic_conf['comic_name']
	comic_url = comic_conf['comic_url']
	parse = comic_conf.get("parse") or Parse

	chps_url = parse.get_chapters(comic_url)
	chps_ids = chps_url.keys()
	chps_ids.sort()

	greents = []
	def down_chp(chp_id):
		chp_url = chps_url[chp_id]
		imgs = parse.get_imgs_url(chp_url)
		dst_dir = os.path.join(download_path, comic_name, chp_id)
		dowload_chaper_by_gevent(imgs, dst_dir)
		#utils.compress_folder(dst_dir, os.path.join(download_path, comic_name, "compress"))

	for chp_id in chps_ids:
		greents.append(gevent.spawn(down_chp,chp_id))

	gevent.joinall(greents)



def down_comic(comic_conf):
	comic_name = comic_conf['comic_name']
	comic_url = comic_conf['comic_url']
	parse = comic_conf.get("parse") or Parse

	chps_url = parse.get_chapters(comic_url)
	chps_ids= chps_url.keys()
	chps_ids.sort()
	for chp_id in chps_ids:
		chp_url = chps_url[chp_id]
		imgs = parse.get_imgs_url(chp_url)

		dst_dir = os.path.join(download_path, comic_name, chp_id)
		#download_chaper(imgs, dst_dir)
		dowload_chaper_by_gevent(imgs, dst_dir)
		utils.compress_folder(dst_dir, os.path.join(download_path, comic_name, "compress"))



def main():
	import time
	s_time = time.time()
	#down_comic(conf)
	down_comic_by_gevent(conf)
	e_time = time.time()
	print "cost time:",e_time - s_time

if __name__ == "__main__":
	main()