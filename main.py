import kivy
kivy.require('1.8.0')

from style import *


if platform == 'android':
	import android

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

from teams import Create_team, List_teams

###################################################


class Menu(Normal_screen):
	def __init__(self, **args):
		super(Menu, self).__init__(**args)
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='AllSports'))
		
		create = New_btn(text='Create team')
		create.bind(on_release=self._go_create)
		bl.add_widget(create)

		choose = Nav_btn(text='Choose team')
		choose.bind(on_release=self._go_choose)
		bl.add_widget(choose)

		save = List_btn(text='Save database', background_color=(1,1,0,1))
		save.bind(on_release=partial(self.filechooser, True))
		bl.add_widget(save)

		load = List_btn(text='Load database',background_color=(1,1,0,1))
		load.bind(on_release=partial(self.filechooser, False))
		bl.add_widget(load)
		
		b_exit = Back_btn(text='Exit')
		b_exit.bind(on_release=sys.exit)
		bl.add_widget(b_exit)

		root.add_widget(bl)
		self.add_widget(root)


	def on_back_pressed(self, *args):
		sys.exit()

	def _go_create(self, *args):
		if not self.manager.has_screen('createteam'):
			self.manager.add_widget(Create_team(name='createteam'))
		self.manager.current = 'createteam'
			
	def _go_choose(self, *args):
		if not self.manager.has_screen('list_teams'):
			self.manager.add_widget(List_teams(name='list_teams'))
		self.manager.current = 'list_teams'

	def _save(self, *args):
		backup_name = self.file_name_ti.text if self.file_name_ti.text else 'allsports_backup'
		try:
			sd_path_file = str(self.fc.path) + '/%s.db' % backup_name
			with open('allsports.db', 'rb') as r:
				with open(sd_path_file, 'wb') as w:
					for i in r:
						w.write(i)
		except Exception as exc:
			try:
				pp = W_popup(str(exc) ,'Error!')
			except:
				pp = W_popup('You need to select a file before!' ,'Error!')				
			pp.open()
		else:
			self.pp.dismiss()
			pp = W_popup('Your database was successfuly saved.' ,'Success!')
			pp.open()

	def _load(self, *args):
		try:
			sd_path_file = self.fc.selection[0].encode('utf-8')
			with open(sd_path_file, 'rb') as r:
				with open('allsports.db', 'wb') as w:
					for i in r:
						w.write(i)
		except Exception as exc:
			try:
				pp = W_popup(str(exc) ,'Error!', size_hint=(.5,.3))
			except:
				pp = W_popup('You need to select a file before!' ,'Error!')			
			pp.open()
		else:
			self.pp.dismiss()
			pp = W_popup('Your database was successfuly loaded.' ,'Success!')
			pp.open()

	def filechooser(self, save_flag, *args):
		root = BoxLayout(orientation='vertical')
		
		if save_flag:
			self.file_name_ti = TextInput(hint_text="database's name", multiline=False, size_hint_y=.1)
			root.add_widget(self.file_name_ti) 
		
		bl = BoxLayout(size_hint_y=.1)

		b_open = Button(text='Confirm', size_hint_x=.1)
		bl.add_widget(b_open)

		b_cancel = Button(text='Cancel', size_hint_x=.1)
		bl.add_widget(b_cancel)

		b_view = Button(text='List/Icon View', size_hint_x=.1)
		bl.add_widget(b_view)
		root.add_widget(bl)

		b_view.bind(on_release=self.change_view)

		self.fc = FileChooser(multiselect=True)
		self.fc.add_widget(FileChooserListLayout())
		self.fc.add_widget(FileChooserIconLayout())
		root.add_widget(self.fc)

		if save_flag:
			title = 'Get inside the destination folder'
		else:
			title = 'Select your backup file'
		
		self.pp = Popup(title=title, content=root)
		if save_flag:
			b_open.bind(on_release=self._save)
		else:
			b_open.bind(on_release=self._load)
		b_cancel.bind(on_release=self.pp.dismiss)
		self.pp.open()

	def change_view(self, *args):
		if self.fc.view_mode == 'list':
			self.fc.view_mode = 'icon'
		else:
			self.fc.view_mode = 'list'
	
###################################################

	
class AllSports(App):
	Window.clearcolor = (.7,.7,.7,1)

	def build(self):
		self.icon = 'icon.png'
		self.bind(on_start=self._post_build_init)
		self.sm = ScreenManager(transition=NoTransition())
		self.sm.add_widget(Menu(name='menu'))
		return self.sm 

	def _post_build_init(self, ev):
		if platform == 'android':
			android.map_key(android.KEYCODE_BACK, 1000)
			android.map_key(android.KEYCODE_MENU, 1001)
		win = self._app_window
		win.bind(on_keyboard=self._key_handler)
 
	def _key_handler(self, window, key, *args):
		if key in (1000, 27):
			self.sm.current_screen.dispatch("on_back_pressed")
			return True
		elif key == 1001:
			self.sm.current_screen.dispatch("on_menu_pressed")
			return True

	def on_pause(self, *args):
		return True

if __name__ == '__main__':
	AllSports().run()