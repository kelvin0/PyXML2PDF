What is PyXML2PDF?
==================
PyXML2PDF is a pure python module that can generate PDF files from XML.
It can be used with the command line or integrated in a python application.
PyXML2PDF allows to generate pixel precise PDF documents in any page size. 
It can generate very complex pages while being easily edited as an XML file.

PyXML2PDF wraps over the excellent Reportlab python module to generate PDFs
All PyXML2PDF does is to bring an XML semantic to the concepts used in Reportlab.
Instead of having to code your PDFs using Reportlab modules, you simply write
easily maintainable PyXML2PDF files which in turn generate PDF pages.

We have been using this module in healthcare applications for 3 years now,
and have had great results. Performance is adequate, however it certainly can
be optimised for greater speed.

__Ease of use__:
Anyone who knows some basic HTML/XML concepts will be able to use PyXML2PDF within minutes.

__Styles (CSS)__:
PyXML2PDF supports the concepts of a simple CSS implementation.
This allows for flexibility and decoupling of content/appearance (like HTML).

__HTML__:
PyXML2PDF is NOT compatible with any XHTML/HTML/CSS. It uses a small set of tags
to quickly allow generation of PDFs.

__PyXML2PDF Tags__:
Please refer to the list of tags in the 'Reference' section (below)

__Templating__:
PyXML2PDF does not include a templating language for dynamically generating 
XML files. But you can use any templating tool or other method to generate 
XML files which can then be fed to PyXML2PDF in order to generate a PDF.
We have been successfully using Genshi as a templating engine.

__Reporting__:
PyXML2PDF is not a reporting engine. Rather it could be used as a backend 
for an existing reporting engine, providing it could generate PyXML2PDF layouts.

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
[WIP]



-----------------------------------------------------
Reference
=========
### Special variables : #PAGE# and #TOTALPAGES##
These variable can be inserted freely in the XML document to specifiy the 
current page number and the totalnumber of pages (respectively).

### Coordinates and units
The coordinate system has (0,0) as the top left of each page.
The units used to specify coordinates and size correspond to 72 points/inch. 
For example a 8.5" x 11" page is 8.5*72 = 612 and 11*72 = 792 (612x792).

### All Tags
All tags described here support the attributes 'id' and 'class'

### &lt;rlxml&gt;
This tag must be the root of the XML document.

Attributes:
pagesize="page_width:page_height", orientation="portrait" (or "landscape")

### &lt;rlframe&gt;    
Frames are a concept used in Reportlab. They are containers in which
other elements can reside. Elements within a frame cannot have posx
and posy attributes, they are positionned in a 'flow' within the frame.

Attributes:
posx, posy, height, width

### &lt;rlbox&gt;
Draws a box.

Attributes:
posx, posy, height, width, background-color, border, color, snapto

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
All elements within the tranform tags will be tranformed accordingly.
Transforms can be nested, to compose more complex transformations as needed.

Attributes:
transform = "rotate:degrees"    or 
...       = "translate:tx:ty"   or 
...       = "scale:multx:multy"

### &lt;head&gt;
Has no effect on the visual appearance of generated PDF. Simply a way to 
partition the XML content. It is recommened the 'style(s)' tags be declared
within the 'header'.
    
Attributes: None
    
### &lt;body&gt;
Has no effect on the visual appearance of generated PDF. Simply a way to 
partition the XML content.

Attributes: None

### &lt;pagebreak&gt;
This tag is ESSENTIAL in telling PyXML2PDF where each page ends. Otherwise, the
generated PDF will be a blank page. It should be placed at the end of each page
that needs to be part of the PDF.

Attributes: None

### &lt;styles&gt;
This tag should be used in 'header'. It is simply a way to contain 'style' tags.

Attributes: None

### &lt;style&gt;
This tag allows to create a named style. Each style can have specific attributes
(font, color, height ...) which can be applied to a specific tag to modify it's
appearance. If an attribute is also specified within a tag, it overrides the 
same attribute for the style used for that tag.

Attributes:
name

### &lt;p&gt;
This tags allow to create a textfield (paragraph). The text will be truncated
by default if it is larger than the width. However, the 'wrap' attribute can
be used to wrap the text within the width specified. All newline (\n) characters 
within this tag's text will be render as so in PDF document .

Attributes:
background-color, font-weight, font-style, leading, color,wrap, text-align, 
posx, posy, height, width, snapto

### &lt;img&gt;
This tag allows inserting images within the PDF document.
    
Attributes:
border, border-color, posx, posy, height, src, width, snapto

All tag attributes
------------------
###Color definition

By description: red,blue,brown,cyan ... (see reportlab\lib\colors.py)
    
By RGB (#RRGGBB): #DE22FF, #AA00CC, #123456

###Fonts
Default Reportlab fonts are: Times-Roman, Courier, Helvetica, Symbol, ZapfDingbats

If you need to use additional fonts:
    
    from reportlab.pdfbase.ttfonts import TTFont
    arial_ttf = TTFont('Arial Black', 'ArialBD.TTF')
    comic_ttf = TTFont('Comic', 'comic.TTF')
    xml2pdf.genpdf(xml_filename, pdf_filename, fonts=[arial_ttf,comic_ttf])
    
- make sure they are available on your system. 

- you might also need to configure reportlab to find your system fonts

- Lastly, register the fonts within the genpdf(...fonts=[..,..,..]) call.

    
###background-color
Background color

__Example:__ background-color="red", background-color="#FFAABB"


###border
Border thickness 

__Example:__ border="2.0", border="3.5"


###border-color
Border color

__Example:__ border-color="red", border-color="gray"


###bottom-padding
The padding to be inserted bewteen the element and it's boundary rectangle defined
by posx, posy, width, height.

__Example:__bottom-padding="2.0"


###color
The color of a graphical element

__Example:__ color="red", color="#AABBCC"


###endx
The ending x coordinate for an element

__Example:__ endx="223"


###endy
The ending y coordinate for an element

__Example:__ endy="678"


###font
The font name to be used. 

__Example:__ font="Courier"


###font-size
The size of the font to be used.

__Example:__ font-size="12"


###font-style
This specifies a modifier for the font

__Example:__ font-style="italic" (or "underline")


###font-weight
This specifies if you want a bold typeface or not.

__Example:__ font-weight="bold"


###height
Specifies the Height of the element

__Example:__ height="20"


###id
This is an identifier for the tag element. It can be any alphanumeric string.
It does not need to be unique within the xml file, and this id will always refer
to the last tag element having this id.

__Example:__ id="bigbox", id="textfield_001"


###left-padding
The padding at the left of the text field rectangle boundary

__Example:__ left-padding="5.0"


###orientation
This specifies the orientation of the page

__Example:__ orientation="portrait" (or "lanscape")


###pagesize
This specifies the width and height of the page

__Example:__ pagesize="612:792"


###posx
This specifies the starting x coordinate

__Example:__ posx="10"


###posy
This specifies the starting x coordinate

__Example:__ posy="711"


###rx
The horizontal radius size for an ellipse. When rx=ry you get a circle.

__Example:__ rx="134"


###ry
The vertical radius size for an ellipse. When rx=ry you get a circle.

__Example:__ rx="89"


###right-padding
The padding at the right of the text field rectangle boundary

__Example:__ right-padding="5.0"


###src
The path to an image file. 

__Example:__ src="/home/john/pictures/vacation.jpg"


###snapto
This allows to position an element relatively to another. 
The attribute values should be of the form : snapto="other_element_id|pos_this_element|pos_other_element"

In this way you can snap an element onto another one. Each corner of an element's
rectangle boundary is NW, NE, SE, SW and C (center)

        NW            NE
        +-------------+
        |      C      |
        +-------------+
        SW            SE

In this manner it is possible to create complex tables quite simply by 'snapping'
various elements together. This also has the advantage that you can then tweak the
appearance of your document by simply modifiying one anchor element, instead of
having to tweak posx, posy for ALL the elements in your xml file.

When using this attribute, make sure:

- the id of the element you wish to position this relatively to exists

- do not specify posx, posy when wanting to position an element relative to another.

__Example:__ snapto="bigbox|C|C"


###text-align

__Example:__


###top-padding

__Example:__


###transform

__Example:__


###vertical-align

__Example:__


###width

__Example:__


###wrap

__Example:__

