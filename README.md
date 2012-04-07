What is XML2PDF?
----------------
XML2PDF is a pure python module that can generate PDF files from XML.
It can be used with the command line or integrated in a python application.
XML2PDF allows to generate pixel precise PDF documents in any page size. 
It can generate very complex pages while being easily edited as an XML file.

XML2PDF is a wrapper over the excellent Reportlab python module to generate PDFs
All XML2PDF does is to bring an XML semantic to the concepts used in Reportlab.
Instead of having to code your PDFs using Reportlab modules, you simply write
easily maintainable XML2PDF files which in turn generate PDF pages.

We have been using this module in healthcare applications for 3 years now,
and have had great results. Performance is adequate, however it certainly can
be optimised for greater speed.

* Ease of use:
Anyone who knows some basic HTML/XML concepts will be able to use XML2PDF within
minutes.

* Styles (CSS):
XML2PDF supports the concepts of a simple CSS implementation.
This allows for flexibility and decoupling of content/appearance (like HTML).

* HTML:
XML2PDF is NOT compatible with any XHTML/HTML/CSS. It uses a small set of tags
to quickly allow generation of PDFs.

* XML2PDF Tags:
Please refer to the list of tags in the 'Reference' section (below)

* Templating:
XML2PDF does not include a templating language for dynamically generating 
XML files. But you can use any templating tool or other method to generate 
XML files which can then be fed to XML2PDF in order to generate a PDF.
We have been successfully using Genshi as a templating engine.

* Reporting:
XML2PDF is not a reporting engine. Rather it could be used as a backend 
for an existing reporting engine, providing it could generate XML2PDF layouts.

* Language support:
XML2PDF supports UTF8, but all language specific stuff should be handled by
whoever generates the XML. In our case, we use Genshi and python language tools
to generate our XML2PDF files in several languages.


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


Using XML2PDF
-------------
###Command line:
    python xml2pdf.py -f input.xml out.pdf

###In your python code:
    >>>from xml2pdf import xml2pdf
    >>>xml2pdf.genpdf(>

    
Tutorial
--------
[WIP]

Reference
---------
### All Tags
All tags described here support the attributes 'id' and 'class'
Tags that accept 'posx','posy' are the only ones to allow 'snapto'.

### &lt;rlxml&gt;
This tag must be the root of the XML document.

Attributes:
    None

### &lt;rlframe&gt;    
Frames are a concept used in Reportlab. They are containers in which
other elements can reside. Elements within a frame cannot have posx
and posy attributes, they are positionned in a 'flow' within the frame.

Attributes:
    posx, posy, height, width
    
### &lt;rlbox&gt;
Draws a box.

Attributes:
    posx, posy, height, width, background-color, border, color
    
### &lt;rlline&gt;
Draws a line.

Attributes:
    posx, posy, endx, endy, border, color
    
### &lt;rlellipse&gt;
Draws an ellipse (or circle).

Attributes:
    posx, posy, rx, ry, border, color
    
### &lt;rltransform&gt;
Allows to transform the canvas through translations, rotations and scaling.
All elements withing the tranform tags will be tranformed accordingly.
Transforms can contain other tranforms, so they can 'accumulate' several
nested tranforms

Attributes:
    transform = "rotate:degrees"    or 
    ...       = "translate:tx:ty"   or 
    ...       = "scale:multx:multy"
    
### &lt;head&gt;

### &lt;body&gt;

### &lt;pagebreak&gt;

### &lt;comment&gt;

### &lt;styles&gt;

### &lt;style&gt;

### &lt;p&gt;

### &lt;img&gt;


All tag attributes
------------------
*background-color
*border
*border-color
*bottom-padding
*color
*endx
*endy
*font
*font-size
*font-style
*font-weight
*frame
*grid
*height
*id
*leading
*left-padding
*orientation
*pagesize
*posx
*posy
*rx
*ry
*right-padding
*src
*snapto
*text-align
*top-padding
*transform
*vertical-align
*width
*wrap

