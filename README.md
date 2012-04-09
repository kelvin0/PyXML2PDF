What is PyXML2PDF?
==================
PyXML2PDF is a pure python module that can generate PDF files from XML.
It can be used with the command line or integrated in a python application.
PyXML2PDF allows to generate pixel precise PDF documents in any page size. 
It can generate very complex pages while being easily edited as an XML file.

PyXML2PDF wraps over the excellent Reportlab python module to generate PDFs.
All PyXML2PDF does is to bring an XML semantic to the concepts used in Reportlab.
Instead of having to code your PDFs using Reportlab modules, you simply write
easily maintainable PyXML2PDF files which in turn generate PDF pages.

We have been using this module in healthcare applications for 3 years now,
and have had great results. Performance is adequate, however it certainly can
be optimised for greater speed.

__Ease of use__:
Anyone who knows some basic HTML/XML concepts will be able to use PyXML2PDF within minutes.

__Snapping elements__: Elements can be positionned relative to one another to create intricate tables.
[Check the details of this feature](https://github.com/kelvin0/PyXML2PDF/wiki/Snapping-elements-together).

__Styles (CSS)__:
PyXML2PDF supports the concepts of a simple CSS implementation.
This allows for flexibility and decoupling of content/appearance (like HTML).

__HTML__:
PyXML2PDF is NOT compatible with any XHTML/HTML/CSS. It uses a small set of tags
to quickly allow generation of PDFs.

__PyXML2PDF Tags__:
Please refer to the list of tags in the 'Reference' section (below)

__Scripting/Templating/Dynamic content__:
PyXML2PDF does not include a templating language for dynamically generating 
XML files. But you can use any templating tool or other method to generate 
XML files which can then be fed to PyXML2PDF in order to generate a PDF.
We have been successfully using Genshi as a templating engine.

__Reporting__:
PyXML2PDF is not a reporting engine. Rather it could be part of the backend 
for an existing reporting engine to help generate PDFs.

__Language support__:
PyXML2PDF supports UTF8, but all language specific stuff should be handled by
whoever generates the XML. In our case, we use Genshi and python language tools
to generate our PyXML2PDF files in several languages.


Platforms
---------
* Windows (tested)
* Linux (tested)
* Mac should also work (untested)
* Anywhere you can get Python/Reportlab to work.


Licensing
---------
BSD License ( http://www.opensource.org/licenses/bsd-license.php )


Dependencies
------------
* Python 2.x
* Reportlab ( http://www.reportlab.com/software/opensource/rl-toolkit ) 
* lxml ( http://lxml.de/ )


Installation
-------------
Simply run the following command within root directory of the project:

	python setup.py install

    
Using PyXML2PDF
-------------
###Command line:
    python xml2pdf.py -f input.xml out.pdf

###In your python code:
    from PyXML2PDF import xml2pdf
    xml2pdf.genpdf(in_xml_filename, out_pdf_filename)

    
-----------------------------------------------------
Tutorial
=========

1) Create an xml file named 'sample.xml'. Paste the following in it then save it.

    <rlxml>
	<head>
		<styles>
			<style name="redhot">
				border:4.0;
				color:red;
			</style>
			<style name="thinblue">
				border:1.0;
				color:blue;
			</style>
			<style name="normal">
				font-size:10;
				top-padding:0.5;
				left-padding:0.5;
				height:11;
			</style>
		</styles>		
	</head>
	
	<body>
		<rlbox id="bigbox" posx="100" posy="120" width="100" height="200" class="redhot"/>
		
		<rlbox id="smallbox" width="40" height="20" snapto="bigbox|C|NW"/>
		
		<rlline posx="450" posy="230" endx="600" endy="10" class="thinblue" />
		
		<p width="40" height="20" background-color="white" class="normal" snapto="bigbox|C|C">
		BigBox
		</p>
		
		<pagebreak/>
	</body>
	</rlxml>

3) In the same directory as 'sample.xml' , create a file named 'sample.py'. 
Put the following code in the sample.py and save it.

	import os
	from PyXML2PDF import xml2pdf
	from reportlab.pdfbase.ttfonts import TTFont
    
	xml = os.path.abspath('./sample.xml')
	pdf = os.path.abspath('./sample.pdf')
	
	xml2pdf.genpdf(xml,pdf)
	
	# Show the PDF (this line optionnal)
	os.system('call %s'%(pdf))

4) From the command line in the same directory as the 'sample.py' file, type:
   (assuming python is installed and in path)
   
	python sample.py
	
	
-----------------------------------------------------
Reference
=========
[All XML tags] (https://github.com/kelvin0/PyXML2PDF/wiki/Reference:-XML-tags)

[All XML attributes] (https://github.com/kelvin0/PyXML2PDF/wiki/Reference:-XML-attributes)


