import os
import sys
import time
import docbase
from reportlab.pdfgen import canvas
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from rlutils import RLFrame, RLParagraphFrame, RLXPreformatted, RLImage
from rlutils import FRM_SW, FRM_NW, FRM_NE, FRM_SE, FRM_CTR
from rlutils import NumberedCanvas, pagemgr

rlsamplestylesheet = getSampleStyleSheet()
all_timers  = {}
def adddeltatimer(timername, deltatime):
	"""
	Simple way of wuickly profiling rendering various
	elements in a document
	"""
	pass
	#try:
		#all_timers[timername] += deltatime
	#except:
		#all_timers[timername] = deltatime


RLOBJECTS_CACHE = {}
def register(rlid, rlinstance):
	"""
	Some objects are rendered as ReportLab flowables and
	are registered if they are declared with an attribute
	'id' within the XML document file.

	Registered objects can be referred to by other objects
	that might need to 'snap' into a positon relative to
	the 'anchor' object
	"""
	global RLOBJECTS_CACHE
	if rlid is not None and rlinstance is not None:
		RLOBJECTS_CACHE[rlid] = rlinstance


def findinstance(rlid):
	"""
	Find an instance of a registered object
	"""
	global RLOBJECTS_CACHE
	try:
		return RLOBJECTS_CACHE[rlid]
	except:
		return None


def snapsrctodest(src_rect, dest_rect, snapsrc, snapto, offset):
	x = 0
	y = 1
	width = 2
	height = 3

	src_anchors = [(0,src_rect[height]),
		           (0,0),
		           (src_rect[width],0),
		           (src_rect[width],src_rect[height]),
		           (src_rect[width]/2.0,src_rect[height]/2.0)]

	dst_anchors = [(0,dest_rect[height]),
		           (0,0),
		           (dest_rect[width],0),
		           (dest_rect[width],dest_rect[height]),
		           (dest_rect[width]/2.0,dest_rect[height]/2.0),]

	src_rect[x] = dest_rect[x]+dst_anchors[snapto][0]-src_anchors[snapsrc][0]
	src_rect[y] = dest_rect[y]+dst_anchors[snapto][1]-src_anchors[snapsrc][1]
	if offset is not None:
		src_rect[x] += offset[0]
		src_rect[y] += offset[1]

	return src_rect


def rlObjectInstance(classname, baseelement):
	"""
	We build a new 'rlobject' instance by selecting
	the appopriate subclass matching a 'docElement' instance.
	Basically we map a document element to a object that knows
	how to render it
	"""
	newrlobject = None        
	try:
		klass = CLASS_RLOBJECTS[classname]                                
	except:
		print "Uknown docElement (%s)"%(classname)

	newrlobject = klass(baseelement)        
	return newrlobject


class rlobject:
	"""
	Base class of all objects used to render docElement(s) instances
	"""
	snapto_dict ={'NE':FRM_NE,'NW':FRM_NW,'SE':FRM_SE,'SW':FRM_SW,'C':FRM_CTR}

	def __init__(self, docelement):                
		self._baseelement = docelement                             
		self._rect = None
		self._needs_postrender = False

	def setrect(self, rectboundaries):
		self._rect = rectboundaries

	def render(self, pagemgr):
		"""
		This is the 'generic' renderer. It simply calls render(...)
		on all its children
		"""
		rendered = []
		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()

		for child in self._baseelement.getchildren():
			docelementname  = child.__class__.__name__

			newrlobject = rlObjectInstance(docelementname, child)
			if newrlobject is not None:
				# the child inherits the parent's rect
				newrlobject.setrect(self._rect)
				rendered.append(newrlobject.render(pagemgr))

		# Even if nothing is rendered we ship an empty text flowable
		if len(rendered) == 0:
			rendered = XPreformatted('', rlsamplestylesheet['BodyText'])

		return rendered


class rlBOX(rlobject):

	def render(self, pagemgr):
		rendered = []
		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()                

		rect = self._baseelement.getrect()
		canvas_height = canvas._pagesize[1]

		# We're looking for the object we're supposed to be positionned
		# relative to, hopefully it exists and has been rendered already!
		anchor_id, anchor_data = self._baseelement.getanchor()
		rendered_anchor = findinstance(anchor_id)                
		if rendered_anchor is not None:
			dest_rect = rendered_anchor.getrect()   
			dest_rect[1] = canvas_height - (dest_rect[1]+dest_rect[3])                        
			rect = snapsrctodest(rect, 
						         dest_rect, 
						         rlobject.snapto_dict[anchor_data[1].upper()],
						         rlobject.snapto_dict[anchor_data[2].upper()], 
						         [0,0])

		rect[1] = canvas_height - (rect[1]+rect[3])
		basestyle = self._baseelement.getstyle()
		bckg_color = basestyle.getattribute('background-color',str)
		border = basestyle.getattribute('border',float)
		color = basestyle.getattribute('color',str)
		canvas.saveState()
		canvas.setStrokeColor(color)
		canvas.setLineWidth(border)
		dofill = 0
		if bckg_color.lower() != 'none':
			canvas.setFillColor(bckg_color)
			dofill = 1
		canvas.rect(rect[0], rect[1], rect[2], rect[3], stroke=1, fill=dofill)
		canvas.restoreState()
		register(self._baseelement.getid(), RLFrame(rect[0], rect[1], rect[2], rect[3]))                


class rlLINE(rlobject):

	def render(self, pagemgr):
		rendered = []
		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()                

		basestyle = self._baseelement.getstyle()
		border = basestyle.getattribute('border',float)
		color = basestyle.getattribute('color',str)

		from_xy, to_xy = self._baseelement.getline()                
		canvas_height = canvas._pagesize[1]
		from_y = canvas_height - from_xy[1]
		to_y = canvas_height - to_xy[1]

		canvas.saveState()
		canvas.setStrokeColor(color)
		canvas.setLineWidth(float(border))
		canvas.line(from_xy[0], from_y, to_xy[0], to_y)
		canvas.restoreState()

class rlELLIPSE(rlobject):

	def render(self, pagemgr):
		rendered = []
		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()                

		basestyle = self._baseelement.getstyle()
		border = basestyle.getattribute('border',float)
		color = basestyle.getattribute('color',str)

		pos_xy, r_xy = self._baseelement.getellipse()                
		canvas_height = canvas._pagesize[1]
		pos_y = canvas_height - pos_xy[1]

		canvas.saveState()
		canvas.setStrokeColor(color)
		canvas.setLineWidth(float(border))
		canvas.ellipse(pos_xy[0], pos_y, pos_xy[0]+r_xy[0], pos_y-r_xy[1])
		canvas.restoreState()


class rlTRANSFORM(rlobject):

	def render(self, pagemgr):
		"""
		We allow canvas transorms in Reporlab coordinates.
		Reportlab does not support saving/restoring canvas states
		across 2+ pages. Make sure all transforms are done BEFORE
		a pagebreak occurs
		"""

		rendered = None
		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()                

		transform_action = None
		num_args = 0
		if canvas is not None:
			basestyle = self._baseelement.getstyle()
			trans_data = basestyle.getattribute('transform',str)
			if trans_data is not None:
				tranform_ctx = trans_data.split(':')
				if tranform_ctx is not None and len(tranform_ctx)>0:
					transform_type = tranform_ctx[0].lower()
					if transform_type == 'rotate' and len(tranform_ctx) >= 2:
						transform_action = NumberedCanvas.dorotate
						num_args = 1
					elif transform_type == 'translate' and len(tranform_ctx) >= 3:
						transform_action = NumberedCanvas.dotranslate
						num_args = 2
					elif transform_type == 'scale' and len(tranform_ctx) >= 3:
						transform_action = NumberedCanvas.doscale
						num_args = 2


		if transform_action is not None:
			pagemgr._canvas.saveState()

		if num_args == 1:
			transform_action(canvas,float(tranform_ctx[1]))
		elif num_args == 2:
			transform_action(canvas,float(tranform_ctx[1]),float(tranform_ctx[2]))
		else:
			print "Warning: transform with no args?"

		rendered = rlobject.render(self, pagemgr)

		if transform_action is not None:
			pagemgr._canvas.restoreState()    

		return rendered


class rlobjectPAGEBREAK(rlobject):
	"""
	Rendered instances of Page Breaks declared in XML
	"""
	def render(self, pagemgr):

		start = time.time()

		pagemgr.pagebreak()

		end = time.time()
		delta = end - start
		adddeltatimer('pagebreak',delta)
		return None


class rlobjectFRAME(rlobject):
	"""
	Rendered instances of frames, as per ReportLab's Frame class
	A frame is a simple container for ReportLab flowables
	"""
	def render(self, pagemgr):

		start = time.time()

		canvas = pagemgr.getcanvas()
		canvas_height = canvas._pagesize[1]
		top_bottom_y = canvas_height - (self._baseelement._y+self._baseelement._height)
		pagemgr.newframe(self._baseelement._x,
				         top_bottom_y,
				         self._baseelement._width,
				         self._baseelement._height)

		end = time.time()
		delta = end - start
		adddeltatimer('frame',delta)

		return rlobject.render(self, pagemgr)


class rlIMAGE(rlobject):
	"""
	Rendered instances of images, as per ReportLab's Image class
	An image can be positionned:
	- Within a frame
	- On the canvas at specified coords (x,y)
	- On the canvas at relative to another flowable
	"""
	def _buildfromrect(self, canvas, imgpath, rect ):
		"""
		When posx, posy attributes are used for an <img> tag,
		we assume it needs to be rendered on the canvas, and is not
		necessarily contained within a frame.
		Even if posx, posy attributes are not defined, the image
		can be placed on the canvas relative to another flowable
		"""
		top_bottom_y = None
		canvas_height = canvas._pagesize[1]
		if rect[1] is not None:
			# We convert from ReportLab's coord system a more intuitive one
			top_bottom_y = canvas_height - (rect[1]+rect[3])

		imgfield = RLImage(rect[0], top_bottom_y, rect[2], rect[3], imgpath, None)                

		basestyle = self._baseelement.getstyle()
		border_color = basestyle.getattribute('border-color',str)
		border_width = basestyle.getattribute('border',float)
		backcolor = basestyle.getattribute('background-color',str)
		top_pad = basestyle.getattribute('top-padding',float)                                
		left_pad = basestyle.getattribute('left-padding',float) 
		imgfield.setborderinfo(border_color, backcolor, border_width, 0, 1)
		imgfield._padding = [top_pad,left_pad]

		# If an x and y coord are specified, draw the image on the canvas
		# directly at those coordinates
		if rect[0] is not None and rect[1] is not None:
			imgfield.show(canvas)
			# If this object has an Id, we register it, as it could
			# be referred to by other objects
			register(self._baseelement.getid(), imgfield)
			return imgfield

		# We're looking for the object we're supposed to be positionned
		# relative to, hopefully it exists and has been rendered already!
		anchor_id, anchor_data = self._baseelement.getanchor()
		rendered_anchor = findinstance(anchor_id)                
		if rendered_anchor is None:
			return None

		imgfield.snapPosToFrame(rendered_anchor,
				                rlobject.snapto_dict[anchor_data[1].upper()],
				                rlobject.snapto_dict[anchor_data[2].upper()]).show(canvas)

		# If this object has an Id, we register it, as it could
		# be referred to by other objects
		register(self._baseelement.getid(), imgfield)
		return imgfield


	def render(self, pagemgr):
		"""
		Render the image at specified width, height
		An image can be positionned:
		- Within a frame
		- On the canvas at specified coords (x,y)
		- On the canvas at relative to another flowable
		"""
		start = time.time()

		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()

		# This might be a special image bound to a rect area
		# The rect is specified in XML and defines a text
		# field to be positionned on canvas at specified coords
		imgfield_rect = self._baseelement.getrect()
		if imgfield_rect is not None and canvas is not None:
			image = self._buildfromrect(canvas,
						                self._baseelement._src,
						                imgfield_rect)
		else:
			image =  Image(self._baseelement._src, self._baseelement._width, self._baseelement._height )
			if frame is not None:
				frame.addFromList([image], canvas)

		end = time.time()
		delta = end - start
		adddeltatimer('image',delta)

		return image


class rlobjectTEXT(rlobject):
	"""
	The text objects are either Paragraph or XPreformatted instances
	from ReportLab's package. 
	An text can be positionned:
	- Within a frame
	- On the canvas at specified coords (x,y)
	- On the canvas at relative to another flowable
	"""
	special_fields = ['#PAGE#',
		              '#TOTALPAGES#']

	def _addPostRender(self, canvas):

		rawtext = self._baseelement.gettext()
		for special in rlobjectTEXT.special_fields:
			if rawtext.find(special) >= 0:
				self._needs_postrender = True
				canvas.addPostRender(self)
				break

	def _buildfromrect(self, canvas, text, style, rect, wrap):
		"""
		We build a text field to be positionned absolutely on
		a rectangular area on the canvas, at specified x,y coords
		"""
		top_bottom_y = None
		canvas_height = canvas._pagesize[1]
		if rect[1] is not None:
			# We convert from ReportLab's coord system a more intuitive one
			top_bottom_y = canvas_height - (rect[1]+rect[3])

		basestyle = self._baseelement.getstyle()
		border_color = basestyle.getattribute('border-color',str)
		border_width = basestyle.getattribute('border',float)
		backcolor = basestyle.getattribute('background-color',str)
		top_pad = basestyle.getattribute('top-padding',float)                                
		left_pad = basestyle.getattribute('left-padding',float)                

		# If wrap is specified, we might need to create a Paragraph class instance
		# from ReportLab packages that supports line wrapping text
		if wrap == 0:
			textfield = RLXPreformatted(rect[0],
						                top_bottom_y,
						                rect[2],
						                rect[3],
						                text,[left_pad,top_pad],style)
		else:
			textfield = RLParagraphFrame(rect[0],
						                 top_bottom_y,
						                 rect[2],
						                 rect[3],
						                 text,[left_pad,top_pad],style)                

		textfield.setborderinfo(border_color, backcolor, border_width, 1, 1)

		# If an absolute coord (x,y) is specified, draw the text on canvas
		# at that exact position
		if rect[0] is not None and rect[1] is not None:                        
			if canvas._isinpostrender == False:
				# Register this object if possible, so others can refer to it
				register(self._baseelement.getid(), textfield)
				self._addPostRender(canvas)
				if self._needs_postrender == False:
					textfield.show(canvas)
			else:
				if self._needs_postrender == True:
					textfield.show(canvas)

		# We're looking for the object we're supposed to be positionned
		# relative to, hopefully it exists and has been rendered already!
		anchor_id, anchor_data = self._baseelement.getanchor()
		rendered_anchor = findinstance(anchor_id)                
		if rendered_anchor is None:
			return None

		textfield.snapPosToFrame(rendered_anchor,
				                 rlobject.snapto_dict[anchor_data[1].upper()],
				                 rlobject.snapto_dict[anchor_data[2].upper()]).show(canvas)

		# Register this object if possible, so others can refer to it
		register(self._baseelement.getid(), textfield)

		return textfield


	def postrender(self, pagemgr, page_number, total_pages):
		self._baseelement._text = self._baseelement._text.replace('#PAGE#', str(page_number))
		self._baseelement._text = self._baseelement._text.replace('#TOTALPAGES#', str(total_pages))

		basestyle = self._baseelement.getstyle()
		backcolor = basestyle.getattribute('background-color',str) # Cache original color
		basestyle.setattribute('background-color','white') # Set to white to overwrite previous field
		self.render(pagemgr) # Render the field
		basestyle.setattribute('background-color',backcolor) # Restore original background color

	def render(self, pagemgr):
		"""
		Texts are either XPreformat class instances or Paragraph class instances
		from Reportlab package. An text can be positionned:
		- Within a frame
		- On the canvas at specified coords (x,y)
		- On the canvas at relative to another flowable
		"""
		start = time.time()

		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()

		rawtext = self._baseelement.gettext()   

		# We allow empty text fields
		##if len(rawtext.strip()) == 0:                        
		##        return None

		basestyle = self._baseelement.getstyle()
		align = basestyle.getattribute('text-align',str)
		font_weight = basestyle.getattribute('font-weight',str)
		font_style = basestyle.getattribute('font-style',str)
		leadingpoints = basestyle.getattribute('leading',int)
		fgdgcolor = basestyle.getattribute('color',str)
		backcolor = basestyle.getattribute('background-color',str)

		wrap = basestyle.getattribute('wrap',int)
		if align == 'center':
			align = TA_CENTER
		elif align == 'right':
			align = TA_RIGHT
		else:
			align = TA_LEFT                

		if font_weight == 'bold':
			rawtext = '%s%s%s'%('<b>',rawtext,'</b>')                        
		if font_style == 'italic':
			rawtext = '%s%s%s'%('<i>',rawtext,'</i>')
		elif font_style == 'underline':
			rawtext = '%s%s%s'%('<u>',rawtext,'</u>')

		rawtext = rawtext.replace('\\n','<br/>')

		rawtext = '<para>%s</para>'%(rawtext)

		# This might be a special text bound to a rect area
		# The rect is specified in XML and defines a text
		# field to be positionned on canvas at specified coords
		textfield_rect = self._baseelement.getrect()

		kwargs = {'name':'', 
				  'fontName':basestyle.getattribute('font',str),
				  'fontSize':basestyle.getattribute('font-size',int),
				  'leading':leadingpoints,
				  'textColor':fgdgcolor,
				  'alignment':align,}

		if backcolor.lower() != 'none':
			kwargs['backColor'] = backcolor

		if wrap == 0:
			# No line wrapping
			def_para_style = ParagraphStyle(**kwargs)   
			if textfield_rect is None:
				formatted = XPreformatted(rawtext, def_para_style)
			else:
				self._rect = None # Since there is a text rect, it ovverides the rendering rect
				formatted = self._buildfromrect(canvas, rawtext, def_para_style, textfield_rect, wrap)                                
		else:
			# Line wrapping!
			##kwargs['wordWrap'] = 'CJK'
			def_para_style = ParagraphStyle(**kwargs) 
			if textfield_rect is None:
				formatted = Paragraph(rawtext, def_para_style)
			else:
				self._rect = None # Since there is a text rect, it ovverides the rendering rect
				formatted = self._buildfromrect(canvas, rawtext, def_para_style, textfield_rect, wrap)



		# The rendering rect is specified by an element which is within a table cell
		# This rect is not taken into account if the field is to be positionned on
		# specific coords on canvas (see 'self._baseelement.getrect()')
		if self._rect is not None and self._rect[2] is not None and self._rect[3] is not None:                        
			formatted = KeepInFrame( self._rect[2], self._rect[3], content=[formatted], mode='truncate')

		# If this is a 'normal' text flowable, it is simply displayed with the current frame
		# wherever that may be ...
		if textfield_rect is None and frame is not None:
			frame.addFromList([formatted], canvas)

		end = time.time()
		delta = end - start
		adddeltatimer('text',delta)

		return formatted


class rlobjectTABLE(rlobject):
	"""
	The tables are almost direct representations of ReportLab's Table class
	Currently, tables do not support being directly positionned onto the canvas
	either in absolute or relative to another flowable.
	Tables are simply rendered within a Frame, wherever the frame may be.
	Tables are also not 'id'-able, which means we also cannot position another
	object relative to a table.
	"""
	def render(self, pagemgr):                
		"""
		Tables seem to be the most expensive elements to render, proportionately
		to their number of cells. TODO: A faster implementation of tables using
		a different XML representation, which could be closer to ReportLab tables
		"""
		def makeRLTablestyle(tableelement, basestyle, styles, start, end):

			color = basestyle.getattribute('color',str)
			backgcolor = basestyle.getattribute('background-color',str)
			vertical_alignment = basestyle.getattribute('vertical-align',str)                        
			top_padding = basestyle.getattribute('top-padding',float)
			bottom_padding = basestyle.getattribute('bottom-padding',float)
			left_padding = basestyle.getattribute('left-padding',float)
			right_padding = basestyle.getattribute('right-padding',float)
			if backgcolor.lower() != 'none':
				styles.append(('BACKGROUND',start, end, backgcolor))
			styles.append(('TOPPADDING',start, end, top_padding))
			styles.append(('BOTTOMPADDING',start, end, bottom_padding))
			styles.append(('LEFTPADDING',start, end, left_padding))
			styles.append(('RIGHTPADDING',start, end, right_padding))
			styles.append(('VALIGN', start, end, vertical_alignment.upper()))
			styles.append(('COLOR', start, end, color))
			if start != end:
				styles.append(('SPAN',start , end))

		frame = None
		canvas = None
		if pagemgr is not None:
			frame = pagemgr.getcurrentframe()
			canvas = pagemgr.getcanvas()

		colwidths, rowheights = self._baseelement.getdimensions()
		rowcells = self._baseelement.getrowcells()

		num_cols = len(colwidths)
		num_rows = len(rowheights)
		ori_num_cols = num_cols

		data_array = []
		for i in range(num_rows):
			data_array.append(num_cols*[None])

		basestyle = self._baseelement.getstyle()
		border = basestyle.getattribute('border',float)
		grid = basestyle.getattribute('grid',float)
		color = basestyle.getattribute('color',str)
		border_frame = basestyle.getattribute('frame',str)

		stylecmds = []

		if border_frame == 'above':
			stylecmds.append(('LINEABOVE',(0,0),(-1,0), border, color))
		elif border_frame == 'below':
			stylecmds.append(('LINEBELOW',(0,-1),(-1,-1), border, color))
		elif border_frame == 'left':
			stylecmds.append(('LINEBEFORE',(0,0),(0,-1), border, color))
		elif border_frame == 'right':
			stylecmds.append(('LINEAFTER',(-1,0),(-1,-1), border, color))
		elif border > 0.0:
			stylecmds.append(('BOX',(0,0),(-1,-1), border, color))

		if grid > 0.0:
			stylecmds.append(('INNERGRID',(0,0),(-1,-1), grid, color))


		start = 0
		delta_loop = 0
		start = time.time()

		row_index = 0
		# Go through each row for the table
		for row in rowcells:                        
			col_index = 0
			cell_index = 0                             
			# Each row is composed of cells which may span several columns, rows
			for cell in row:   
				addstyle = True
				subrow_index = 0
				# Each cell possibly spans several rows
				for subrow in cell:                                        
					subcol_index = 0
					# Each cell possibly spans several columns
					for subcol in subrow:
						docelementname  = subcol.__class__.__name__
						# This is the object contained withing a table cell
						rlobject = rlObjectInstance(docelementname, subcol) 
						final_row_index = row_index+subrow_index
						final_col_index = col_index+subcol_index
						row_span = len(cell)
						col_span = len(subrow)
						cell_width = None
						cell_height = None

						# We dont want to overwrite existing cells from previous rows.
						# Skip until we find empty cells. Sometimes this results in
						# a table that needs to be adjusted and we'll add extra columns.
						while data_array[final_row_index][final_col_index] is not None:
							subcol_index += 1
							final_col_index = col_index+subcol_index
							if final_col_index >= len(data_array[final_row_index]):
								data_array[final_row_index].append(None)
								num_cols += 1

						#Calculate actual width, height of a cell. Cells can span several columns, rows
						if colwidths[col_index] is not None:
							cell_width = col_span*colwidths[col_index]# TODO: Test we dont get out bounds of colwidths
						if rowheights[row_index] is not None:
							cell_height = row_span*rowheights[row_index]# TODO: Test we dont get out bounds of rowheights

						# Give the object contained with the table cell it's boundaries
						rlobject.setrect((0,0,cell_width,cell_height))

						loop_start = time.time()                                                
						data_array[final_row_index][final_col_index] = rlobject.render(None) # render the table cell object                                              
						loop_end = time.time()
						delta_loop += (loop_end-loop_start)

						basestyle = rlobject._baseelement.getstyle()                                                

						if addstyle == True:
							addstyle = False
							makeRLTablestyle( rlobject, basestyle, stylecmds,
											  (final_col_index, final_row_index),
											  (final_col_index+col_span-1,final_row_index+row_span-1))   
						subcol_index += 1
					subrow_index += 1
				col_index += len(subrow)
				cell_index += 1
			row_index += 1

		# if the table needs to be adjusted and add extra colum(s)
		if num_cols > ori_num_cols:
			for i in range(num_rows):
				adjust_cols = num_cols - len(data_array[i])
				new_cols = adjust_cols*[None]
				data_array[i] += new_cols

		style = TableStyle(stylecmds)
		table = Table(data_array, colwidths, rowheights, style)

		if frame is not None:
			frame.addFromList([table], canvas)                

		end = time.time()
		delta = end - start
		adddeltatimer('table',delta-(delta_loop))

		return table


CLASS_RLOBJECTS = {'docElement':rlobject, 
                   'docStyle':rlobject,
                   'docGeoBox':rlBOX,
                   'docGeoLine':rlLINE,
                   'docGeoEllipse':rlELLIPSE,
                   'docGeoTransform':rlTRANSFORM,
                   'docStyle':rlobject,
                   'docImage':rlIMAGE, 
                   'docText':rlobjectTEXT,
                   'docTable':rlobjectTABLE, 
                   'docPagebreak':rlobjectPAGEBREAK,
                   'docFrame':rlobjectFRAME}


def render( root, pdf, **kwargs ):

	debug = False
	mycanvas = None
	if kwargs is not None:
		try:
			fonts = kwargs['fonts']
			map(pdfmetrics.registerFont, fonts)
		except:
			pass
		
		try:
			debug = kwargs['showframes']
		except:
			pass
		try:
			mycanvas = kwargs['canvas']
		except:
			pass
	doc_pagesize = pagesizes.letter
	root_pagesize = root._style.getattribute('pagesize',str)
	root_pageorientation = root._style.getattribute('orientation',str)

	pagesize_tuple = root_pagesize.split(':')
	if len(pagesize_tuple) > 1:
		doc_pagesize = (float(pagesize_tuple[0]),float(pagesize_tuple[1]))

	if root_pageorientation == 'landscape':
		doc_pagesize = pagesizes.landscape(doc_pagesize)
	if root_pageorientation == 'portrait':
		doc_pagesize = pagesizes.portrait(doc_pagesize)        

	if mycanvas is None:
		pdf_canvas = NumberedCanvas(pdf, pagesize=doc_pagesize)        
	else:
		mycanvas.setPageSize(doc_pagesize)
		pdf_canvas = mycanvas                

	page_manager = pagemgr(pdf_canvas)        
	page_manager.showframes(debug)

	rlroot = rlobject(root)
	rlroot.render(page_manager)

	start = time.time()

	if mycanvas is None:
		pdf_canvas.save()

	end = time.time()
	delta = end - start
	adddeltatimer('canvas',delta)

	final_delta = 0

	return 0


def main(argv):
	return -1

if __name__ == '__main__':
	sys.exit(main(sys.argv))