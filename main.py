# -*- coding:utf-8 -*-
from gevent import monkey; monkey.patch_all()
import gevent

from utils import http_get, HttpReq
from bs4 import BeautifulSoup

import urllib2
import re, os, shutil
import utils

from operator import itemgetter, attrgetter

# import parseTuku as Parse
# import parseHentai as Parse
# conf = {
# 	"comic_name": u"政宗君的复仇",
# 	"comic_url": "/comic/10533/",
# }
# import parseBuka as Parse
import parse36mh

# conf = {
# 	"comic_name": u"1年A班的Monster",
# 	"comic_url": "",
# 	"firs_chp_url":"/view/221736/65537",
# }

conf = {
	"comic_name":u"黑色四叶草",
	"comic_url":"/manhua/heisesiyecao/",
	"Parse":parse36mh,
}
download_path = "comics"


import gevent
from gevent import Timeout
from gevent.pool import Pool

seconds = 20

# timeout = Timeout(seconds)
# timeout.start()

down_pool = utils.DownPool(100)
down_pool.reg_fun(utils.down_and_save)

pool = Pool(100)


class Comic(object):
	def __init__(self, name, url, down_path,parse,first_chp_url=''):
		self.chapters = [] #
		self.name = name
		self.url = url
		self.first_chp_url = first_chp_url
		self.comic_path = os.path.join(down_path, name)
		self.Parse = parse



	def load_chapters(self,start_id=0,end_id=10000000):
		if self.url == "":
			return self.load_chps_from_fist_chps()
		chps = self.Parse.get_chapters(self.url)
		# print chps
		for chp_id,chp_url in chps.items():
			if(int(chp_id) < start_id) or int(chp_id)>end_id:
				continue
			self.add_chapter(chp_id, chp_url)

		self.chapters.sort(key=attrgetter("chp_id"))
		# print self.chapters
		# self.chapters = self.chapters[:2]
	def load_chps_from_fist_chps(self):
		http_req = HttpReq()
		chps = self.Parse.get_chps_from_first_chp(self.first_chp_url,http_req)
		for chp_id,item in chps.items():
			self.add_chapter(chp_id,item["url"],item["imgs"])
			
		self.chapters.sort(key=attrgetter("chp_id"))
		# print self.chapters
	
	def add_chapter(self,chp_id, chp_url,imgs=None):
		self.chapters.append(Chapter(chp_id,chp_url,self.comic_path,self.Parse,imgs))

	def download_all(self):
		def _down(chp):
			print "going to down chapter:%s"%chp.chp_id
			chp.load()
			print "load chp:%s,success."%chp.chp_id
			chp.down_imgs()
			print "down chp:%s,suceess."%chp.chp_id

		pool.map(_down, self.chapters)
		# gs = [gevent.spawn(_down, arg) for arg in self.chapters]
		# gevent.joinall(gs)




class Chapter(object):
	def __init__(self, chp_id, url, comic_path,parse,imgs=None):
		self.chp_id = chp_id
		self.url = url
		self.imgs = [] if imgs is None else imgs # (name,url)
		self.chp_path = os.path.join(comic_path,chp_id)
		self.Parse = parse

	def load(self):
		if len(self.imgs) == 0:
			self.imgs = self.Parse.get_imgs_url(self.url)

	def down_imgs(self):
		if not os.path.exists(self.chp_path):
			os.makedirs(self.chp_path)

		def _down(args):
			img_name, img_url = args
			img_path = os.path.join(self.chp_path, img_name)
			if os.path.exists(img_path):
				print "skip:%s" % img_path
				return
			utils.down_and_save2(img_url, img_path)
		pool.map(_down, self.imgs)
		# greents = [gevent.spawn(_down, *img) for img in self.imgs]
		# print "going to joinall imgs:%s"%self.chp_id
		# gevent.joinall(greents)

	def __str__(self):
		return self.chp_id+":,"+str(self.imgs)




		# for img_name, img_url in self.imgs:

def download_chapter_by_gevent(imgs_url,dst_dir):
	if not os.path.exists(dst_dir):
		if not os.path.exists(dst_dir):
			os.makedirs(dst_dir)

	for img_url in imgs_url:
		img_name = img_url[img_url.rfind("/") + 1:]
		img_path = os.path.join(dst_dir, img_name)

		if os.path.exists(img_path):
			print "skip:%s" % img_path
			continue
		down_pool.add_task(0, (img_url, img_path))
	# 	greents.append(gevent.spawn(utils.down_and_save, img_url, img_path))
	# gevent.joinall(greents)


def download_chapter(imgs_url,dst_dir):
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	# imgs_url = Parse.get_imgs_url(chp_url)
	for img_url in imgs_url:

		img_name = img_url[img_url.rfind("/") + 1:]
		img_path = os.path.join(dst_dir, img_name)

		if os.path.exists(img_path):
			print "skip:%s" % img_path
			continue

		img_context = http_get(img_url)

		with open(img_path,"wb") as f:
			f.write(img_context)
		print "download %s:%s" % (img_url, img_path)

def down_comic_by_gevent(comic_conf):
	comic_name = comic_conf['comic_name']
	comic_url = comic_conf['comic_url']
	parse = comic_conf.get("parse") or Parse

	chps_url = parse.get_chapters(comic_url)
	chps_ids = chps_url.keys()
	chps_ids.sort()

	greents = []
	down_count = 0
	def down_chp(chp_id):
		chp_url = chps_url[chp_id]
		imgs = parse.get_imgs_url(chp_url)
		dst_dir = os.path.join(download_path, comic_name, chp_id)
		dowload_chapter_by_gevent(imgs, dst_dir)

		utils.compress_folder(dst_dir, os.path.join(download_path, comic_name, "compress"))

	down_pool.reg_fun(down_chp)

	def start_pool():
		down_pool.start()
	#greents.append(gevent.spawn(start_pool))
	g = gevent.spawn(start_pool)

	# chps_ids = chps_ids[:4]
	for chp_id in chps_ids:
		#greents.append(gevent.spawn(down_chp, chp_id))
		down_pool.add_task(1, (chp_id,))

	g.join()

	#gevent.joinall(greents)



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
		#download_chapter(imgs, dst_dir)
		dowload_chapter_by_gevent(imgs, dst_dir)
		utils.compress_folder(dst_dir, os.path.join(download_path, comic_name, "compress"))


def make_zip(comic,dst,rewrite=False):
	for chp in comic.chapters:
		chp_dst = os.path.join(dst,comic.name)
		chp_src = os.path.join(comic.comic_path,chp.chp_id)
		utils.compress_folder(chp_src,chp_dst,rewrite)

def main():
	import time
	s_time = time.time()
	# down_comic(conf)
    # down_comic_by_gevent(conf)
	comic = Comic(conf['comic_name'], conf['comic_url'], \
	              download_path, conf["Parse"],conf.get('firs_chp_url',""))
	comic.load_chapters(171)
	# comic.download_all()
	make_zip(comic,"zips",True)
	
	
	
	

	e_time = time.time()
	print "cost time:",e_time - s_time

if __name__ == "__main__":
	main()