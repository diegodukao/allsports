import sys
import os
import sqlite3 as lite
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
import random


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

class Back_btn(Button):
	def __init__(self, **args):
		super(Back_btn, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70
		self.background_color = get_color_from_hex('#707090')
	
class New_btn(Button):
	def __init__(self, **args):
		super(New_btn, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70
		self.background_color = (0, .8, 0, 1)


class Red_btn(Button):
	def __init__(self, **args):
		super(Red_btn, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70
		self.background_color = (.8, 0, 0, 1)

class Form_btn(Button):
	def __init__(self, **args):
		super(Form_btn, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70
		self.background_color = get_color_from_hex('#707090')
		
class Nav_btn(Button):
	def __init__(self, **args):
		super(Nav_btn, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70
		self.background_color = (0, 0, .8, 1)
	
class List_btn(Button):
	def __init__(self, **args):
		super(List_btn, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70


class Drop_list(Spinner):
	def __init__(self, **args):
		super(Drop_list, self).__init__(**args)
		self.size_hint_y = None
		self.heigth = 40



##################################################

class Title_lb(Label):
	def __init__(self, **args):
		super(Title_lb, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70

class Form_lb(Label):
	def __init__(self, **args):
		super(Form_lb, self).__init__(**args)
		self.size_hint_y = None
		self.height = 70
		
#######################################################
	
class Base_layout(GridLayout):
	def __init__(self, **args):
		super(Base_layout, self).__init__(**args)
		self.cols = 1
		self.size_hint_y = None
		self.spacing = 1
		
class Form_layout(GridLayout):
	def __init__(self, **args):
		super(Form_layout, self).__init__(**args)
		self.cols = 2
		self.size_hint_y = None