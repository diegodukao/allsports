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
			cur.execute('select opponent_name, date, id from games where team_name=?;', (self.team_name,))
			self.list_games = cur.fetchall()
			if len(self.list_games):
				for event in self.list_events:
					b_event = Nav_btn(text=event[0])
					b_event.bind(on_press=partial(self._graph_popup, b_event.text))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='There are no game records to show'))
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
			cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
			for game in self.list_games:
				cur.execute('select event_id from game_events where game_id=? and player_name=?;', (str(game[2]), self.player_name))
				aux = cur.fetchall()
				event_numbers.append(len([i for i in aux if i[0]==event_id]))
		
		if len(event_numbers) and max(event_numbers):
			try:
				graph = Graph(xlabel='Games', ylabel='Occurrences', x_ticks_major=1, y_ticks_major=1 ,y_grid_label=True , x_grid_label=True, padding=5, x_grid=True, y_grid=True,  xmin=0, xmax=len(event_numbers)+1, ymin=0, ymax=max(event_numbers)+5)
				plot = MeshLinePlot(color=[1, 0, 0, 1])
				plot.points = [(0,0)]+[(i+1, j) for i, j in enumerate(event_numbers)]
				graph.add_plot(plot)
				content.add_widget(graph)

				fm = Form_layout()
				fm.add_widget(Label(text='Total: %d'%(sum(event_numbers))))
				fm.add_widget(Label(text='Mean: %0.2f'%(sum(event_numbers)/float(len(event_numbers)))))
				content.add_widget(fm)

			except Exception as exc:
				print(exc)
				content.add_widget(List_btn(text='No records to show'))
		else:
			content.add_widget(List_btn(text='No records to show'))

		back_btn = Back_btn(text='Back')
		content.add_widget(back_btn)

		self.popup = Popup(title='%s - %s Graph' % (self.player_name, event_name), content=content, size_hint=(1, 1))
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
			cur.execute('select opponent_name, date, id from games where team_name=?;', (self.team_name,))
			self.list_games = cur.fetchall()
			if len(self.list_events):
				for event in self.list_events:
					b_event = Nav_btn(text=event[0])
					b_event.bind(on_press=partial(self._graph_popup, b_event.text))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))
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
			cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
			for game in self.list_games:
				aux = cur.execute('select event_id from game_events where game_id=?;', (str(game[2])))
				event_numbers.append(len([i for i in aux if i[0]==event_id]))

		if len(event_numbers) and max(event_numbers):
			try:
				graph = Graph(xlabel='Games', ylabel='Occurrences', x_ticks_major=1, y_ticks_major=1 ,y_grid_label=True , x_grid_label=True, padding=5, x_grid=True, y_grid=True,  xmin=0, xmax=len(event_numbers)+1, ymin=0, ymax=max(event_numbers)+5)
				plot = MeshLinePlot(color=[1, 0, 0, 1])
				plot.points = [(0,0)]+[(i+1, j) for i, j in enumerate(event_numbers)]
				graph.add_plot(plot)
				content.add_widget(graph)
			
				fm = Form_layout()
				fm.add_widget(Label(text='Total: %d'%(sum(event_numbers))))
				fm.add_widget(Label(text='Mean: %0.2f'%(sum(event_numbers)/float(len(event_numbers)))))
				content.add_widget(fm)

			except Exception as exc:
				print(exc)
				content.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))
		else:
			content.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))

		back_btn = Back_btn(text='Back')
		content.add_widget(back_btn)

		self.popup = Popup(title='%s - %s Graph' % (self.team_name, event_name), content=content, size_hint=(1, 1))
		back_btn.bind(on_press=self.popup.dismiss)
		self.popup.open()		
		
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


class Game_stats(Normal_screen):
	def __init__(self, team_name, game, **args):
		super(Game_stats, self).__init__(**args)
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
				cur.execute('create table if not exists players(name varchar(100), team_name varchar(100), visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
				cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(100), team_name varchar(100), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('select events.name, events.id, count(events.id) from game_events join events on game_events.event_id=events.id where game_events.game_id=? group by events.id;', (str(self.game[3]),))
				self.events = cur.fetchall()
				if len(self.events):
					for game_event in self.events:
						b_game_event = Nav_btn(text='%s' % (game_event[0]))
						b_game_event.bind(on_press=partial(self._graph_popup, game_event[0],game_event[1]))
						bl.add_widget(b_game_event)
						bl.add_widget(List_btn(text='Total: %d'%(game_event[2]), background_color=(.5,0,.5,1)))
				else:
					bl.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))
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
			cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
			cur.execute('select player_name, count(player_name) from game_events where game_id=? and event_id=? group by player_name;', (str(self.game[3]), event_id))
			players_events = cur.fetchall()

			if len(players_events):
				for player in players_events:
					content.add_widget(List_btn(text=player[0], background_color=(.3,.3,.3,1)))
					content.add_widget(List_btn(text=str(player[1]), background_color=(0,0,0,1)))

			else:
				content.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))

		back_btn = Back_btn(text='Back')
		content.add_widget(back_btn)

		self.popup = Popup(title='%s - %s\'s statistics' % (self.team_name, event_name), content=content, size_hint=(1, 1))
		back_btn.bind(on_press=self.popup.dismiss)
		self.popup.open()		

	def on_back_pressed(self, *args):
		self.manager.current = '%s_%s_%s' % (self.team_name, self.opponent_name, self.date_game)
		self.manager.remove_widget(self.manager.get_screen(self.name))


class List_player_heats(Normal_screen):
	def __init__(self, team_name, player_name, **args):
		super(List_player_heats, self).__init__(**args)
		self.team_name = team_name
		self.player_name = player_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.add_widget(Title_lb(text='Choose an event'))
		bl.bind(minimum_height=bl.setter('height'))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(40), team_name varchar(40), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select name, id from events where team_name=?', (self.team_name,))
			self.list_events = cur.fetchall()
			if len(self.list_events):
				for event in self.list_events:
					b_event = Nav_btn(text=event[0])
					b_event.bind(on_press=partial(self._graph_popup, event[1]))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='There are no event records to show'))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def _graph_popup(self, event_id,  *args):
		try:
			
			content = GridLayout(cols=1)

			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()

				with open('temp_field.png', 'wb') as wf:
					wf.write(cur.execute('select field from teams where name=?;', (self.team_name,)).fetchone()[0])
				
				field = Img.open('temp_field.png')

				cur.execute('create table if not exists players(name varchar(100), team_name varchar(100),visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('select x, y from game_events where player_name=? and event_id=?;', (self.player_name, event_id))
				events_pos = cur.fetchall()
				events_pos = [(x, y) for x, y in events_pos if x > -1 and y > -1]
			if not len(events_pos):
				content.add_widget(Image(source='temp_field.png', allow_stretch=True))

			else:
				img = np.zeros((field.size[0],field.size[1]))
				for i, j in events_pos:   
					img[int(i*field.size[0]), int((1-j)*field.size[1])] += 10000000


				maximum = int(np.amax(img))

				img2 = Img.new('RGBA', (field.size[0],field.size[1]), "white") 
				pixels = img2.load()

				for i in range(img2.size[0]): 
					for j in range(img2.size[1]):
						try:
							pixels[i,j] = ((255 * int(img[i,j])) // maximum, 0, 0,(255 * int(img[i,j])) // maximum)
						except Exception as exc:
							pixels[i,j] = 0

				img2 = img2.filter(ImgF.MaxFilter(size=9))

				result = alpha_composite(img2, field)
				result.save('heat.png')

				im = Image(source='heat.png', allow_stretch=True)
				content.add_widget(im)
				im.reload()

			back_btn = Back_btn(text='Back')
			content.add_widget(back_btn)

			self.popup = Popup(title='Heat map', content=content, size_hint=(1, 1), separator_height=0, title_align='center')
			back_btn.bind(on_press=self.popup.dismiss)
			self.popup.open()		
		except Exception as exc:
			pp = W_popup('Did you forgot to add a field\' image?' ,'Error!')
			pp.open()			
			

	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_' + self.player_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


class List_team_heats(Normal_screen):
	def __init__(self, team_name, **args):
		super(List_team_heats, self).__init__(**args)
		self.team_name = team_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.add_widget(Title_lb(text='Choose an event'))
		bl.bind(minimum_height=bl.setter('height'))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(40), team_name varchar(40), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select name, id from events where team_name=?', (self.team_name,))
			self.list_events = cur.fetchall()
			if len(self.list_events):
				for event in self.list_events:
					b_event = Nav_btn(text=event[0])
					b_event.bind(on_press=partial(self._graph_popup, event[1]))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='There are no event records to show'))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def _graph_popup(self, event_id,  *args):
		try:
			
			content = GridLayout(cols=1)

			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()

				with open('temp_field.png', 'wb') as wf:
					wf.write(cur.execute('select field from teams where name=?;', (self.team_name,)).fetchone()[0])
				
				field = Img.open('temp_field.png')

				cur.execute('create table if not exists players(name varchar(100), team_name varchar(100),visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('select x, y from game_events where team_name=? and event_id=?;', (self.team_name, event_id))
				events_pos = cur.fetchall()
				events_pos = [(x, y) for x, y in events_pos if x > -1 and y > -1]
			if not len(events_pos):
				content.add_widget(Image(source='temp_field.png', allow_stretch=True))

			else:
				img = np.zeros((field.size[0],field.size[1]))
				for i, j in events_pos:   
					img[int(i*field.size[0]), int((1-j)*field.size[1])] += 10000000


				maximum = int(np.amax(img))

				img2 = Img.new('RGBA', (field.size[0],field.size[1]), "white") 
				pixels = img2.load()

				for i in range(img2.size[0]): 
					for j in range(img2.size[1]):
						try:
							pixels[i,j] = ((255 * int(img[i,j])) // maximum, 0, 0,(255 * int(img[i,j])) // maximum)
						except Exception as exc:
							pixels[i,j] = 0

				img2 = img2.filter(ImgF.MaxFilter(size=9))

				result = alpha_composite(img2, field)
				result.save('heat.png')

				im = Image(source='heat.png', allow_stretch=True)
				content.add_widget(im)
				im.reload()

			back_btn = Back_btn(text='Back')
			content.add_widget(back_btn)

			self.popup = Popup(title='Heat map', content=content, size_hint=(1, 1), separator_height=0, title_align='center')
			back_btn.bind(on_press=self.popup.dismiss)
			self.popup.open()		
		except Exception as exc:
			pp = W_popup('Did you forgot to add a field\' image?' ,'Error!')
			pp.open()			
			

	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


class List_game_heats(Normal_screen):
	def __init__(self, team_name, game, back_name, **args):
		super(List_game_heats, self).__init__(**args)
		self.team_name = team_name
		self.game = game
		self.back_name = back_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.add_widget(Title_lb(text='Choose an event'))
		bl.bind(minimum_height=bl.setter('height'))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(40), team_name varchar(40), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			cur.execute('select name, id from events where team_name=?', (self.team_name,))
			self.list_events = cur.fetchall()
			if len(self.list_events):
				for event in self.list_events:
					b_event = Nav_btn(text=event[0])
					b_event.bind(on_press=partial(self._graph_popup, event[1]))
					bl.add_widget(b_event)
			else:
				bl.add_widget(List_btn(text='There are no event records to show'))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def _graph_popup(self, event_id,  *args):
		try:
			
			content = GridLayout(cols=1)

			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()

				with open('temp_field.png', 'wb') as wf:
					wf.write(cur.execute('select field from teams where name=?;', (self.team_name,)).fetchone()[0])
				
				field = Img.open('temp_field.png')

				cur.execute('create table if not exists players(name varchar(100), team_name varchar(100),visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('select x, y from game_events where game_id=? and event_id=?;', (self.game[3], event_id))
				events_pos = cur.fetchall()
				events_pos = [(x, y) for x, y in events_pos if x > -1 and y > -1]
			if not len(events_pos):
				content.add_widget(Image(source='temp_field.png', allow_stretch=True))

			else:
				img = np.zeros((field.size[0],field.size[1]))
				for i, j in events_pos:   
					img[int(i*field.size[0]), int((1-j)*field.size[1])] += 10000000


				maximum = int(np.amax(img))

				img2 = Img.new('RGBA', (field.size[0],field.size[1]), "white") 
				pixels = img2.load()

				for i in range(img2.size[0]): 
					for j in range(img2.size[1]):
						try:
							pixels[i,j] = ((255 * int(img[i,j])) // maximum, 0, 0,(255 * int(img[i,j])) // maximum)
						except Exception as exc:
							pixels[i,j] = 0

				img2 = img2.filter(ImgF.MaxFilter(size=9))

				result = alpha_composite(img2, field)
				result.save('heat.png')

				im = Image(source='heat.png', allow_stretch=True)
				content.add_widget(im)
				im.reload()

			back_btn = Back_btn(text='Back')
			content.add_widget(back_btn)

			self.popup = Popup(title='Heat map', content=content, size_hint=(1, 1), separator_height=0, title_align='center')
			back_btn.bind(on_press=self.popup.dismiss)
			self.popup.open()		
		except Exception as exc:
			pp = W_popup('Did you forgot to add a field\' image?' ,'Error!')
			pp.open()			
			

	def on_back_pressed(self, *args):
		self.manager.current = self.back_name
		self.manager.remove_widget(self.manager.get_screen(self.name))

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
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				cur.execute('select events.name, game_events.player_name, game_events.time from game_events join events on game_events.event_id=events.id where game_events.game_id=?;', (str(self.game[3]),))
				game_events = cur.fetchall()
				if len(game_events):
					for game_event in game_events:
						if game_event[2] == -1:
							b_game_event = List_btn(text=' ? | %s | %s ' % (game_event[0], game_event[1]), background_color=(1,0,1,1))
						else:
							b_game_event = List_btn(text=' %d | %s | %s' % (game_event[2], game_event[0], game_event[1]), background_color=(1,0,1,1))
						bl.add_widget(b_game_event)
				else:
					bl.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))
			except Exception as exc:
				print(exc)
				pp = W_popup(exc ,'Error!')
				pp.open()

		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def on_back_pressed(self, *args):
		self.manager.current = '%s_%s_%s' % (self.team_name, self.opponent_name, self.date_game)
		self.manager.remove_widget(self.manager.get_screen(self.name))
