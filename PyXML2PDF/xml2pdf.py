import os
import sys
import time
import docbase
import rlxmlparser
import rlrenderer
from optparse import OptionParser


def consoleprint(msg):
	print msg

def devnull(msg):
	pass

def genpdf(xml_filename, pdf_filename, **kwargs):	
	root = rlxmlparser.parser(xml_filename)
	rlrenderer.render(root, pdf_filename, **kwargs)
	return pdf_filename

def main(argv, stdout=None):
	consoleout = devnull
	if stdout is not None:
		consoleout = stdout

	usage = "Usage: %prog [options] outputfile"
	parser = OptionParser(usage)
	parser.set_defaults(input_file=None,
		                input_parser='rlxmlparser',
		                output_generator='rlrenderer')

	parser.add_option("-f", "--file", dest="input_file",
		              help="Generate a pdf from an input document description file")

	parser.add_option("-p", "--intype", dest="input_parser",
		              help="How to interpret input file (xml==>rlxml...)", 
	                  choices=["rlxmlparser"])

	parser.add_option("-o", "--outtype", dest="output_generator",
		              help="What type of file is generated (pdf==>rlrenderer)", 
	                  choices=["rlrenderer"])

	(options, args) = parser.parse_args(argv)

	if len(args) < 2:
		consoleout("need to output file")
		return -1,''

	moduleNames = ['%s'%(options.input_parser), 
		           '%s'%(options.output_generator)]

	if not os.path.exists(options.input_file):
		consoleout("Error: cannot access file (%s)"%(options.input_file))
		return -1,''
	try:
		modules = map(__import__, moduleNames)
	except Exception, expt:
		consoleout("Error importing modules (%s) (%s) %s"%(moduleNames[0],
		                                                   moduleNames[1],
		                                                   expt))
		return -1,''

	root = sys.modules[moduleNames[0]].parser(options.input_file)        
	generated_pdf = args[1]        
	sys.modules[moduleNames[1]].render(root, generated_pdf, args)

	return 0,generated_pdf


if __name__ == '__main__':
	res, pdf = main(sys.argv,consoleprint)
	sys.exit(res)