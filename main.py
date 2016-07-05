# -*- coding:utf-8 -*-

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


def down_comic(comic_conf):
	comic_name = comic_conf['comic_name']
	comic_url = comic_conf['comic_url']
	parse = comic_conf.get("parse") or Parse

	chps_url = parse.get_chapters(comic_url)
	for chp_id, chp_url in chps_url.items():
		imgs = parse.get_imgs_url(chp_url)
		# print imgs
		dst_dir = os.path.join(download_path, comic_name, chp_id)
		download_chaper(imgs, dst_dir)
		utils.compress_folder(dst_dir, os.path.join(download_path, comic_name, "compress"))



def main():
	down_comic(conf)

if __name__ == "__main__":
	main()