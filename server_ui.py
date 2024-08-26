#!/usr/bin/env python
# -*- coding:utf-8 -*-

import BaseHTTPServer
import os
from os import listdir
from os.path import expanduser, isfile, join
from urlparse import urlparse, parse_qs
import Image
import lib

PORT = 8080

#Create the generer_billede directory and subdir
home = expanduser("~")
generate_image = home + os.sep + "generer_billede"
if not os.path.exists(generate_image):
	os.mkdir(generate_image)
smaller_images = generate_image + os.sep + "mindre_billeder"
if not os.path.exists(smaller_images):
	os.mkdir(smaller_images)

def readFile(name):
	return open(os.path.join(os.path.dirname(__file__), name)).read()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
	def do_GET(self):
#		print("Path: " + self.path)
		html_output = readFile("index.html")
		if "size" in self.path and "output" in self.path:#Process the images
			args = parse_qs(urlparse(self.path).query)
#			print(args)
			html_output = readFile("done.html")
			lib.blockSize = int(args.get("size")[0])
			lib.matchType = 0 #Means: select a random image
			small_images = [ Image.open(join(smaller_images, f)) for f in listdir(smaller_images) if isfile(join(smaller_images, f)) ]
			big_image = [ join(generate_image, f) for f in listdir(generate_image) if isfile(join(generate_image, f)) ]
			if not len(big_image) == 1 :
				html_output = readFile("index.html")
				html_output = html_output.replace("<!--error-->", "Fejl: fandt mere end en fil i generer_billede mappen!")
			elif len(small_images) < 1:
				html_output = readFile("index.html")
				html_output = html_output.replace("<!--error-->", "Fejl: kunne ikke finde nogen filer i mappen mindre_billeder!")
			else:
				img = Image.open(big_image[0])
				new_img = lib.generateImage(img, small_images)
				new_img.save(generate_image + os.sep + args.get("output")[0])
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		print(html_output)
		self.wfile.write(html_output)

httpd = BaseHTTPServer.HTTPServer(("", PORT), MyHandler)
httpd.serve_forever()
