from PIL import Image, ImageDraw
import math
import random

blockSize = 16
blockHeight = 16
blockWidth = 16

matchType = 0;
# 0 = random
# 1 = select best
# 2 = iterate

seed = -1
imgHeight = -1

#####################################################
# PyCrop (https://github.com/christopherhan/pycrop) #
#####################################################
def prepare_image(image, thumbnail_size):
	x,y = image.size
	th_x, th_y = thumbnail_size

	#the image is smaller than the minimum thumbnail dimensions
	if x < th_x and y < th_y:
		return image

	if x > y: #wide image
		im = square_wide_image(image)
	elif x < y: #tall image
		im = square_tall_image(image)
	else: #it's already square
		im = image

	if im.mode != "RGB":
		im = im.convert('RGB')

	im.thumbnail(thumbnail_size, Image.ANTIALIAS)

	return im

def image_entropy(img):
	"""calculate the entropy of an image"""
	hist = img.histogram()
	hist_size = sum(hist)
	hist = [float(h) / hist_size for h in hist]
	return -sum([p * math.log(p, 2) for p in hist if p != 0])

def square_wide_image(img):
	x,y = img.size
	while x > y:
		#slice 10px at a time until square
		slice_width = min(x - y, 10)
		right = img.crop((x-slice_width, 0, x, y))
		left = img.crop((0, 0, slice_width, y))

		#remove the slice with the least entropy
		if image_entropy(left) < image_entropy(right):
			img = img.crop((slice_width, 0, x, y)) #crop the left side
		else:
			img = img.crop((0,0,x-slice_width, y)) #crop the right side

		x,y = img.size

	return img

def square_tall_image(img):
	"""if the image is taller than it is wide, square it off. determine
	which pieces to cut off based on the entropy pieces."""
	x,y = img.size
	while y > x:
		#slice 10px at a time until square
		slice_height = min(y - x, 10)

		bottom = img.crop((0, y - slice_height, x, y))
		top = img.crop((0, 0, x, slice_height))

		#remove the slice with the least entropy
		if image_entropy(bottom) < image_entropy(top):
			img = img.crop((0, 0, x, y - slice_height))
		else:
			img = img.crop((0, slice_height, x, y))

		x,y = img.size

	return img

##################
#End PyCrop      #
##################


def colorFilter(img, colorTo):
	pix = img.load()
	coordX = -1
	coordY = 0
	sizeX = img.size[0]
	size = img.size[0] * img.size[1]
	for x in range(size):
		coordX = coordX + 1
		if coordX >= sizeX:
			coordY = coordY + 1
			coordX = 0
		p = pix[coordX, coordY]

		color = ((colorTo[0] + p[0]) / 2, (colorTo[1] + p[1]) / 2, (colorTo[2] + p[2]) / 2)

		pix[coordX, coordY] = color

def averageColor(img):
	pix = img.load()
	coordX = -1
	coordY = 0
	sizeX = img.size[0]
	size = img.size[0] * img.size[1]
	red = []
	green = []
	blue = []
	for x in range(size):
		coordX = coordX + 1
		if coordX >= sizeX:
			coordY = coordY + 1
			coordX = 0
		p = pix[coordX, coordY]
		red.append(p[0])
		green.append(p[1])
		blue.append(p[2])
	return (sum(red) / len(red), sum(green) / len(green), sum(blue) / len(blue))

def generateImage(img, listOfImages):
	img = img.convert('RGB')
	if imgHeight > 1: # The big image needs to be scaled
		w = img.size[0]
		h = img.size[1]
		ratio = float(imgHeight) / h
		img = img.resize((int(round(h * ratio)), int(round(w * ratio))))
	for listIndex, listImg in enumerate(listOfImages):
#		listOfImages[listIndex] = listImg.resize((blockSize, blockSize)).convert('RGB')
		# No need to convert to RGB as pycrop already does so
		listOfImages[listIndex] = prepare_image(listImg, (blockSize, blockSize))
	prefWidth = img.size[0]
	prefHeight = img.size[1]
	prefWidth = int(math.floor(prefWidth / blockSize) * blockSize)
	prefHeight = int(math.floor(prefHeight / blockSize) * blockSize)
	img = img.crop((0, 0, prefWidth, prefHeight))
	blockCount = (prefWidth / blockSize) * (prefHeight / blockSize)
	blocksX = prefWidth / blockSize;
	coordX = -1
	coordY = 0
	listIndex = -1
	foundColors = {}
	blockList = []

	if matchType == 1: #Find best color-matching image in list
	#TODO: make this work
		for x in range(blockCount):
			coordX = coordX + 1
			listIndex = listIndex + 1
			if coordX >= blocksX:
				coordY = coordY + 1
				coordX = 0
			if listIndex >= len(listOfImages):
				listIndex = 0
			rect = (coordX * blockSize, coordY * blockSize, coordX * blockSize + blockSize, coordY * blockSize + blockSize)
			block = img.crop(rect)
			blockColor = averageColor(block)
			if blockColor[0] >= 250 and blockColor[1] >= 250 and blockColor[2] >= 250:
				continue
			newBlock = listOfImages[listIndex].copy()
			colorFilter(newBlock, blockColor)
			img.paste(newBlock, rect)
		return img

	if matchType == 0 or matchType == 2: #Loop through the list or pick a random (check later in the loop)
		if not seed == -1:
			random.seed(seed)
		for x in range(blockCount):
			coordX = coordX + 1
			listIndex = listIndex + 1
			if coordX >= blocksX:
				coordY = coordY + 1
				coordX = 0
			if listIndex >= len(listOfImages):
				listIndex = 0
			rect = (coordX * blockSize, coordY * blockSize, coordX * blockSize + blockSize, coordY * blockSize + blockSize)
			block = img.crop(rect)
			blockColor = averageColor(block)
			if blockColor[0] >= 250 and blockColor[1] >= 250 and blockColor[2] >= 250:
				continue
			if matchType == 0: #Pick a random
				newBlock = listOfImages[random.randrange(0, len(listOfImages))].copy()
			else: #Pick next image in the list
				newBlock = listOfImages[listIndex].copy()
			colorFilter(newBlock, blockColor)
			img.paste(newBlock, rect)
		return img
