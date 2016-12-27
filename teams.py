from style import *
from players import List_players, Create_player
from events import List_events, Create_event
from games import List_games, Create_game
from statistics import List_team_stats, List_team_heats, List_team_temp

 
###################################################
class Create_team(Normal_screen):
	def __init__(self, **args):
		super(Create_team, self).__init__(**args)
			
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='New team'))
		
		fl = Form_layout()
		
		fl.add_widget(Form_lb(text='Name:'))
		self.ti_name = TextInput(hint_text='Write your team\'s name', multiline=False)
		fl.add_widget(self.ti_name)

		fl.add_widget(Form_lb(text='Games\' length:'))
		self.ti_time = TextInput(hint_text='ex: futsal 40min', multiline=False, input_filter='int')
		fl.add_widget(self.ti_time)
		
		b_conf = Form_btn(text='Confirm', background_color=(.5,.8,.5,1))
		b_conf.bind(on_release=self._confirm)
		b_cancel = Form_btn(text='Cancel')
		b_cancel.bind(on_release=self.on_back_pressed)
		
		fl.add_widget(b_conf)
		fl.add_widget(b_cancel)
		bl.add_widget(fl)
		
		root.add_widget(bl)
		self.add_widget(root)
	
	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size

	def on_enter(self, *args):
		self.ti_name.focus = True

	def _confirm(self, *args):
		if not self.ti_time.text:
			return

		self.ti_name.focus, self.ti_time.focus = False, False
		try:
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('create table if not exists teams(name varchar(100) primary key, games_length numeric, field blob);')
				cur.execute('insert into teams (name, games_length) values(?, ?);', (self.ti_name.text, int(self.ti_time.text)))
			self.ti_name.text, self.ti_time.text = '', ''
			self.manager.current = 'menu'
		except Exception as exc:
			print(exc)
			self.ti_name.hint_text = '\"' + self.ti_name.text + '\" is already taken, choose another name'
			self.ti_name.text = ''

	def on_back_pressed(self, *args):
		if self.ti_name.focus == True:
			self.ti_name.focus = False
		elif self.ti_time.focus == True:
			self.ti_time.focus = False
		else:
			self.manager.current = 'menu'

	
###################################################	
class List_teams(Normal_screen):
	def __init__(self, menu=True, previous_screen='', team_name='', **args):
		super(List_teams, self).__init__(**args)
		self.menu = menu
		self.previous_screen = previous_screen
		self.team_name = team_name

	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()
		
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Choose a team'))
		
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists teams(name varchar(100) primary key, games_length numeric, field blob);')
			cur.execute('select name from teams;')
			names = cur.fetchall()
			if len(names):
				for name in names:
					b_team = List_btn(text=name[0])
					if self.menu:
						b_team.bind(on_release=partial(self._go_team, b_team))
					else:
						b_team.bind(on_release=partial(self._return_to_previous_screen, b_team))
					bl.add_widget(b_team)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_release=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)
		
	def _go_team(self, b_team, *args):
		if not self.manager.has_screen(b_team.text):
			self.manager.add_widget(Team(b_team.text, name=b_team.text))
		self.manager.current = b_team.text

	def _return_to_previous_screen(self, b_team, *args):
		print(b_team.text)
		try:
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(100), team_name varchar(100), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
				
				cur.execute('select name as nm from events where team_name=? and not exists(select * from events where team_name=? and name=nm)', (b_team.text, self.team_name))
				events = cur.fetchall()
				for event in events:
					cur.execute('insert into events (name, team_name) values(?, ?);', (event[0], self.team_name))		
		except Exception as exc:
			pp = W_popup(str(exc) ,'Error!')				
			pp.open()
		self.manager.current = self.previous_screen
		self.manager.remove_widget(self.manager.get_screen(self.name))

	def on_back_pressed(self, *args):
		if self.menu:
			self.manager.current = 'menu'
		else:
			print(self.previous_screen)
			self.manager.current = self.previous_screen
			self.manager.remove_widget(self.manager.get_screen(self.name))

###################################################
class Team(Normal_screen):
	def __init__(self, team_name, **args):
		super(Team, self).__init__(**args)
		self.team_name = team_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Team: %s'%(team_name)))
		
		b_players = Nav_btn(text='Players')
		b_players.bind(on_release=self._go_list_players)
		bl.add_widget(b_players)
		
		b_new_player = New_btn(text='New player')
		b_new_player.bind(on_release=self._go_new_player)
		bl.add_widget(b_new_player)

		b_games = Nav_btn(text='Games')
		b_games.bind(on_release=self._go_list_games)
		bl.add_widget(b_games)
		
		b_new_game = New_btn(text='New game')
		b_new_game.bind(on_release=self._go_new_game)
		bl.add_widget(b_new_game)

		b_stats = List_btn(text='Statistics', background_color=(1,1,0,1))
		b_stats.bind(on_release=self._go_list_team_stats)
		bl.add_widget(b_stats)

		b_heats = List_btn(text='Heats', background_color=(1,1,0,1))
		b_heats.bind(on_release=self._go_list_team_heats)
		bl.add_widget(b_heats)

		b_temp = List_btn(text='Temporal', background_color=(1,1,0,1))
		b_temp.bind(on_release=self._go_list_team_temp)
		bl.add_widget(b_temp)
		
		b_events = Nav_btn(text='Events')
		b_events.bind(on_release=self._go_list_events)
		bl.add_widget(b_events)
		
		b_new_event = New_btn(text='New event')
		b_new_event.bind(on_release=self._go_new_event)
		bl.add_widget(b_new_event)

		b_import_events = Nav_btn(text='Import events')
		b_import_events.bind(on_release=self._import_events)
		bl.add_widget(b_import_events)


		b_field = Nav_btn(text='Add/Change field')
		b_field.bind(on_release=partial(self.filechooser, team_name))
		bl.add_widget(b_field)

		b_time = Nav_btn(text='Change games\' length')
		b_time.bind(on_release=self.change_time)
		bl.add_widget(b_time)

		b_delete = Red_btn(text='Delete')
		b_delete.bind(on_release=self._confirm_popup)
		bl.add_widget(b_delete)
		
		b_back = Back_btn(text='Back')
		b_back.bind(on_release=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)

	def change_time(self, *args):
		content = Form_layout()

		content.add_widget(Form_lb(text='Games\' length:'))
		self.ti_time = TextInput(hint_text='ex: futsal 40min', multiline=False, input_filter='int')
		content.add_widget(self.ti_time)

		b_conf = Form_btn(text='Confirm', background_color=(.5,.8,.5,1))
		b_conf.bind(on_release=self.confirm_time)
		b_cancel = Form_btn(text='Cancel')

		content.add_widget(b_conf)
		content.add_widget(b_cancel)

		self.pp = Popup(title='New games\' length', content=content, size_hint_y=.3)
		b_cancel.bind(on_release=self.pp.dismiss)
		self.pp.open()

	def confirm_time(self, *args):
		if not self.ti_time.text:
			return

		try:
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute("update teams set games_length=? where name=?;", (int(self.ti_time.text), self.team_name))
		except Exception as exc:
			pp = W_popup(str(exc), title='Database error!')


	def filechooser(self, team_name, *args):
		root = BoxLayout(orientation='vertical')
		bl = BoxLayout(size_hint_y=.1)
		

		self.fc = FileChooser(multiselect=True)

		b_open = Button(text='Confirm', size_hint_x=.1)
		bl.add_widget(b_open)

		b_cancel = Button(text='Cancel', size_hint_x=.1)
		bl.add_widget(b_cancel)

		b_view = Button(text='List/Icon View', size_hint_x=.1)
		bl.add_widget(b_view)
		root.add_widget(bl)

		b_view.bind(on_release=self.change_view)

		self.fc.add_widget(FileChooserListLayout())
		self.fc.add_widget(FileChooserIconLayout())
		root.add_widget(self.fc)
		
		self.pp = Popup(title='Select the field image', content=root)
		
		b_open.bind(on_release=partial(self._load, team_name))
		b_cancel.bind(on_release=self.pp.dismiss)
		self.pp.open()

	def _load(self, team_name, *args):
		try:
			sd_path_file = self.fc.selection[0].encode('utf-8')
			with open(sd_path_file, 'rb') as r:
				with lite.connect('allsports.db') as con:
					cur = con.cursor()
					cur.execute('update teams set field=? where name=?;', (lite.Binary(r.read()), team_name))
					self.pp.dismiss()
		except Exception as exc:
			try:
				pp = W_popup(exc ,'Error!')
			except:
				pp = W_popup('You need to select a file before!' ,'Error!')
			pp.open()
		else:
			self.pp.dismiss()
			pp = W_popup('Your image was successfuly loaded.' ,'Success!')
			pp.open()

	def change_view(self, *args):
		if self.fc.view_mode == 'list':
			self.fc.view_mode = 'icon'
		else:
			self.fc.view_mode = 'list'

	def _confirm_popup(self, *args):
		content = GridLayout(cols=2)
		confirm_btn = Button(text='Confirm', background_color=(1, 0, 0, 1))
		content.add_widget(confirm_btn)
		cancel_btn = Button(text='Cancel')
		content.add_widget(cancel_btn)

		self.popup = Popup(title="Confirm you want to delete %s\'s records" % (self.team_name), content=content, size_hint=(0.8, 0.4))
		cancel_btn.bind(on_release=self.popup.dismiss)
		confirm_btn.bind(on_release=self.delete_team)
		self.popup.open()

	def delete_team(self, *args):
		self.popup.dismiss()
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('pragma foreign_keys = on;')
			cur.execute('delete from teams where name=?;', (self.team_name,))

		self.manager.current = 'menu'
		self.manager.remove_widget(self.manager.get_screen(self.name))

	def _go_list_players(self, *args):
		if not self.manager.has_screen(self.team_name + '_list_players'):
			self.manager.add_widget(List_players(self.team_name, name=self.team_name + '_list_players'))
		self.manager.current = self.team_name + '_list_players'

	def _go_list_team_stats(self, *args):
		if not self.manager.has_screen(self.team_name + '_stats'):
			self.manager.add_widget(List_team_stats(self.team_name, name=self.team_name + '_stats'))
		self.manager.current = self.team_name + '_stats'

	def _go_list_team_heats(self, *args):
		if not self.manager.has_screen(self.team_name + '_heats'):
			self.manager.add_widget(List_team_heats(self.team_name, name=self.team_name + '_heats'))
		self.manager.current = self.team_name + '_heats'

	def _go_list_team_temp(self, *args):
		if not self.manager.has_screen(self.team_name + '_temp'):
			self.manager.add_widget(List_team_temp(self.team_name, name=self.team_name + '_temp'))
		self.manager.current = self.team_name + '_temp'
		
	def _go_new_player(self, *args):
		if not self.manager.has_screen(self.team_name + '_new_player'):
			self.manager.add_widget(Create_player(self.team_name, name=self.team_name + '_new_player'))
		self.manager.current = self.team_name + '_new_player'
	
	def _go_list_games(self, *args):
		if not self.manager.has_screen(self.team_name + '_list_games'):
			self.manager.add_widget(List_games(self.team_name, name=self.team_name + '_list_games'))
		self.manager.current = self.team_name + '_list_games'
		
	def _go_new_game(self, *args):
		if not self.manager.has_screen(self.team_name + '_new_game'):
			self.manager.add_widget(Create_game(self.team_name, name=self.team_name + '_new_game'))
		self.manager.current = self.team_name + '_new_game'

	def _go_list_events(self, *args):
		if not self.manager.has_screen(self.team_name + '_list_events'):
			self.manager.add_widget(List_events(self.team_name, name=self.team_name + '_list_events'))
		self.manager.current = self.team_name + '_list_events'
		
	def _go_new_event(self, *args):
		if not self.manager.has_screen(self.team_name + '_new_event'):
			self.manager.add_widget(Create_event(self.team_name, name=self.team_name + '_new_event'))
		self.manager.current = self.team_name + '_new_event'

	def _import_events(self, *args):
		self.manager.add_widget(List_teams(menu=False, previous_screen=self.name, team_name=self.team_name, name=self.team_name + '_import_events'))
		self.manager.current = self.team_name + '_import_events'

	def on_back_pressed(self, *args):
		self.manager.current = 'list_teams'
		self.manager.remove_widget(self.manager.get_screen(self.name))
