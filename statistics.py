from style import *

class List_player_stats(Normal_screen):
	def __init__(self, team_name, player_name, **args):
		super(List_player_stats, self).__init__(**args)
		self.team_name = team_name
		self.player_name = player_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		bl.add_widget(Title_lb(text='%s statistics'%(self.player_name)))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(40), team_name varchar(40), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select name, id from events where team_name=?', (self.team_name,))
			self.list_events = cur.fetchall()
			cur.execute('create table if not exists games(id integer primary key autoincrement, team_name varchar(40), opponent_name varchar(40), date varchar(10), open integer, foreign key(team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select opponent_name, date from games where team_name=?;', (self.team_name,))
			self.list_games = cur.fetchall()
			if len(self.list_games):
				for event in self.list_events:
					b_event = List_btn(text=event[0])
					b_event.bind(on_press=partial(self._graph_popup, b_event.text))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def _graph_popup(self, event_name,  *args):
		content = GridLayout(cols=1)
		try:
			event_id = [i[1] for i in self.list_events if i[0] == event_name][0]
		except Exception as exc:
			print(exc)
			return

		event_numbers = []
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(40), opponent_name varchar(40), player_name varchar(40), date_game varchar(10), time varchar(10), x integer, y integer, foreign key (event_id) references events(id) on delete cascade on update cascade, foreign key (team_name) references teams(name) on delete cascade on update cascade, foreign key (player_name) references players(name) on delete cascade on update cascade);')
			for game in self.list_games:
				aux = cur.execute('select event_id from game_events where team_name=? and player_name=? and opponent_name=? and date_game=?;', (self.team_name, self.player_name, game[0], game[1]))
				event_numbers.append(len([i for i in aux if i[0]==event_id]))
		
		graph = Graph(xlabel='Games', ylabel='Occurrences', x_ticks_major=1, y_ticks_major=1 ,y_grid_label=True , x_grid_label=True, padding=5, x_grid=True, y_grid=True,  xmin=1, xmax=len(event_numbers), ymin=0, ymax=max(event_numbers)+5)
		plot = MeshLinePlot(color=[1, 0, 0, 1])
		plot.points = [(i+1, j) for i, j in enumerate(event_numbers)]
		graph.add_plot(plot)
		content.add_widget(graph)

		fm = Form_layout()
		fm.add_widget(Label(text='Total: %d'%(sum(event_numbers))))
		fm.add_widget(Label(text='Mean: %0.2f'%(sum(event_numbers)/float(len(event_numbers)))))
		content.add_widget(fm)


		back_btn = Back_btn(text='Back')
		content.add_widget(back_btn)

		self.popup = Popup(title='%s - %s\'s statistics' % (self.player_name, event_name), content=content, size_hint=(1, 1))
		back_btn.bind(on_press=self.popup.dismiss)
		self.popup.open()		
		
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_' + self.player_name
		self.manager.remove_widget(self.manager.get_screen(self.name))



class List_team_stats(Normal_screen):
	def __init__(self, team_name, **args):
		super(List_team_stats, self).__init__(**args)
		self.team_name = team_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		bl.add_widget(Title_lb(text='%s statistics'%(self.team_name)))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(40), team_name varchar(40), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select name, id from events where team_name=?', (self.team_name,))
			self.list_events = cur.fetchall()
			cur.execute('create table if not exists games(id integer primary key autoincrement, team_name varchar(40), opponent_name varchar(40), date varchar(10), open integer, foreign key(team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select opponent_name, date from games where team_name=?;', (self.team_name,))
			self.list_games = cur.fetchall()
			if len(self.list_events):
				for event in self.list_events:
					b_event = List_btn(text=event[0])
					b_event.bind(on_press=partial(self._graph_popup, b_event.text))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def _graph_popup(self, event_name,  *args):
		content = GridLayout(cols=1)
		try:
			event_id = [i[1] for i in self.list_events if i[0] == event_name][0]
		except Exception as exc:
			print(exc)
			return

		event_numbers = []
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(40), opponent_name varchar(40), player_name varchar(40), date_game varchar(10), time varchar(10), x integer, y integer, foreign key (event_id) references events(id) on delete cascade on update cascade, foreign key (team_name) references teams(name) on delete cascade on update cascade, foreign key (player_name) references players(name) on delete cascade on update cascade);')
			for game in self.list_games:
				aux = cur.execute('select event_id from game_events where team_name=? and opponent_name=? and date_game=?;', (self.team_name, game[0], game[1]))
				event_numbers.append(len([i for i in aux if i[0]==event_id]))
		
		graph = Graph(xlabel='Games', ylabel='Occurrences', x_ticks_major=1, y_ticks_major=1 ,y_grid_label=True , x_grid_label=True, padding=5, x_grid=True, y_grid=True,  xmin=1, xmax=len(event_numbers), ymin=0, ymax=max(event_numbers)+5)
		plot = MeshLinePlot(color=[1, 0, 0, 1])
		plot.points = [(i+1, j) for i, j in enumerate(event_numbers)]
		graph.add_plot(plot)
		content.add_widget(graph)

		fm = Form_layout()
		fm.add_widget(Label(text='Total: %d'%(sum(event_numbers))))
		fm.add_widget(Label(text='Mean: %0.2f'%(sum(event_numbers)/float(len(event_numbers)))))
		content.add_widget(fm)


		back_btn = Back_btn(text='Back')
		content.add_widget(back_btn)

		self.popup = Popup(title='%s - %s\'s statistics' % (self.team_name, event_name), content=content, size_hint=(1, 1))
		back_btn.bind(on_press=self.popup.dismiss)
		self.popup.open()		
		
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


class Game_stats(Normal_screen):
	def __init__(self, team_name, opponent_name, date_game, **args):
		super(Game_stats, self).__init__(**args)
		self.team_name = team_name
		self.opponent_name = opponent_name
		self.date_game = date_game

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
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), opponent_name varchar(100), player_name varchar(100), date_game varchar(10), time varchar(10), x integer, y integer, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('select events.name, events.id, count(events.id) from game_events join events on game_events.event_id=events.id where game_events.team_name=? and game_events.opponent_name=? and game_events.date_game=? group by events.id;', (self.team_name, self.opponent_name, self.date_game))
				self.events = cur.fetchall()
				if len(self.events):
					for game_event in self.events:
						b_game_event = List_btn(text='%s' % (game_event[0]))
						b_game_event.bind(on_press=partial(self._graph_popup, game_event[0],game_event[1]))
						bl.add_widget(b_game_event)
						bl.add_widget(List_btn(text='Total: %d'%(game_event[2]), background_color=(0,0,0,1)))
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

	def _graph_popup(self, event_name, event_id,  *args):
		content = GridLayout(cols=1)

		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(40), opponent_name varchar(40), player_name varchar(40), date_game varchar(10), time varchar(10), x integer, y integer, foreign key (event_id) references events(id) on delete cascade on update cascade, foreign key (team_name) references teams(name) on delete cascade on update cascade, foreign key (player_name) references players(name) on delete cascade on update cascade);')
			cur.execute('select player_name, count(player_name) from game_events where team_name=? and opponent_name=? and date_game=? and event_id=? group by player_name;', (self.team_name, self.opponent_name, self.date_game, event_id))
			players_events = cur.fetchall()

			if len(players_events):
				for player in players_events:
					content.add_widget(List_btn(text=player[0]))
					content.add_widget(List_btn(text=str(player[1]), background_color=(0,0,0,1)))

			else:
				content.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))

		back_btn = Back_btn(text='Back')
		content.add_widget(back_btn)

		self.popup = Popup(title='%s - %s\'s statistics' % (self.team_name, event_name), content=content, size_hint=(1, 1))
		back_btn.bind(on_press=self.popup.dismiss)
		self.popup.open()		

	def on_back_pressed(self, *args):
		self.manager.current = '%s_%s_%s' % (self.team_name, self.opponent_name, self.date_game)
		self.manager.remove_widget(self.manager.get_screen(self.name))
