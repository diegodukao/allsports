from style import *
from players import List_players, Create_player
from events import List_events, Create_event
from games import List_games, Create_game
from statistics import List_team_stats

 
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
		
		b_conf = Form_btn(text='Confirm')
		b_conf.bind(on_press=self._confirm)
		b_cancel = Form_btn(text='Cancel')
		b_cancel.bind(on_press=self.on_back_pressed)
		
		fl.add_widget(b_conf)
		fl.add_widget(b_cancel)
		bl.add_widget(fl)
		
		root.add_widget(bl)
		self.add_widget(root)

	def on_enter(self, *args):
		self.ti_name.focus = True

	def _confirm(self, *args):
		try:
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('create table if not exists teams(name varchar(100) primary key);')
				cur.execute('insert into teams (name) values(?);', (self.ti_name.text,))
			self.ti_name.text = ''
			self.manager.current = 'menu'
		except Exception as exc:
			print(exc)
			self.ti_name.hint_text = '\"' + self.ti_name.text + '\" is already taken, choose another name'
			self.ti_name.text = ''

	def on_back_pressed(self, *args):
		self.manager.current = 'menu'

	
###################################################	
class List_teams(Normal_screen):
	def __init__(self, **args):
		super(List_teams, self).__init__(**args)
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()
		
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Choose a team'))
		
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists teams(name varchar(100) primary key);')
			cur.execute('select name from teams;')
			names = cur.fetchall()
			if len(names):
				for name in names:
					b_team = List_btn(text=name[0], background_color=(.7,0,1,1))
					b_team.bind(on_press=partial(self._go_team, b_team))
					bl.add_widget(b_team)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)
		
	def _go_team(self, b_team, *args):
		if not self.manager.has_screen(b_team.text):
			self.manager.add_widget(Team(b_team.text, name=b_team.text))
		self.manager.current = b_team.text

	def on_back_pressed(self, *args):
		self.manager.current = 'menu'


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
		b_players.bind(on_press=self._go_list_players)
		bl.add_widget(b_players)
		
		b_new_player = New_btn(text='New player')
		b_new_player.bind(on_press=self._go_new_player)
		bl.add_widget(b_new_player)

		b_games = Nav_btn(text='Games')
		b_games.bind(on_press=self._go_list_games)
		bl.add_widget(b_games)
		
		b_new_game = New_btn(text='New game')
		b_new_game.bind(on_press=self._go_new_game)
		bl.add_widget(b_new_game)

		b_stats = List_btn(text='Statistics', background_color=(1,1,0,1))
		b_stats.bind(on_press=self._go_list_team_stats)
		bl.add_widget(b_stats)
		
		b_events = Nav_btn(text='Events')
		b_events.bind(on_press=self._go_list_events)
		bl.add_widget(b_events)
		
		b_new_event = New_btn(text='New event')
		b_new_event.bind(on_press=self._go_new_event)
		bl.add_widget(b_new_event)

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

		self.popup = Popup(title="Confirm you want to delete %s\'s records" % (self.team_name), content=content, size_hint=(0.8, 0.4))
		cancel_btn.bind(on_press=self.popup.dismiss)
		confirm_btn.bind(on_press=self.delete_team)
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

	def on_back_pressed(self, *args):
		self.manager.current = 'list_teams'
		self.manager.remove_widget(self.manager.get_screen(self.name))
