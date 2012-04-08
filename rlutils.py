import os
import sys
import time
import datetime
import random
import locale

from reportlab.pdfgen import canvas
from reportlab.pdfgen import canvas
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase import pdfmetrics


# Snap positions used un RLFrame
FRM_SW = 0
FRM_NW = 1
FRM_NE = 2
FRM_SE = 3
FRM_CTR = 4


#------------------------
# StrIIF
#------------------------    
def StrIIF(strToClean, strInvalid, strCoalescedValue ):

	if strToClean == strInvalid:
		if strToClean is None:
			return strCoalescedValue

		if type(strToClean) is str or type(strToClean) is unicode:
			return unicode(strCoalescedValue,'utf8')

	if type(strToClean) is str:
		return unicode(strToClean,'utf8')

	return strToClean


#------------------------
# GetDateFormat
#------------------------
def GetDateFormat(win_locale_id, year, month, day, format):            

	deflang, defencode = locale.getdefaultlocale()
	if win_locale_id == 3084:
		try:
			locale.setlocale(locale.LC_TIME,'french_canada')
		except:
			locale.setlocale(locale.LC_TIME,'fr_CA')
	elif win_locale_id == 1033:
		try:
			locale.setlocale(locale.LC_TIME,'english_us')
		except:
			locale.setlocale(locale.LC_TIME,'en_US')
	elif win_locale_id == 3082:
		try:
			locale.setlocale(locale.LC_TIME,'spanish')
		except:
			locale.setlocale(locale.LC_TIME,'ES')
	else:
		try:
			locale.setlocale(locale.LC_TIME,'english_us')
		except:
			locale.setlocale(locale.LC_TIME,'en_US')

	date =  datetime.date(year,  month, day)
	strunidate = date.strftime(format)
	return unicode(strunidate,defencode)


#------------------------
# RLFrame
#------------------------
class RLFrame:
	def __init__(self, x, y, width, height ):
		self.x = x
		self.y = y      
		self.width = width
		self.height = height
		self.frame = None
		self.flowable = None
		self._padding = [0.0,0.0,0.0,0.0]
		self._border_width = 0.0
		self._border_color = None
		self._border_fill_color = None
		self._fill_border_rect = 0
		self._border_type = 1

	def getrect(self):
		return [self.x, self.y, self.width, self.height]

	def setborderinfo(self, border_color, back_color, width, fill, stroke):
		self._border_width = width
		self._border_color = border_color
		self._border_fill_color = back_color
		self._fill_border_rect = fill
		self._border_type = stroke

	def snapPosToFrame(self, frame, snapsrc, snapto, offset=None):
		#------------------------------------------------------
		# Basically the 'snapsrc' and 'snapto' indices
		# tells us which corner from the source frame should
		# snap onto which corner of the destination frame
		#------------------------------------------------------
		#  NW            NE
		# (1)           (2)
		#   +-----------+
		#   |           |
		#   +-----------+
		# (0)           (3)
		#  SW            SE
		#
		src_anchors = [(0,0),
				       (0,self.height),
				       (self.width,self.height),
				       (self.width,0),
				       (self.width/2.0,self.height/2.0)]

		dst_anchors = [(0,0),
				       (0,frame.height),
				       (frame.width,frame.height),
				       (frame.width,0),
				       (frame.width/2.0,frame.height/2.0)]

		if self.flowable is not None:
			if snapto is not None:
				self.x = frame.x+dst_anchors[snapto][0]-src_anchors[snapsrc][0]
				self.y = frame.y+dst_anchors[snapto][1]-src_anchors[snapsrc][1]
				if offset is not None:
					self.x += offset[0]
					self.y += offset[1]
		return self

	def show(self, canvas, showframe=None):
		if self._border_width > 0.0:
			canvas.saveState()
			canvas.setStrokeColor(self._border_color)
			canvas.setLineWidth(self._border_width)
			if self._border_fill_color.lower() != 'none':
				canvas.setFillColor(self._border_fill_color)                        
			canvas.rect(self.x, 
						self.y, 
						self.width, 
						self.height, 
						stroke=self._border_type, 
						fill=self._fill_border_rect)
			canvas.restoreState()

		if self.flowable is not None:                  
			self.flowable.width = self.width-(2.0*self._padding[0])
			self.flowable.height = self.height-(2.0*self._padding[1])
			self.flowable.drawOn(canvas, self.x+self._padding[0], self.y-self._padding[1])

			if showframe is not None:
				canvas.saveState()
				canvas.setLineWidth(showframe[0])
				canvas.rect(self.x, self.y, self.width, self.height, stroke=1, fill=showframe[1])
				canvas.restoreState()

		return self


#------------------------
# RLParagraphFrame
#------------------------
class RLParagraphFrame(RLFrame):
	def __init__(self, x, y, width, height, paragraphText, innerpad=None, paragraphStyle=None):
		RLFrame.__init__(self, x, y, width, height)
		paracontent = ' '
		parainstance = None            

		if innerpad is not None:
			self._padding = innerpad

		if paragraphText is not None:
			paracontent = paragraphText

		finalStyle = None
		if paragraphStyle is not None:
			finalStyle = paragraphStyle                  
		else:
			finalStyle = getSampleStyleSheet()["Normal"]

		mypara = Paragraph(paracontent, finalStyle)                  
		self.flowable = KeepInFrame( self.width-(self._padding[0]*2.0), self.height-(2.0*self._padding[1]), content=[mypara], mode='truncate') 

#------------------------
# RLXPreformatted
#------------------------
class RLXPreformatted(RLFrame):
	def __init__(self, x, y, width, height, paragraphText, innerpad=None, paragraphStyle=None):
		RLFrame.__init__(self, x, y, width, height)
		paracontent = ' '
		parainstance = None

		if innerpad is not None:
			self._padding = innerpad

		if paragraphText is not None:
			paracontent = paragraphText

		finalStyle = None
		if paragraphStyle is not None:
			finalStyle = paragraphStyle                  
		else:
			finalStyle = getSampleStyleSheet()['BodyText']

		myxpreformat = XPreformatted(paracontent, finalStyle)
		self.flowable = KeepInFrame( self.width-(2.0*self._padding[0]), self.height-(2.0*self._padding[1]), content=[myxpreformat], mode='truncate')


#------------------------
# RLImage
#------------------------
class RLImage(RLFrame):
	def __init__(self, x, y, width, height, picpath, altpicpath=None):
		RLFrame.__init__(self, x, y, width, height)
		self._path = None

		if picpath is None:
			return
		if os.path.exists(picpath):
			self._path = picpath
		elif altpicpath is not None:
			self._path = altpicpath
		else:
			return

		image =  Image(self._path, self.width, self.height )
		self.flowable = KeepInFrame( self.width, self.height, content=[image], mode='truncate')


def tempFilename(prefix, ext):
	"""
	Get a temp file name for any file type
	"""
	now = time.localtime()
	generated_filename_id = "%d%d%d%d%d%d%d%d%d"%(now[0],now[1],now[2],now[3],now[4],now[5],now[6],now[7],random.randint(0,999))
	return prefix+generated_filename_id+'.'+ext


class pagemgr:        
	"""
	This is a simple class that tracks the frames within a document.
	Frames are declared in the XML file. Also used to render page breaks
	"""
	def __init__(self, canvas):
		self._frame_x = None
		self._frame_y = None
		self._frame_width = None
		self._frame_height = None
		self._canvas = canvas
		self._curframe = None                                

	def pagebreak(self):

		if self._canvas is not None:
			self._canvas.showPage()
			# if we pagebreak, we re-create the current frame onto the new page
			if self._curframe is not None:
				self.newframe(self._frame_x, self._frame_y, self._frame_width, self._frame_height)

	def newframe(self, x, y, width, height):
		self._frame_x = x
		self._frame_y = y
		self._frame_width = width
		self._frame_height = height
		self._curframe = Frame(x, y, width, height, bottomPadding=0,topPadding=0,leftPadding=0,rightPadding=0,showBoundary=0)
		if self._showframes == True:
			self._curframe.drawBoundary(self._canvas)

	def getcurrentframe(self):
		return self._curframe

	def showframes(self, debugframes):
		self._showframes = debugframes                                

	def getcanvas(self):                     
		return self._canvas


class NumberedCanvas(canvas.Canvas):
	"""
	We derive Reportlab's Canvas class to be able to do
	some post-processing stuff. Such as rendering rlText
	containg special values (current page, total pages).
	Obviously we can only do this once a document is processed
	and we know the total number of pages.
	"""
	def __init__(self, *args, **kwargs):
		canvas.Canvas.__init__(self, *args, **kwargs)
		self._saved_page_states = [] #We keep the state of the canvas each time 'ShowPage' is called
		self._all_post_render_elements = [] # All elements that require post-rendering processing
		self._post_render_page_elements = [] # Elements within a document page which will require post-rendering processing
		self._post_render_page_trf = [] # The list of rltransforms for a document page, to be recalled for post-rendering processing
		self._isinpostrender = False # Are we rendering, or post-rendering?
		self._isDirty = False

	def addPostRender(self, pr_rlobject):
		"""
		An object within the current page will need post-rendering
		processing
		"""
		# We cache the tuple: (objects to rendered, current tranforms applied to object)
		self._post_render_page_elements.append((pr_rlobject,self._post_render_page_trf))

	def showPage(self):
		"""
		Overriden from Canvas.showPage
		We save the canvas state for later use and reset page specific lists
		"""
		# Append the list of elements of this page that need post-rendering
		# to the document's list
		self._all_post_render_elements.append(self._post_render_page_elements)
		self._post_render_page_elements = []
		self._post_render_page_trf = []
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()

	def _postrender(self, page_number):
		"""
		We revist each document page and do post-rendering on rlTEXT
		elements, if there are any.
		"""
		for element in self._all_post_render_elements[page_number-1]:
			# We need this distinction, otherwise the object will
			# not know its in post-render mode, and attempt to
			# add itself to post-rendering list for this page!
			self._isinpostrender = True       

			rl = element[0] # object to be processed in post-rendering
			all_tranforms = element[1] # Tranforms preceding this object

			if len(all_tranforms) == 0:
				# No tranforms, simply render and go
				rl.postrender(pagemgr(self), 
							  page_number, 
							  len(self._saved_page_states))
				return

			self.saveState()

			for trfdata in all_tranforms:
				# For each cached tranform, we re-apply
				# before calling the object to be processed
				# in post rendering
				if trfdata[0] == canvas.Canvas.rotate:
					canvas.Canvas.rotate(self,trfdata[1])
				elif trfdata[0] == canvas.Canvas.translate:
					canvas.Canvas.translate(self,trfdata[1],trfdata[2])
				elif trfdata[0] == canvas.Canvas.scale:
					canvas.Canvas.scale(self,trfdata[1],trfdata[2])

			rl.postrender(pagemgr(self), 
						  page_number, 
						  len(self._saved_page_states))

			self.restoreState()

	def dorotate(self, angle):
		"""
		This should only be called by rlTransform. We chose not to override
		canvas.rotate, because ReportLab does many tranforms internally that
		we don't want to cache for use in 'postrender'. We only cache transforms
		from <rltransform> tag directives 
		"""
		self._post_render_page_trf.append((canvas.Canvas.rotate,angle,0.0))
		canvas.Canvas.rotate(self,angle)

	def dotranslate(self, x,y):
		"""
		This should only be called by rlTransform. We chose not to override
		canvas.rotate, because ReportLab does many tranforms internally that
		we don't want to cache for use in 'postrender'. We only cache transforms
		from <rltransform> tag directives 
		"""
		self._post_render_page_trf.append((canvas.Canvas.translate,x,y))
		canvas.Canvas.translate(self,x,y)

	def doscale(self, x,y):
		"""
		This should only be called by rlTransform. We chose not to override
		canvas.rotate, because ReportLab does many tranforms internally that
		we don't want to cache for use in 'postrender'. We only cache transforms
		from <rltransform> tag directives 
		"""
		self._post_render_page_trf.append((canvas.Canvas.scale,x,y))
		canvas.Canvas.scale(self,x,y)

	def save(self):
		"""add page info to each page (page x of y)"""
		num_pages = len(self._saved_page_states)
		for state in self._saved_page_states:
			self.__dict__.update(state)
			self._postrender(self._pageNumber)                        
			canvas.Canvas.showPage(self)
		canvas.Canvas.save(self)