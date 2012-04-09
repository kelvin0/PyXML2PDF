import copy

DFLT_STYLE_DICT = {'background-color':None,
                   'border':0.0,
                   'border-color':'black',
                   'bottom-padding':0.0,
                   'color':'black',                   
                   'endx':None,
                   'endy':None,                   
                   'font':'Times-Roman',
                   'font-size':10,
                   'font-style':'normal',
                   'font-weight':'normal',              
                   'frame':'void',                                      
                   'grid':0.0,
                   'height':None,
                   'id':None,
                   'leading':12.0,
                   'left-padding':0.0,
                   'orientation':'portrait',
                   'pagesize':'letter',
                   'posx':None,
                   'posy':None,
                   'rx':None,
                   'ry':None,
                   'right-padding':0.0,
                   'src':None,
                   'snapto':None,
                   'text-align':'left',
                   'top-padding':0.0,
                   'transform':None,
                   'vertical-align':'top',
                   'width':None,
                   'wrap':0,                   
                   }

DFLT_STYLE = None

REGISTERED_STYLES = {}


def getnamedstyle(stylename):
	try:
		return REGISTERED_STYLES[stylename.lower()]
	except:
		return getdefaultstyle()


def getattrvalue_int( node, attr_name, default_value ):    
	try:
		return int(node.get(attr_name))
	except:
		pass
	return default_value    

def getattrvalue_float( node, attr_name, default_value ):    
	try:
		return float(node.get(attr_name))
	except:
		pass
	return default_value    


def getdefaultstyle():
	global DFLT_STYLE
	if DFLT_STYLE is None:
		DFLT_STYLE = docStyle('dflt', None)
		DFLT_STYLE._style_dict = copy.deepcopy(DFLT_STYLE_DICT)
	return DFLT_STYLE


class docElement:

	def __init__(self):
		self._children = []
		self._parent = None
		self._style = None
		self._id = None
		self._anchor = None
		self._anchor_data = None
		self._rect = None

	def addchild(self, child):
		self._children.append(child)

	def getchildren(self):
		return self._children

	def setparent(self, parent):
		if self._parent is None:
			self._parent = parent
			if parent is not None:
				parent.addchild(self)

	def setid(self, myid):
		self._id = myid

	def getid(self):
		return self._id

	def setstyle(self, style):
		self._style = style

	def getstyle(self):
		return self._style

	def getrect(self):
		return self._rect

	def setrect(self, x, y, width, height ):
		self._rect = [x,y,width,height]

	def setanchor(self, anchor_id, anchor_data):
		self._anchor = anchor_id
		self._anchor_data = anchor_data

	def getanchor(self):
		return self._anchor, self._anchor_data


class docPagebreak(docElement):
	pass


class docFrame(docElement):

	def __init__(self, x, y, width, height):

		docElement.__init__(self)
		self._x = x
		self._y = y
		self._width = width
		self._height = height


class docStyle(docElement):

	def __init__(self, stylename, styledata):

		docElement.__init__(self)
		self._style_dict = copy.deepcopy(DFLT_STYLE_DICT)
		if stylename is None:
			print "Style with no name!"
			return
		self._name  = stylename.lower()

		if styledata is None:
			return

		style_attrs = styledata.strip().lower().split(';')
		for attr in style_attrs:
			if len(attr) > 0:
				key, val = attr.split(':')
				self._setattribute(key, val)

		REGISTERED_STYLES[stylename] = self

	def copy(self, source):
		self._name = copy.deepcopy(source._name)
		self._style_dict = copy.deepcopy(source._style_dict)

	def _setattribute(self, key, val):
		try:
			curval = self._style_dict[key.strip()]
			if isinstance(curval, int):
				self._style_dict[key.strip()] = int(val.strip())
			elif isinstance(curval, float):
				self._style_dict[key.strip()] = float(val.strip())
			else:
				self._style_dict[key.strip()] = str(val.strip())
		except:
			self._style_dict[key.strip()] = ''

	def getattribute(self, attrname, attrtype):

		try:
			val = attrtype(self._style_dict[attrname.lower()])
			if attrtype == str:
				return val.lower()
			return val
		except:
			return None

	def setattribute(self, key, value):

		self._setattribute(key, value)


class docTableCell(docElement):
	pass


class docTable(docElement):

	def __init__(self):

		docElement.__init__(self)
		self._colwidths = None
		self._rowheights = None
		self._rows = []
		self._width = None
		self._height = None

	def getdimensions(self):

		return self._colwidths, self._rowheights

	def setdimensions(self, colwidths, rowheights, width, height):

		self._rowheights = rowheights
		self._colwidths = colwidths
		self._width = width
		self._height = height

	def getrowcells(self):

		return self._rows

	def addrowcells(self, row_cells):        

		self._rows.append(row_cells)


class docText(docElement):

	def __init__(self, text):

		docElement.__init__(self)        

		if text is None:
			self._text = ''
		else:
			self._text = text.strip()

	def gettext(self):

		return self._text


class docImage(docElement):

	def __init__(self, src, height, width):

		docElement.__init__(self)
		self._height = height
		self._width = width
		self._src = src


class docGeoBox(docElement):
	pass


class docGeoEllipse(docElement):

	def __init__(self, pos_xy, r_xy):

		docElement.__init__(self)
		self._fromxy = pos_xy
		self._rxy = r_xy

	def getellipse(self):
		return self._fromxy, self._rxy


class docGeoLine(docElement):

	def __init__(self, from_pt, to_pt):

		docElement.__init__(self)
		self._fromxy = from_pt
		self._toxy = to_pt

	def getline(self):
		return self._fromxy, self._toxy


class docGeoTransform(docElement):

	def __init__(self, transform ):

		docElement.__init__(self)
		self._tranform = transform

	def gettransform(self):
		return self._tranform



