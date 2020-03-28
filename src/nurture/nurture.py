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
from PIL import ImageFilter

# Setup the required loggers
log = logger.setup_logger(__name__+'.default', logging.WARNING, logger.defaultLoggingHandler())

FNULL = open(os.devnull, 'w')

def generate(file, output_arg, percent, type_cut, blur, verbose):
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

	# Make required directories (these should have already been created in install)
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
	
	# Check if the percentage parsed is valid
	if not percent:
		percent = 30
	elif not percent.isdigit():
		log.critical("%s is not a valid percentage! Exiting...", percent)
		sys.exit(1)

	# Uppercase the parsed argument for the type of cut
	if type_cut:
		type_cut = type_cut.upper()
	
	# If the percentage is not parsed, auto sets it. If it is but is not valid exit the program
	if not type_cut:
		type_cut = "BOTTOM_HORIZONTAL"
	elif not type_cut == "BOTTOM_HORIZONTAL"\
		and not type_cut == "TOP_HORIZONTAL"\
		and not type_cut == "LEFT_VERTICAL"\
		and not type_cut == "RIGHT_VERTICAL":
			log.critical("%s is not a valid cutting method! Exiting...", type_cut)
			sys.exit(1)
	
	# Convert the percentage into a decimal
	percent_cut = int(percent)/100

	image = utils.get_image(file)

	# Get all scribbles from data dir
	scribbles = [f for f in os.listdir(scribble_dir)
		if re.match(r'scribble_[0-9]{2}.png', f)
			and os.access(os.path.join(scribble_dir, f), os.F_OK)]

	# Pick a random scribble
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

	textbox_size = (width, int(height*(1/20)))
	cut_width = width
	cut_height = height

	# Get random info message information
	mod_date = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(image)))
	mod_time = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(image)))
	msg = ("35°39′34″N | 139°42′02″E | filename: " + os.path.basename(image) + " date: " + mod_date + " time: " + mod_time + 
		" color space: " + img.mode + " width: " + str(width) + " height: " + str(height) + " | ")
	msg = msg + msg 

	#Load the font
	font = ImageFont.truetype(os.path.expanduser("~/.fonts/opensans.ttf"), 33)

	# Make the background (black) image and the textbox (black) image
	background = Image.new('RGBA', (width, height), (0, 0, 0, 255))
	text_box = Image.new('RGBA', textbox_size, (0, 0, 0, 255))

	# Add text to the text box
	draw = ImageDraw.Draw(text_box)
	text_size = draw.textsize(msg, font=font)
	draw.text((10, int((textbox_size[1]- text_size[1])/2)), msg, (255,255,255), font=font)

	# Basically depending on the orientation the crop of the image will be different and hence
	# a different crop, offset, and position needs to be applied
	if type_cut == "TOP_HORIZONTAL":
		# How much of the original image should be cut and where
		cut_height = height * percent_cut
		crop = (0, cut_height, width, height)
		offset = (0, int(cut_height)) 

		# The locations for the textbox and scribbles
		textbox_pos = (0, int(cut_height))
		scribble_pos = (0, 0)

		# Draw the scribble, but rotate it first
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

		# Rotate the textbox and everything written to it
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
			# Crop the image to the bounds
			img_top = img.crop(crop)
			if blur:
				if blur.isdigit():
					img_top = img_top.filter(ImageFilter.GaussianBlur(int(blur)))
				else:
					log.warning("Blur is not a valid integer, proceeding without blur...")

			# Combine the image, textbox and random scribble to make one image.
			background.paste(img_top, offset)
			background.paste(text_box, textbox_pos)
			background.paste(random_scribble, scribble_pos, random_scribble)

			# Save the output to a file
			background.save(output_name)
	except:
		raise
	