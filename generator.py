#!/usr/bin/env python
import Image
import lib
import argparse

#Add arguments, see their help
parser = argparse.ArgumentParser()
parser.add_argument("input", help="Specifies the big input file")
parser.add_argument('blocks', type=str, nargs="+", help='A list of files to be used as blocks')
parser.add_argument("-o", "--output", help="Specifies the file to which the output file should be stored")
parser.add_argument("-bs", "--blocksize", type=int, help="Specifies the size of the image blocks")
parser.add_argument("--height", type=int, help="Specifies how high the input image should be scaled to")
parser.add_argument("--select", type=str, help="Specifies how to select an image to use as a block. Choises are: random, choose, iterate")
parser.add_argument("--seed", type=int, help="Specifies a seed to use for random. Only use together with '--select random'")
args = parser.parse_args()

#Store the args in some variables used by lib.py
output = "output.png"
inputFile = args.input
inputBlocks = []
for img in args.blocks:
	inputBlocks.append(Image.open(img))

if args.output:
	output = args.output
if args.blocksize:
	lib.blockSize = args.blocksize
if args.select:
	if args.select == "random":
		lib.matchType = 0
	elif args.select == "choose":
		lib.matchType = 1
	elif args.select == "iterate":
		lib.matchType = 2
	else:
		print("You have not choosen a valid --select value")
if args.seed:
	lib.seed = args.seed
if args.height:
	lib.imgHeight = args.height
	

logo_orig = Image.open(inputFile)
logo = logo_orig.copy()
logo = lib.generateImage(logo, inputBlocks)
#logo.show()
#logo_orig.show()
logo.save(output)
