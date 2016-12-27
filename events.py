from style import *

class List_events(Normal_screen):
	def __init__(self, team_name, **args):
		super(List_events, self).__init__(**args)
		self.team_name = team_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Events'))

		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(100), team_name varchar(100), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select * from events where team_name=? order by id desc;', (self.team_name,))
			names = cur.fetchall()
			if len(names):
				for name in names:
					b_event = List_btn(text=name[1], background_color=(.7,0,1,1))
					b_event.bind(on_press=partial(self._go_event, b_event))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)
		
	def _go_event(self, event_name, *args):
		if not self.manager.has_screen(event_name.text):
			self.manager.add_widget(Event(self.team_name, event_name.text, name=event_name.text))
		self.manager.current = event_name.text
		
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


###################################################
class Create_event(Normal_screen):
	def __init__(self, team_name, **args):
		super(Create_event, self).__init__(**args)
		self.team_name = team_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='New event'))
		
		fl = Form_layout()
		
		fl.add_widget(Form_lb(text='Name:'))
		self.ti_name = TextInput(hint_text='Write new event\'s name', multiline=False)
		fl.add_widget(self.ti_name)
		
		b_conf = Form_btn(text='Confirm')
		b_conf.bind(on_press=self._confirm)
		b_cancel = Form_btn(text='Cancel')
		b_cancel.bind(on_press=self.on_back_pressed)
		
		fl.add_widget(b_conf)
		fl.add_widget(b_cancel)
		bl.add_widget(fl)
		
		root.add_widget(bl)
		self.add_widget(root)

	def on_enter(self, **args):
		self.ti_name.focus = True
	
	def _confirm(self, *args):
		try:
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(100), team_name varchar(100), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
				cur.execute('insert into events (name, team_name) values(?, ?);', (self.ti_name.text, self.team_name))
			self.ti_name.text = ''
			self.manager.current = self.team_name
			self.manager.remove_widget(self.manager.get_screen(self.name))
		except Exception as exc:
			print(exc)
			self.ti_name.hint_text = '\"' + self.ti_name.text + '\" is already taken, choose another name'
			self.ti_name.text = ''
			
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


###################################################
class Event(Normal_screen):
	def __init__(self, team_name, event_name, **args):
		super(Event, self).__init__(**args)
		self.event_name = event_name
		self.team_name = team_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Event: %s'%(event_name)))
		
		b_rename = Nav_btn(text='Rename')
		b_rename.bind(on_press=self._go_rename_event)
		bl.add_widget(b_rename)
		
		b_delete = Red_btn(text='Delete')
		b_delete.bind(on_press=self._confirm_popup)
		bl.add_widget(b_delete)
		
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)
	
	def _confirm_popup(self, *args):
		content = GridLayout(cols=2)
		confirm_btn = Button(text='Confirm', background_color=(1, 0, 0, 1))
		content.add_widget(confirm_btn)
		cancel_btn = Button(text='Cancel')
		content.add_widget(cancel_btn)

		self.popup = Popup(title="Confirm you want to delete %s\'s records" % (self.event_name),
              content=content,
              size_hint=(0.8, 0.4))
		cancel_btn.bind(on_press=self.popup.dismiss)
		confirm_btn.bind(on_press=self.delete_event)
		self.popup.open()

	def delete_event(self, *args):
		self.popup.dismiss()
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('delete from events where name=? and team_name=?;', (self.event_name, self.team_name))
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))
	
	def _go_rename_event(self, *args):
		if not self.manager.has_screen('rename_' + self.event_name):
			self.manager.add_widget(Rename_event(self.team_name, self.event_name, name='rename_' + self.event_name))
		self.manager.current = 'rename_' + self.event_name
		self.manager.remove_widget(self.manager.get_screen(self.name))
	
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_list_events'
		self.manager.remove_widget(self.manager.get_screen(self.name))
	
	
###################################################	
class Rename_event(Normal_screen):
	def __init__(self, team_name, event_name, **args):
		super(Rename_event, self).__init__(**args)
		self.team_name = team_name
		self.event_name = event_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Rename event'))
		
		fl = Form_layout()
		
		fl.add_widget(Form_lb(text='New name:'))
		self.new_event_name = TextInput(hint_text='Write new event\'s name', multiline=False)
		fl.add_widget(self.new_event_name)
		
		b_conf = Form_btn(text='Confirm')
		b_conf.bind(on_press=self._confirm)
		b_cancel = Form_btn(text='Cancel')
		b_cancel.bind(on_press=self.on_back_pressed)
		
		fl.add_widget(b_conf)
		fl.add_widget(b_cancel)
		bl.add_widget(fl)
		
		root.add_widget(bl)
		self.add_widget(root)

	def on_enter(self, **args):
		self.new_event_name.focus = True
	
	def _confirm(self, *args):
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('pragma foreign_keys = on;')
			cur.execute('update events set name=? where name=?', (self.new_event_name.text, self.event_name))
		self.manager.current = self.team_name + '_list_events'
		self.manager.remove_widget(self.manager.get_screen(self.name))
			
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_list_events'
		self.manager.remove_widget(self.manager.get_screen(self.name))