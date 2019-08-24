#-*- coding:utf-8 -*-
import utils
import os

def main(argv):
	src = argv[0]
	out = argv[1]
	comic_name = os.path.basename(src)
	dst_path = os.path.join(out,comic_name)
	for root, dirs, files in os.walk(src):
		for chp in dirs:
			chp_path = os.path.join(root,chp)
			utils.compress_folder(chp_path,dst_path)
			print "comperss:%s->%s"%(chp_path,dst_path)
		break

if __name__ == "__main__":
	import sys
	main(sys.argv[1:])
