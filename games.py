from style import *

from statistics import Game_stats, List_game_heats, List_game_events, List_game_temp
from records import List_game_records

class Create_game(Normal_screen):
	def __init__(self, team_name, **args):
		super(Create_game, self).__init__(**args)
		self.team_name = team_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='New game'))
		
		fl = Form_layout()
		
		fl.add_widget(Form_lb(text='Opponent:'))
		self.ti_opponent_name = TextInput(hint_text='Write your opponent\'s name', multiline=False)
		fl.add_widget(self.ti_opponent_name)
		
		fl.add_widget(Form_lb(text='Game\'s date:'))
		self.ti_date = TextInput(hint_text='YYYY-MM-DD', multiline=False)
		fl.add_widget(self.ti_date)
		
		
		b_conf = Form_btn(text='Confirm', background_color=(.5,.8,.5,1))
		b_conf.bind(on_release=self._confirm)
		b_cancel = Form_btn(text='Cancel')
		b_cancel.bind(on_release=self.on_back_pressed)
		
		fl.add_widget(b_conf)
		fl.add_widget(b_cancel)
		bl.add_widget(fl)
		
		root.add_widget(bl)
		self.add_widget(root)

	def on_enter(self, **args):
		self.ti_opponent_name.focus = True
	
	def _confirm(self, *args):
		self.ti_opponent_name.focus = False
		self.ti_date.focus = False

		aux = self.ti_date.text.strip()
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
		if self.ti_opponent_name.focus == True: 
			self.ti_opponent_name.focus = False
		elif self.ti_date.focus == True:
			self.ti_date.focus = False
		else:
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
			cur.execute('select opponent_name, date, open, id from games where team_name=? order by date desc;', (self.team_name,))
			games = cur.fetchall()
			if len(games):
				for game in games:
					b_game = List_btn(text='%s | %s' % (game[0], game[1]))
					if game[2]:
						b_game.bind(on_release=partial(self._go_open_game, game))
						b_game.background_color = (1, 1, 0, 1)
					else:	
						b_game.bind(on_release=partial(self._go_closed_game, game))
					bl.add_widget(b_game)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(1,1,1,0)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_release=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)
	
	def _go_open_game(self, game, *args):
		opponent, date = game[0], game[1]
		if not self.manager.has_screen('%s_%s_%s' % (self.team_name, opponent, date)):
			self.manager.add_widget(Open_game(self.team_name, game, name='%s_%s_%s' % (self.team_name, opponent, date)))
		self.manager.current = '%s_%s_%s' % (self.team_name, opponent, date)

	def _go_closed_game(self, game, *args):
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

		bl.add_widget(Title_lb(text='Finished', color=(1,0,0,1)))
		bl.add_widget(Title_lb(text= '%s vs %s' % (self.team_name, self.opponent_name)))
		bl.add_widget(Title_lb(text=self.date_game))
		
		b_stats = List_btn(text='Statistics', background_color=(1,1,0,1))
		b_stats.bind(on_release=self._go_game_stats)
		bl.add_widget(b_stats)

		b_heat = List_btn(text='Heat', background_color=(0,1,1,1))
		b_heat.bind(on_release=self._go_list_game_heats)
		bl.add_widget(b_heat)

		b_temp = Nav_btn(text='Temporal', background_color=(1,.5,.5,1))
		b_temp.bind(on_release=self._go_list_game_temp)
		bl.add_widget(b_temp)

		if platform == 'android':

			b_list_game_records = Nav_btn(text='Records\' List', background_color=(1,0,1,1))
			b_list_game_records.bind(on_release=self._go_list_records)
			bl.add_widget(b_list_game_records)

			b_remove_records = Red_btn(text='Remove Records')
			b_remove_records.bind(on_release=self._confirm_popup_rec)
			bl.add_widget(b_remove_records)		

		b_list_game_events = Nav_btn(text='List')
		b_list_game_events.bind(on_release=self._go_list_game_events)
		bl.add_widget(b_list_game_events)

		b_delete = Red_btn(text='Delete')
		b_delete.bind(on_release=self._confirm_popup)
		bl.add_widget(b_delete)

		b_back = Back_btn(text='Back')
		b_back.bind(on_release=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)


	def _confirm_popup_rec(self, *args):
		content = GridLayout(cols=2)
		confirm_btn = Button(text='Confirm', background_color=(1, 0, 0, 1))
		content.add_widget(confirm_btn)
		cancel_btn = Button(text='Cancel')
		content.add_widget(cancel_btn)

		self.popup = Popup(title="Confirm you want to delete this game's records", content=content, size_hint=(0.8, 0.4))
		cancel_btn.bind(on_release=self.popup.dismiss)
		confirm_btn.bind(on_release=self._remove_records)
		self.popup.open()

	def _remove_records(self, *args):
		self.popup.dismiss()
		conn = lite.connect('allsports.db')
		try:
			with conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				cur.execute('create table if not exists records(id integer primary key autoincrement, game_id integer, tape blob, foreign key (game_id) references games(id) on delete cascade on update cascade);')
				cur.execute('delete from records where game_id=?;', (self.game[3],))
				pp = W_popup('Records successfuly removed.', 'Success!')
				pp.open()
		except Exception as exc:
			pp = W_popup(str(exc) ,'Error!')
			pp.open()

	def _go_list_game_heats(self, *args):
		if not self.manager.has_screen('%s_%s_%s_heats' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_heats(self.team_name, self.game, self.name, name='%s_%s_%s_heats' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_heats' % (self.team_name, self.opponent_name, self.date_game)

	def _go_list_game_events(self, *args):
		if not self.manager.has_screen('%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_events(self.team_name, self.game, name='%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)

	def _go_list_game_temp(self, *args):
		if not self.manager.has_screen('%s_%s_%s_temp' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_temp(self.team_name, self.game, name='%s_%s_%s_temp' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_temp' % (self.team_name, self.opponent_name, self.date_game)

	def _go_game_stats(self, *args):
		if not self.manager.has_screen('%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(Game_stats(self.team_name, self.game, name='%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)

	def _go_list_records(self, *args):
		if not self.manager.has_screen('%s_%s_%s_records' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_records(self.team_name, self.game, self.name, name='%s_%s_%s_records' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_records' % (self.team_name, self.opponent_name, self.date_game)

	def _confirm_popup(self, *args):
		content = GridLayout(cols=2)
		confirm_btn = Button(text='Confirm', background_color=(1, 0, 0, 1))
		content.add_widget(confirm_btn)
		cancel_btn = Button(text='Cancel')
		content.add_widget(cancel_btn)

		self.popup = Popup(title="Confirm you want to delete this game from database", content=content, size_hint=(0.8, 0.4))
		cancel_btn.bind(on_release=self.popup.dismiss)
		confirm_btn.bind(on_release=self._delete_game)
		self.popup.open()

	def _delete_game(self, *args):
		self.popup.dismiss()
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('pragma foreign_keys = on;')
			cur.execute('delete from games where id=?;', (self.game[3],))

		self.on_back_pressed()

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
		self.mRecorder = None
		self.rec = False
		
		root = BoxLayout(orientation='vertical')
		
		root.add_widget(Title_lb(text='Running: %s vs %s' % (self.team_name, self.opponent_name), color=(0,1,0,1)))

		if platform == 'android':
			bl = BoxLayout(size_hint_y=.15)

			bl_voice_record = Form_btn(text='Rec', background_color=(0,1,0,1))
			bl_voice_record.bind(on_release=self._record_voice)
			bl.add_widget(bl_voice_record)

			bl_list_records = Form_btn(text='Recs')
			bl_list_records.bind(on_release=self._go_list_records)
			bl.add_widget(bl_list_records)

			root.add_widget(bl)

		bl_buttons = BoxLayout(size_hint_y=.15)
		
		b_add_event = New_btn(text='Add', size_hint_y=1)
		b_add_event.bind(on_release=partial(self._event_popup, -1, -1))
		bl_buttons.add_widget(b_add_event)

		b_stats = List_btn(text='Stats', background_color=(1,1,0,1), size_hint_y=1)
		b_stats.bind(on_release=self._go_game_stats)
		bl_buttons.add_widget(b_stats)

		b_heat = List_btn(text='Heat', background_color=(0,1,1,1), size_hint_y=1)
		b_heat.bind(on_release=self._go_list_game_heats)
		bl_buttons.add_widget(b_heat)

		b_list_game_events = Nav_btn(text='Events', size_hint_y=1)
		b_list_game_events.bind(on_release=self._go_list_game_events)
		bl_buttons.add_widget(b_list_game_events)

		b_close = Red_btn(text='Close', size_hint_y=1)
		b_close.bind(on_release=self._confirm_popup)
		bl_buttons.add_widget(b_close)

		b_back = Back_btn(text='Back', size_hint_y=1)
		b_back.bind(on_release=self.on_back_pressed)
		bl_buttons.add_widget(b_back)

		root.add_widget(bl_buttons)
		try:
			with lite.connect('allsports.db') as con:
				cur = con.cursor()
				with open('temp_field.png', 'wb') as wf:
					wf.write(cur.execute('select field from teams where name=?;', (self.team_name,)).fetchone()[0])

			self.b_field = IconButton(source='temp_field.png', allow_stretch=True, keep_ratio=False)
			self.b_field.reload()
			self.b_field.bind(on_touch_down=self._click)
			root.add_widget(self.b_field)
		except Exception as exc:
			pp = W_popup('Add a field image at Team\'s menu!' ,'Error!')
			pp.open()
		
		self.add_widget(root)

	def _record_voice(self, button, *args):
		try:
			if self.rec:
				self.mRecorder.stop()
				self.rec = False
				button.background_color = (0, 1, 0, 1)

				conn = lite.connect('allsports.db')
				try:
					with conn:
						cur = conn.cursor()
						cur.execute('pragma foreign_keys = on;')
						cur.execute('create table if not exists records(id integer primary key autoincrement, game_id integer, tape blob, foreign key (game_id) references games(id) on delete cascade on update cascade);')
						cur.execute('insert into records (game_id, tape) values(?,?);', (self.game[3], lite.Binary(open('/sdcard/temp_record.mp3', 'rb').read())))
						pp = W_popup('Audio successfuly recorded.', 'Success!')
						os.remove('/sdcard/temp_record.mp3')
						pp.open()
				except Exception as exc:
					pp = W_popup(str(exc) ,'Error!')
					pp.open()

			else:
				MediaRecorder = autoclass('android.media.MediaRecorder')
				AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
				OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
				AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

				self.mRecorder = MediaRecorder()
				self.mRecorder.setAudioSource(AudioSource.MIC)
				self.mRecorder.setOutputFormat(OutputFormat.MPEG_4)
				self.mRecorder.setOutputFile('/sdcard/temp_record.mp3')
				self.mRecorder.setAudioEncoder(AudioEncoder.AAC)
				self.mRecorder.prepare()
				self.mRecorder.start()
				self.rec = True
				button.background_color = (1, 0, 0, 1)
		except Exception as exc:
			pp = W_popup(str(exc) ,'Error!')
			pp.open()

	def _click(self, *args):
		if self.b_field.collide_point(*args[1].pos):
			self._event_popup(args[1].pos[0]/self.b_field.size[0], args[1].pos[1]/self.b_field.size[1])

	def _go_list_game_events(self, *args):
		if not self.manager.has_screen('%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_events(self.team_name, self.game, name='%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_events' % (self.team_name, self.opponent_name, self.date_game)

	def _go_game_stats(self, *args):
		if not self.manager.has_screen('%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(Game_stats(self.team_name, self.game, name='%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_stats' % (self.team_name, self.opponent_name, self.date_game)

	def _go_list_game_heats(self, *args):
		if not self.manager.has_screen('%s_%s_%s_heats' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_heats(self.team_name, self.game, self.name, name='%s_%s_%s_heats' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_heats' % (self.team_name, self.opponent_name, self.date_game)

	def _go_list_records(self, *args):
		if not self.manager.has_screen('%s_%s_%s_records' % (self.team_name, self.opponent_name, self.date_game)):
			self.manager.add_widget(List_game_records(self.team_name, self.game, self.name, name='%s_%s_%s_records' % (self.team_name, self.opponent_name, self.date_game)))
		self.manager.current = '%s_%s_%s_records' % (self.team_name, self.opponent_name, self.date_game)
	
	def _confirm_popup(self, *args):
		content = GridLayout(cols=2)
		confirm_btn = Button(text='Confirm')
		content.add_widget(confirm_btn)
		cancel_btn = Button(text='Cancel')
		content.add_widget(cancel_btn)

		self.popup = Popup(title="Confirm you want to close this game", content=content, size_hint=(0.8, 0.4))
		cancel_btn.bind(on_release=self.popup.dismiss)
		confirm_btn.bind(on_release=self._close_game)
		self.popup.open()

	def _close_game(self, *args):
		self.popup.dismiss()
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('pragma foreign_keys = on;')
			cur.execute('update games set open=0 where id=?', (self.game[3],))
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))

	def _event_popup(self, x, y, *args):
		content = ScrollView()
		root = GridLayout(cols=2)
		root.bind(minimum_height=root.setter('height'))

		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists events(id integer primary key autoincrement, name varchar(100), team_name varchar(100), foreign key (team_name) references teams(name) on delete cascade on update cascade);')
			self.events_results = cur.execute('select id, name from events where team_name=?', (self.team_name,))

		self.events_list = Drop_list(text="Select an event", values=tuple(i[1] for i in self.events_results))
		root.add_widget(self.events_list)
		
		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('create table if not exists players(name char(40), team_name char(40), visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
			players_results = cur.execute('select name from players where team_name=? and visible=1', (self.team_name,))

		self.players_list = Drop_list(text="Select a player", values=tuple(i[0] for i in players_results))
		root.add_widget(self.players_list)

		root.add_widget(Form_lb(text='Event\'s time:', size_hint_y=None, height=button_h))
		self.ti_time = TextInput(hint_text='optional', multiline=False, input_filter='int', size_hint_y=None, height=button_h)
		root.add_widget(self.ti_time)

		confirm_btn = Form_btn(text='Confirm')
		confirm_btn.bind(on_release=partial(self._confirm_event, x, y))
		root.add_widget(confirm_btn)
		cancel_btn = Form_btn(text='Cancel')
		root.add_widget(cancel_btn)
		content.add_widget(root)

		self.popup = Popup(title="New event",
              content=content,
              size_hint=(1, 1))
		cancel_btn.bind(on_release=self.cancel_popup)
		self.popup.open()

	def cancel_popup(self, *args):
		if self.ti_time.focus == True:
			self.ti_time.focus = False
		else:
			self.popup.dismiss()

	def on_back_pressed(self, *args):
		if platform == 'android' and self.mRecorder:
			self.mRecorder.release()
		self.manager.current = self.team_name + '_list_games'
		self.manager.remove_widget(self.manager.get_screen(self.name))

	def _confirm_event(self, x, y, *args):
		self.ti_time.focus = False

		with lite.connect('allsports.db') as conn:
			cur = conn.cursor()
			cur.execute('select games_length from teams where name=?;', (self.team_name,))
			games_length = cur.fetchall()[0][0]

		if self.ti_time.text and (int(self.ti_time.text) > games_length or int(self.ti_time.text) < 1):
			pp = W_popup('Time of event must be empty or between 1-%d!'%games_length ,'Error!')				
			pp.open()
			return

		if self.events_list.text!="Select an event" and self.players_list.text != "Select a player":
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				event_id = cur.execute('select id from events where team_name=? and name=?;', (self.team_name, self.events_list.text))
				event_id = [i for i in event_id][0][0]
				cur.execute('create table if not exists game_events(id integer primary key autoincrement, event_id integer, team_name varchar(100), player_name varchar(100), game_id integer, time numeric, x float, y float, foreign key (event_id) references events(id) on update cascade on delete cascade, foreign key (game_id) references games(id) on update cascade on delete cascade, foreign key (player_name, team_name) references players(name, team_name) on update cascade on delete cascade);')
				if self.ti_time.text:
					cur.execute('insert into game_events(event_id, team_name, player_name, game_id, x, y, time) values(?, ?, ?, ?, ?, ?, ?);', (event_id, self.team_name, self.players_list.text, str(self.game[3]), x, y, int(self.ti_time.text)))
				else:
					cur.execute('insert into game_events(event_id, team_name, player_name, game_id, x, y, time) values(?, ?, ?, ?, ?, ?, ?);', (event_id, self.team_name, self.players_list.text, str(self.game[3]), x, y, -1))

			self.popup.dismiss()

		
