# -*- coding:utf-8 -*-

import urllib2
import zipfile
import os

def http_get(url):
	print "GET:%s"%url
	resp = urllib2.urlopen(url)
	data = resp.read()
	return data


def compress_folder(src,dst):
	base_path, arch_path = os.path.split(src)
	arch_file = arch_path + ".zip"
	if not os.path.exists(dst):
		os.makedirs(dst)
	zip_path = os.path.join(dst, arch_file)
	zipf = zipfile.ZipFile(zip_path, "w")
	for root,dirs,files in os.walk(src):
		for fname in files:
			fpath = os.path.join(root,fname)
			zipf.write(fpath,fname)
		break

	zipf.close()