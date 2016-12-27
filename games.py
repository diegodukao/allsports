from style import *

from statistics import Game_stats

class Create_game(Normal_screen):
	def __init__(self, team_name, **args):
		super(Create_game, self).__init__(**args)
		self.team_name = team_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='New game'))
		
		fl = Form_layout()
		
		fl.add_widget(Form_lb(text='Name:'))
		self.ti_opponent_name = TextInput(hint_text='Write your opponent\'s name', multiline=False)
		fl.add_widget(self.ti_opponent_name)
		
		fl.add_widget(Form_lb(text='Game\'s date:'))
		self.ti_date = TextInput(hint_text='YYYY-MM-DD', multiline=False)
		fl.add_widget(self.ti_date)
		
		
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
		self.ti_opponent_name.focus = True
	
	def _confirm(self, *args):
		aux = self.ti_date.text
		aux = aux.split('-')
		try:
			res = int(aux[0]) < 1900 or int(aux[0]) > 2100 or int(aux[1]) < 0 or int(aux[1]) > 12 or int(aux[2]) < 0 or int(aux[2]) > 31
		except Exception as exc:
			print(exc)
			self.ti_date.hint_text = 'Wrong date format. Use \"YYYY-MM-DD\"'
			self.ti_date.text = ''
			return
		
		if len(aux) != 3 or res:
			self.ti_date.hint_text = 'Wrong date format. Use \"YYYY-MM-DD\"'
			self.ti_date.text = ''
			return
		
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('pragma foreign_keys = on;')
			cur.execute('create table if not exists games(id integer primary key autoincrement, team_name varchar(100), opponent_name varchar(100), date varchar(10), open integer, foreign key(team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('insert into games (team_name, opponent_name, date, open) values(?, ?, ?, 1);', (self.team_name, self.ti_opponent_name.text,  self.ti_date.text))
		self.ti_date.text, self.ti_opponent_name.text = '', ''
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))
			
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))

class List_games(Normal_screen):
	def __init__(self, team_name, **args):
		super(List_games, self).__init__(**args)
		self.team_name = team_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		bl.add_widget(Title_lb(text='Games'))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			cur.execute('pragma foreign_keys = on;')
			cur.execute('create table if not exists games(id integer primary key autoincrement, team_name varchar(100), opponent_name varchar(100), date varchar(10), open integer, foreign key(team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select opponent_name, date, open, id from games where team_name=? order by id desc;', (self.team_name,))
			games = cur.fetchall()
			if len(games):
				for game in games:
					b_game = List_btn(text='%s | %s' % (game[0], game[1]), background_color=(.7,0,1,1))
					if game[2]:
						b_game.bind(on_press=partial(self._go_open_game, game))
						b_game.background_color = (1, 1, 0, 1)
					else:	
						b_game.bind(on_press=partial(self._go_closed_game, game))
					bl.add_widget(b_game)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)
	
	def _go_open_game(self, game, *args):
		opponent, date = game[0], game[1]
		if not self.manager.has_screen('%s_%s_%s' % (self.team_name, opponent, date)):
			self.manager.add_widget(Open_game(self.team_name, game, name='%s_%s_%s' % (self.team_name, opponent, date)))
		self.manager.current = '%s_%s_%s' % (self.team_name, opponent, date)

	def _go_closed_game(self, opponent_name, *args):
		opponent, date = game[0], game[1]
		if not self.manager.has_screen('%s_%s_%s' % (self.team_name, opponent, date)):
			self.manager.add_widget(Closed_game(self.team_name, game, name='%s_%s_%s' % (self.team_name, opponent, date)))
		self.manager.current = '%s_%s_%s' % (self.team_name, opponent, date)
		
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


class Closed_game(Normal_screen):
	def __init__(self, team_name, game, **args):
		super(Closed_game, self).__init__(**args)
		self.team_name = team_name
		self.opponent_name = game[0]
		self.date_game = game[1]
		self.game = game

		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))

		bl.add_widget(Title_lb(text='Finished'))
		bl.add_widget(Title_lb(text= '%s vs %s' % (self.team_name, self.opponent_name)))
		bl.add_widget(Title_lb(text=date_game))
		
		b_stats = List_btn(text='Statistics', background_color=(1,1,0,1))
		b_stats.bind(on_press=self._go_game_stats)
		bl.add_widget(b_stats)

		b_list_game_events = Nav_btn(text='Events\' list')
		b_list_game_events.bind(on_press=self._go_list_game_events)
		bl.add_widget(b_list_game_events)

		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)

	def _go_list_game_events(self, *args):
		if not self.manager.has_screen('%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_events(self.team_name, self.game, name='%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)

	def _go_game_stats(self, *args):
		if not self.manager.has_screen('%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(Game_stats(self.team_name, self.game, name='%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)

	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_list_games'
		self.manager.remove_widget(self.manager.get_screen(self.name))

class Open_game(Normal_screen):
	def __init__(self, team_name, game, **args):
		super(Open_game, self).__init__(**args)
		self.team_name = team_name
		self.opponent_name = game[0]
		self.date_game = game[1]
		self.game = game

		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))

		bl.add_widget(Title_lb(text='Running', color=(1,0,0,1)))
		bl.add_widget(Title_lb(text= '%s vs %s' % (self.team_name, self.opponent_name)))
		bl.add_widget(Title_lb(text=self.date_game))
		
		b_add_event = New_btn(text='Add event')
		b_add_event.bind(on_press=self._event_popup)
		bl.add_widget(b_add_event)

		b_stats = List_btn(text='Statistics', background_color=(1,1,0,1))
		b_stats.bind(on_press=self._go_game_stats)
		bl.add_widget(b_stats)

		b_list_game_events = Nav_btn(text='Events\' list')
		b_list_game_events.bind(on_press=self._go_list_game_events)
		bl.add_widget(b_list_game_events)

		b_close = Red_btn(text='Close game')
		b_close.bind(on_press=self._confirm_popup)
		bl.add_widget(b_close)

		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)

	def _go_list_game_events(self, *args):
		if not self.manager.has_screen('%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_events(self.team_name, self.game, name='%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)

	def _go_game_stats(self, *args):
		if not self.manager.has_screen('%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(Game_stats(self.team_name, self.game, name='%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)

	def _confirm_popup(self, *args):
		content = GridLayout(cols=2)
		confirm_btn = Button(text='Confirm')
		content.add_widget(confirm_btn)
		cancel_btn = Button(text='Cancel')
		content.add_widget(cancel_btn)

		self.popup = Popup(title="Confirm you want to close this game", content=content, size_hint=(0.8, 0.4))
		cancel_btn.bind(on_press=self.popup.dismiss)
		confirm_btn.bind(on_press=self.close_game)
		self.popup.open()

	def close_game(self, *args):
		self.popup.dismiss()
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('pragma foreign_keys = on;')
			cur.execute('update games set open=0 where id=?', (self.game[3]))
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))

	def _event_popup(self, *args):
		content = ScrollView()
		root = GridLayout(cols=2)
		root.bind(minimum_height=root.setter('height'))
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(100), team_name varchar(100), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			self.events_results = cur.execute('select id, name from events where team_name=?', (self.team_name,))

		self.events_list = Drop_list(text="Select an event", values=tuple([i[1] for i in self.events_results]))
		root.add_widget(self.events_list)
		
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists players(name char(40), team_name char(40), visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
			players_results = cur.execute('select name from players where team_name=? and visible=1', (self.team_name,))

		self.players_list = Drop_list(text="Select a player", values=tuple([i[0] for i in players_results]))
		root.add_widget(self.players_list)

		confirm_btn = Form_btn(text='Confirm')
		confirm_btn.bind(on_press=self._confirm_event)
		root.add_widget(confirm_btn)
		cancel_btn = Form_btn(text='Cancel')
		root.add_widget(cancel_btn)
		content.add_widget(root)

		self.popup = Popup(title="New event",
              content=content,
              size_hint=(1, 1))
		cancel_btn.bind(on_press=self.popup.dismiss)
		self.popup.open()

	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_list_games'
		self.manager.remove_widget(self.manager.get_screen(self.name))

	def _confirm_event(self, *args):
		if self.events_list.text!="Select an event" and self.players_list.text != "Select a player":
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				event_id = cur.execute('select id from events where team_name=? and name=?;', (self.team_name, self.events_list.text))
				event_id = [i for i in event_id][0][0]
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time varchar(10), x integer, y integer, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('insert into game_events(event_id, team_name, player_name, game_id) values(?, ?, ?, ?);', (event_id, self.team_name, self.players_list.text, str(self.game[3])))
			self.popup.dismiss()

		
class List_game_events(Normal_screen):
	def __init__(self, team_name, game, **args):
		super(List_game_events, self).__init__(**args)
		self.team_name = team_name
		self.opponent_name = game[0]
		self.date_game = game[1]
		self.game = game

	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		bl.add_widget(Title_lb(text='Game\'s events'))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			try:
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time varchar(10), x integer, y integer, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('select events.name, game_events.player_name from game_events join events on game_events.event_id=events.id where game_events.game_id=?;', (str(self.game[3]),))
				game_events = cur.fetchall()
				if len(game_events):
					for game_event in game_events:
						b_game_event = List_btn(text='%s | %s' % (game_event[0], game_event[1]), background_color=(1,0,1,1))
						bl.add_widget(b_game_event)
				else:
					bl.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))
			except Exception as exc:
				print(exc)
				bl.add_widget(Label(text='Database error.', color=(1,0,0,1)))

		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def on_back_pressed(self, *args):
		self.manager.current = '%s_%s_%s' % (self.team_name, self.opponent_name, self.date_game)
		self.manager.remove_widget(self.manager.get_screen(self.name))
