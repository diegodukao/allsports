import sys
import os
import sqlite3 as lite
import numpy as np
from PIL import Image as Img, ImageFilter as ImgF

from kivy.utils import platform
from kivy.uix.filechooser import FileChooser, FileChooserIconLayout, FileChooserListLayout
from kivy.uix.scrollview import ScrollView
from functools import partial
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex 
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.accordion import Accordion, AccordionItem
import random
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import *
from kivy.uix.floatlayout import FloatLayout

from jnius import autoclass

button_h = 90
font_size = 20
title_font_size = 20

class Normal_screen(Screen):
	def __init__(self, **args):
		super(Normal_screen, self).__init__(**args)
		self.register_event_type('on_back_pressed')
		self.register_event_type('on_menu_pressed')
 
	def on_back_pressed(self, *args):
		pass
 
	def on_menu_pressed(self, *args):
		pass

############################################### 

class IconButton(ButtonBehavior, Image):
	def __init__(self, source, **args):
		self.source = source
		super(IconButton, self).__init__(**args)

class Back_btn(Button):
	def __init__(self, **args):
		self.size_hint_y = None
		self.font_size = font_size
		self.height = button_h
		self.background_color = get_color_from_hex('#aaaaaa')
		super(Back_btn, self).__init__(**args)
	
class New_btn(Button):
	def __init__(self, **args):
		self.size_hint_y = None
		self.font_size = font_size
		self.height = button_h
		self.background_color = (.5, .8, .5, 1)
		super(New_btn, self).__init__(**args)

class Red_btn(Button):
	def __init__(self, **args):
		self.size_hint_y = None
		self.font_size = font_size
		self.height = button_h
		self.background_color = (.8, .5, .5, 1)
		super(Red_btn, self).__init__(**args)

class Form_btn(Button):
	def __init__(self, **args):
		self.size_hint_y = None
		self.font_size = font_size
		self.height = button_h
		self.background_color = get_color_from_hex('#aaaaaa')
		super(Form_btn, self).__init__(**args)
		
class Nav_btn(Button):
	def __init__(self, **args):
		self.size_hint_y = None
		self.font_size = font_size
		self.height = button_h
		self.background_color = (.95, .95, .95, 1)
		super(Nav_btn, self).__init__(**args)
	
class List_btn(Button):
	def __init__(self, **args):
		self.size_hint_y = None
		self.font_size = font_size
		self.height = button_h
		self.background_color = (.95, .95, .95, 1)
		super(List_btn, self).__init__(**args)


class Drop_list(Spinner):
	def __init__(self, **args):
		self.size_hint_y = None
		self.heigth = 40
		super(Drop_list, self).__init__(**args)



##################################################

class Title_lb(Label):
	def __init__(self, **args):
		self.size_hint_y = None
		self.height = button_h
		self.font_size = title_font_size
		super(Title_lb, self).__init__(**args)

class Form_lb(Label):
	def __init__(self, **args):
		self.size_hint_y = None
		self.font_size = font_size
		self.height = button_h
		super(Form_lb, self).__init__(**args)
		
#######################################################
	
class Base_layout(GridLayout):
	def __init__(self, **args):
		self.cols = 1
		self.size_hint_y = None
		self.spacing = 1
		super(Base_layout, self).__init__(**args)
		
class Form_layout(GridLayout):
	def __init__(self, **args):
		self.cols = 2
		self.size_hint_y = None
		super(Form_layout, self).__init__(**args)


######################################################

class W_popup(Popup):
	def __init__(self, msg, ttl, **args):
		self.title = ttl 
		self.size_hint = (1,.4)
		self.title_align = 'center'

		bl = BoxLayout(orientation='vertical')
		
		l_warn = Label(text=msg)
		bl.add_widget(l_warn)
		
		b_close = Button(text='Close')
		bl.add_widget(b_close)
		
		self.content = bl
		
		b_close.bind(on_press=self.dismiss)
		super(W_popup, self).__init__(**args)


def alpha_composite(src, dst):
    src = np.asarray(src)
    dst = np.asarray(dst)
    out = np.empty(src.shape, dtype = 'float')
    alpha = np.index_exp[:, :, 3:]
    rgb = np.index_exp[:, :, :3]
    src_a = src[alpha]/255.0
    dst_a = dst[alpha]/255.0
    out[alpha] = src_a+dst_a*(1-src_a)
    old_setting = np.seterr(invalid = 'ignore')
    out[rgb] = (src[rgb]*src_a + dst[rgb]*dst_a*(1-src_a))/out[alpha]
    np.seterr(**old_setting)    
    out[alpha] *= 255
    np.clip(out,0,255)
    # astype('uint8') maps np.nan (and np.inf) to 0
    out = out.astype('uint8')
    out = Img.fromarray(out, 'RGBA')
    return out