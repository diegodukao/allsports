from style import *

class List_game_records(Normal_screen):
	def __init__(self, team_name, game, back_name, **args):
		super(List_game_records, self).__init__(**args)
		self.team_name = team_name
		self.game = game
		self.back_name = back_name
		self.sound = None
		self.record = None
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		bl.add_widget(Title_lb(text="Records' List"))
		
		conn = lite.connect('allsports.db')
		try:
			with conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				cur.execute('create table if not exists records(id integer primary key autoincrement, game_id integer, tape blob, foreign key (game_id) references games(id) on delete cascade on update cascade);')
				cur.execute('select id, tape from records where game_id=? order by game_id desc', (self.game[3],))
				self.list_records = cur.fetchall()
				
				if len(self.list_records):
					for record in self.list_records:
						b_record = Nav_btn(text=str(record[0]))
						b_record.bind(on_release=partial(self.play_stop, record))
						bl.add_widget(b_record)
				else:
					bl.add_widget(List_btn(text='There are no game records to show'))
		except Exception as exc:
			pp = W_popup(str(exc) ,'Error!')
			pp.open()

		b_back = Back_btn(text='Back')
		b_back.bind(on_release=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)

	def play_stop(self, record, *args):		
		if self.sound and self.sound.state == 'play':
			self.sound.stop()

		else:
			if self.record != record[0]:
				self.record = record[0]
				with open('/sdcard/temp_record.mp3', 'wb') as wf:
					wf.write(record[1])

				self.sound = SoundLoader.load('/sdcard/temp_record.mp3') 
			
			try:		
				self.sound.play()
				
			except Exception as exc:
				pp = W_popup(str(exc) ,'Error!')
				pp.open()

	def on_back_pressed(self, *args):
		self.manager.current = self.back_name
		self.manager.remove_widget(self.manager.get_screen(self.name))