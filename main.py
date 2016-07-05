#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import PyV8
import urllib2
import re

site_url = "http://www.tuku.cc"
comic_url = "http://www.tuku.cc/comic/10533/"

def http_get(url):
	print "GET:%s"%url
	resp = urllib2.urlopen(url)
	data = resp.read()
	return data

def get_chapters(comic_url):
	html_data = http_get(comic_url)
	soup = BeautifulSoup(html_data, "lxml")
	chapter_box = soup.find(class_="chapterBox")
	chps = {}#name:url
	for link in  chapter_box.find_all("a"):
		chp_name = link.stripped_strings.next()
		chp_id = None
		m = re.match(u"第(\d+(.\d+)?)话",chp_name,re.UNICODE)

		if m:
			chp_id = m.group(1)
			chp_url = link['href']
			chps[chp_id] = chp_url
	return chps





def main():
	print get_chapters(comic_url)


if __name__ == "__main__":
	main()