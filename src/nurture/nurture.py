import os
import sys
import logging
import time
import random
import re

from utils import utils, logger
from PIL import Image
from PIL import ImageDraw 
from PIL import ImageFont

# Setup the required loggers
log = logger.setup_logger(__name__+'.default', logging.WARNING, logger.defaultLoggingHandler())

FNULL = open(os.devnull, 'w')

def generate(file, output_arg, percent, type_cut, verbose):
	"""
	Used to resize the image to a specific size, the way the arguments are parsed
	here are terribly done and will need to be improved in the future

	FIXME: this

	Arguments:
		file (string): The path to the file
		output (string): The path to the output file
		percent (int): the percentage to cut the image
		type_cut (string): the direction to cut the image
		verbose (boolean): If verbose logging should be enabled (log level of INFO)
	"""

	scribble_dir = os.path.join(os.getenv('XDG_DATA_HOME'), 'nurturify')
	try:
		os.makedirs(scribble_dir, exist_ok=True)
	except: raise

	# If the verbose option has been passed, set log level to INFO
	if verbose:
		log.setLevel(logging.INFO)

	# Check if the file is a file or a dir
	if os.path.isfile(file):
		images = utils.get_image(file)
	else:
		log.critical("%s is not a file! Exiting...", file)
		sys.exit(1)
	
	# If the output argument has been passed, set it to that
	if output_arg:
		output_name = output_arg
	else:
		output_name = "out.png"
	
	if not percent:
		percent = 30
	elif not percent.isdigit():
		log.critical("%s is not a valid percentage! Exiting...", percent)
		sys.exit(1)

	if type_cut:
		type_cut = type_cut.upper()
	
	if not type_cut:
		type_cut = "BOTTOM_HORIZONTAL"
	elif not type_cut == "BOTTOM_HORIZONTAL"\
		and not type_cut == "TOP_HORIZONTAL"\
		and not type_cut == "LEFT_VERTICAL"\
		and not type_cut == "RIGHT_VERTICAL":
			log.critical("%s is not a valid cutting method! Exiting...", type_cut)
			sys.exit(1)
	
	percent_cut = int(percent)/100

	image = utils.get_image(file)
	original_img_path = image		

	# Get all scribbles from data dir
	scribbles = [f for f in os.listdir(scribble_dir)
		if re.match(r'scribble_[0-9]{2}.png', f)
			and os.access(os.path.join(scribble_dir, f), os.F_OK)]

	random_scribble_num = random.randrange(len(scribbles))
	random_scribble_path = os.path.join(scribble_dir, scribbles[random_scribble_num])
	random_scribble = Image.open(random_scribble_path)

	# Try to get the dimensions of the passed image
	try:
		with Image.open(image) as img:
			width, height = img.size	
	except:
		log.critical("Could not get image info for %s", image)
		sys.exit(1)

	cut_width = width
	cut_height = height

	mod_date = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(image)))
	mod_time = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(image)))
	msg = ("35°39′34″N | 139°42′02″E | filename: " + os.path.basename(image) + " date: " + mod_date + " time: " + mod_time + 
		" color space: " + img.mode + " width: " + str(width) + " height: " + str(height) + " | ")
	msg = msg + msg 

	font = ImageFont.truetype(os.path.expanduser("~/.fonts/opensans.ttf"), 33)
	textbox_size = (width, int(height*(1/20)))

	background = Image.new('RGBA', (width, height), (0, 0, 0, 255))
	text_box = Image.new('RGBA', textbox_size, (0, 0, 0, 255))

	draw = ImageDraw.Draw(text_box)
	text_size = draw.textsize(msg, font=font)

	draw.text((10, int((textbox_size[1]- text_size[1])/2)), msg, (255,255,255), font=font)

	if type_cut == "TOP_HORIZONTAL":
		cut_height = height * percent_cut
		crop = (0, cut_height, width, height)
		offset = (0, int(cut_height)) 

		textbox_pos = (0, int(cut_height))
		scribble_pos = (0, 0)

		random_scribble = random_scribble.transpose(Image.ROTATE_90)
		random_scribble = random_scribble.resize((width, int(cut_height)))
	elif type_cut == "BOTTOM_HORIZONTAL":
		cut_height = height * percent_cut
		crop = (0, 0, width, int(height-cut_height))
		offset = (0, 0)

		textbox_pos = (0, int(height - cut_height))
		scribble_pos = (0, int(height - cut_height))

		random_scribble = random_scribble.transpose(Image.ROTATE_90)
		random_scribble = random_scribble.resize((width, int(cut_height)))
	elif type_cut == "LEFT_VERTICAL":
		cut_width = width * percent_cut
		crop = (cut_width, 0, width, height)
		offset = (int(cut_width), 0)

		textbox_pos = (int(cut_width), 0)
		scribble_pos = (0, 0)
		text_box = text_box.transpose(Image.ROTATE_90)

		random_scribble = random_scribble.resize((int(cut_width), height))

	elif type_cut == "RIGHT_VERTICAL":
		cut_width = width * percent_cut
		crop = (0, 0, width-cut_width, height)
		offset = (0, 0)

		textbox_pos = (int(width - cut_width), 0)
		scribble_pos = (int(width - cut_width), 0)
		text_box = text_box.transpose(Image.ROTATE_90)

		random_scribble = random_scribble.resize((int(cut_width), height))


	try:
		with Image.open(image) as img:	
			img_top = img.crop(crop)

			background.paste(img_top, offset)
			background.paste(text_box, textbox_pos)
			background.paste(random_scribble, scribble_pos, random_scribble)

			background.save(output_name)
	except:
		raise
	