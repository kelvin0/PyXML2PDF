import os
import sys
import copy
import docbase
from docbase import getattrvalue_int, getattrvalue_float, getnamedstyle, getdefaultstyle
from lxml import etree
from lxml import objectify


class rltag:        
	"""
	Base class representing XML tags within the document to be rendered.
	Basically we build an abstract representation of a element to be rendred.
	The abstraction are made with all docElements (and its derivates class)
	instances
	"""
	def __init__(self, data):
		self._tagname = data.tag
		self._children = []
		self._parent = None
		self._tagobject = data      
		self._baseelement = None                
		self._id = data.get('id')                
		stylename = data.get('class')

		self._style = docbase.docStyle('',None)
		if stylename is not None:
			self._style.copy(getnamedstyle(stylename))

		for attr_name in self._style._style_dict:
			attr_name = attr_name.lower()
			attr_value = data.get(attr_name)
			if attr_value is not None:
				self._style.setattribute(attr_name, attr_value)                

		xmlattr_align = self._tagobject.get('align')
		if xmlattr_align is not None:
			self._style.setattribute('text-align',xmlattr_align)

		self._setelement(docbase.docElement())

	def _initrect(self):
		"""
		This is optionnally called by classes which implement
		rendering of a docElement to be positionned onto canvas.

		We need to determine if the object to be rendered is bound
		to a rect area. We also cache the info pertainng to its
		positionning onto canvas (absolute, relative to another object)                
		"""                
		x = self._style.getattribute('posx', float)
		y = self._style.getattribute('posy', float)
		if x is None or y is None:
			snapto = self._style.getattribute('snapto',str)
			if snapto is not None:
				snapdata = snapto.strip().split('|')
				self._baseelement.setanchor(snapdata[0], snapdata)
		else:
			x = float(x)
			y = float(y)

		width = self._style.getattribute('width', float)
		height = self._style.getattribute('height', float)

		if width is not None and height is not None:
			self._baseelement.setrect(x,y,float(width),float(height))
		return [x,y,width,height]

	def finalize(self):
		"""
		This is called once ALL children of a XML tag have been finalized
		"""
		pass

	def setparent(self, parent):
		if self._parent is None:
			self._parent = parent
			if parent is not None:
				parent.addchild(self)                                
				self._baseelement.setparent(parent._baseelement)

	def addchild(self, child):
		self._children.append(child)                

	def getchildren(self):
		return self._children

	def getdocElement(self):
		return self._baseelement

	def _setelement(self, element):
		if self._baseelement is not None:
			del self._baseelement

		self._baseelement = element
		self._baseelement.setid(self._id)                                        
		self._baseelement.setstyle(self._style)
		self._initrect()


class rltagSTYLE(rltag):        
	"""
	This a class representing the 'CSS' mechanism we chose to implement
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)  
		stylename = self._tagobject.get('name')
		self._setelement(docbase.docStyle(stylename, self._tagobject.text))
		self._baseelement.setstyle(None)


class rltagTR(rltag):
	"""
	A table row
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)
		self._cols = None

	def finalize(self):

		if self._parent is not None:
			self._parent.addrow(self)

	def addcolumn(self, coltag):

		if self._cols is None:
			self._cols = []
		self._cols.append(coltag)


class rltagP(rltag):
	"""
	A text object
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)
		self._setelement(docbase.docText(self._tagobject.text))

	def finalize(self):
		pass


class rltagTD(rltag):    
	"""
	A table column
	"""
	def __init__(self, data):                
		rltag.__init__(self, data)                

	def finalize(self):

		if len(self._children) == 0:
			self._setelement(docbase.docText(self._tagobject.text))
		else:
			pass

		if self._parent is not None:
			self._parent.addcolumn(self)


class rltagTH(rltagTD):               
	pass


class rltagIMG(rltag):
	"""
	An image
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)

		height = self._style.getattribute('height',float)
		width = self._style.getattribute('width',float)
		url = self._style.getattribute('src',str)                
		self._setelement(docbase.docImage(url, height, width))


class rlPAGEBREAK(rltag):
	"""
	Page break
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)
		self._setelement(docbase.docPagebreak())


class rlFRAME(rltag):
	"""
	Frame
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)                

		height = self._style.getattribute('height',float)
		width = self._style.getattribute('width',float)
		x = self._style.getattribute('posx',float)
		y = self._style.getattribute('posy',float)

		self._setelement(docbase.docFrame(x, y, width, height))


class rltagRLCELL(rltag):
	"""
	TODO:
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)


class rltagRLTABLE(rltag):
	"""
	TODO:
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)
		self._setelement(docbase.docTable())


class rlBOX(rltag):

	def __init__(self, data):                

		rltag.__init__(self, data)
		self._setelement(docbase.docGeoBox())


class rlLINE(rltag):

	def __init__(self, data):                

		rltag.__init__(self, data)                                

		from_x = self._style.getattribute('posx',float)
		from_y = self._style.getattribute('posy',float)
		to_x = self._style.getattribute('endx',float)
		to_y = self._style.getattribute('endy',float)
		self._setelement(docbase.docGeoLine((from_x, from_y),(to_x,to_y)))


class rlELLIPSE(rltag):

	def __init__(self, data):                

		rltag.__init__(self, data)                                

		from_x = self._style.getattribute('posx',float)
		from_y = self._style.getattribute('posy',float)
		rx = self._style.getattribute('rx',float)
		ry = self._style.getattribute('ry',float)
		self._setelement(docbase.docGeoEllipse((from_x, from_y),(rx,ry)))


class rlTRANSFORM(rltag):

	def __init__(self, data):                

		rltag.__init__(self, data)
		self._setelement(docbase.docGeoTransform(self._tagobject.get('transform')))


class rltagTABLE(rltag):        
	"""
	XML representation of a table container
	"""
	def __init__(self, data):                

		rltag.__init__(self, data)
		self._rows = None
		self._numrows = 0
		self._numcols = 0
		self._width = self._style.getattribute('width',float)
		self._height = self._style.getattribute('height',float)                
		self._setelement(docbase.docTable())

	def addrow(self, rowtag):

		if self._rows is None:
			self._rows = []

		self._rows.append(rowtag)
		self._numrows = len(self._rows)

		cur_row = []                
		cur_num_cols = 0                

		for cell in rowtag._cols:                        
			rowspan = getattrvalue_int(cell._tagobject, 'rowspan', 1)
			colspan = getattrvalue_int(cell._tagobject, 'colspan', 1)                                                        
			cur_num_cols += colspan                        
			cur_row.append(rowspan*[colspan*[cell._baseelement]])

		self._baseelement.addrowcells(cur_row)
		if cur_num_cols > self._numcols:
			self._numcols = cur_num_cols


	def finalize(self):

		if self._rows is None:
			return

		if self._width is None:
			colwidths = self._numcols*[None]
		else:
			colwidths = self._numcols*[self._width/self._numcols]

		if self._height is None:
			rowheights = self._numrows*[None]
		else:
			rowheights = self._numrows*[self._height/self._numrows]

		self._baseelement.setdimensions(colwidths, rowheights, self._width, self._height)                

	def getgriddata(self):
		return self._grid                


CLASS_RLXMLTAGS = {'rlxml':rltag,\
                   'rlframe':rlFRAME,\
                   'rlbox':rlBOX,\
                   'rlline':rlLINE,\
                   'rlellipse':rlELLIPSE,\
                   'rltransform':rlTRANSFORM,\
                   'pagebreak':rlPAGEBREAK,\
                   'head':rltag,\
                   'body':rltag,\
                   'comment':rltag,\
                   'styles':rltag,\
                   'style':rltagSTYLE,\
                   'table':rltagTABLE,\
                   'rltable':rltagRLTABLE,\
                   'rlcell':rltagRLCELL,\
                   'tr':rltagTR,\
                   'td':rltagTD,\
                   'p':rltagP,\
                   'img':rltagIMG,\
                   'th':rltagTH }


def buildtagobject(parentobject, node, func_params):
	tagname = node.tag.lower()
	try:
		klass = func_params[tagname]
	except:
		print "Uknown tag (%s)"%(tagname)
		return None

	tagobject = klass(node)
	tagobject.setparent(parentobject)
	return tagobject


def walk(parentnode, node, func, func_params):      

	tagobject = func(parentnode, node, func_params)
	children_list = node.iterchildren()        
	for childnode in children_list:
		tagchild = walk(tagobject, childnode, func, func_params)                

	if tagobject is None:
		return None

	tagobject.finalize()        
	return tagobject


def parser( xmldata ):        

	if len(xmldata) < 255 and os.path.exists(xmldata):
		datafile = file(xmldata,'rb')
		data = datafile.read()
		datafile.close()
	else:
		data = unicode(xmldata,'utf8')

	tree = objectify.fromstring(data)            
	root = tree.getroottree().getroot()
	objectsroot = walk(None, root, buildtagobject, CLASS_RLXMLTAGS) 
	return objectsroot.getdocElement()


def main(argv):
	if len(argv) > 1:
		return rlxmlparser(argv[1])                
	return None


if __name__ == '__main__':
	sys.exit(main(sys.argv))