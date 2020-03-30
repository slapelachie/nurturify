import argparse
import sys
import logging
import re

from nurture import nurture
from utils import logger

# Setup the logger
log = logger.setup_logger(__name__, logging.WARNING, logger.defaultLoggingHandler())

def get_args():
	"""List of all arguments supported"""

	arg = argparse.ArgumentParser(description="Resize pictures")

	arg.add_argument('-i', metavar='/path/to/file',
		help="Input file")

	arg.add_argument('-o', metavar="/path/to/file",
		help='Output file')

	arg.add_argument('-c', metavar="int",
		help="Percentage to cut off")

	arg.add_argument('-t', metavar="",
		help="Way to cut")

	arg.add_argument('-b', metavar="radius",
		help="The amount to blur the original image")

	arg.add_argument('-m', metavar="string",
		help="The message to include in the banner")

	arg.add_argument('-v', action="store_true",
		help="Verbose logging")

	return arg

def parse_args(parser):
	"""
	Parses arguments specified by the parser
	
	Arguments:
		parser (idk): The parser to be used
	"""
	args = parser.parse_args()

	# If the amount of parsed arguments are less then 1, print the help
	if len(sys.argv) <= 1:
		parser.print_help()
		sys.exit(1)

	# If the image argument has been passed
	# This is required and the program will not work without it
	if args.i:
		nurture.generate(args.i, args.o, args.c, args.t, args.b, args.m, args.v,)
	else:
		log.warning("Argument -i needs to be specified.")
		parser.print_help()
		sys.exit(1)

def main():
	parser = get_args()
	parse_args(parser)

if(__name__ == "__main__"):
	main()