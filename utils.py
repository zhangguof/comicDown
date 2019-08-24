# -*- coding:utf-8 -*-

import urllib2
import zipfile
import os
import gevent
from gevent.pool import Pool
from gevent.queue import Queue

import traceback
import requests
import cookielib


class DownPool(object):
	def __init__(self,size):
		self.max_size = size
		self.count = 0
		self.pool = Pool(size)
		self.queues = []
		self._stop = False
		self._has_kill = False
		#self.pool.map(self.work, xrange(0, size))
		self.funs = []

	def reg_fun(self,f):
		self.funs.append(f)
		self.queues.append(Queue())

	def start(self):
		print "[pool] staring..."
		self.pool.map(self.work, xrange(0, self.max_size))
		print "[pool] end...."
		print "free count:", self.pool.free_count()

	def stop(self):
		self._stop = True

	def work(self, work_id):
		print "[pool] start work:%d" % work_id
		while (not self.queues[0].empty()) or (not self.queues[1].empty()):
			# if self._stop:
			# 	break
			for idx in xrange(0, len(self.queues)):
				f = self.funs[idx]
				q = self.queues[idx]
				if q.empty():
					continue
				args = q.get()
				#print "start f:",f,args
				f(*args)
				#print "end f:", f, args

			gevent.sleep(0.01)


		print "[pool] end work:%d" % work_id
		print "free count:", self.pool.free_count()


	def add_task(self, idx, args):
		self.queues[idx].put(args)


def http_get(url):
	print "GET:%s"%url
	resp = urllib2.urlopen(url)
	data = resp.read()
	return data

HEADERS = {
#"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
# "User-Agent":"Mozilla/5.0 (iPad; CPU OS 11_1_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 Mobile/15B150 Safari/604.1",
}

class HttpReq:
	def __init__(self):
		self.cookie = cookielib.CookieJar()

	def req(self,url,headers=HEADERS):
		# print "url:",url
		handler = urllib2.HTTPCookieProcessor(self.cookie)
		opener = urllib2.build_opener(handler)
		req = urllib2.Request(url,headers=headers)
		res = opener.open(req)
		# print self.cookie,res.read()
		if res.getcode() == 200:
			return res.read()
	

def down_and_save2(url, dst_path):
	print "downloading %s" % url
	r = requests.get(url)
	chunk_size = 4096
	with open(dst_path, 'wb') as fd:
		for chunk in r.iter_content(chunk_size):
			fd.write(chunk)
	print "save %s" % dst_path

def down_and_save(url,dst_path):
	print "downloading %s"%url
	try:
		context = http_get(url)
		print "down %s success."%url
		with open(dst_path, "wb") as f:
			f.write(context)

	except:
		print "error in down:%s"%url
		traceback.format_exc()

	print "save %s" % dst_path


import shutil
def compress_folder(src,dst,rewrite=False):
	base_path, arch_path = os.path.split(src)
	arch_file = arch_path + ".zip"
	if not os.path.exists(dst):
		os.makedirs(dst)
	zip_path = os.path.join(dst, arch_file)
	if os.path.exists(zip_path) and not rewrite:
		print "existing... %s"%zip_path
		return
		
	zipf = zipfile.ZipFile(zip_path, "w")
	for root,dirs,files in os.walk(src):
		for fname in files:
			if fname.endswith(".jpg") or fname.endswith(".png"):
				fpath = os.path.join(root,fname)
				zipf.write(fpath,fname)
		break

	zipf.close()