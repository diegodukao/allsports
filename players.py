from style import *
from statistics import List_player_stats

class List_players(Normal_screen):
	def __init__(self, team_name, **args):
		super(List_players, self).__init__(**args)
		self.team_name = team_name
		
	def on_enter(self, **args):
		self.clear_widgets()
		
		root = ScrollView()

		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		bl.add_widget(Title_lb(text='Players'))
		
		conn = lite.connect('allsports.db')
		with conn:
			cur = conn.cursor()
			cur.execute('create table if not exists players(name varchar(100), team_name varchar(100), visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
			cur.execute('select name from players where team_name=? and visible=1;', (self.team_name,))
			names = cur.fetchall()
			if len(names):
				for name in names:
					b_player = List_btn(text=name[0], background_color=(.7,0,1,1))
					b_player.bind(on_press=partial(self._go_player, b_player))
					bl.add_widget(b_player)
			else:
				bl.add_widget(List_btn(text='No records to show', background_color=(0,0,0,1)))
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)

		root.add_widget(bl)
		self.add_widget(root)
		
	def _go_player(self, player_name, *args):
		if not self.manager.has_screen(self.team_name + '_' + player_name.text):
			self.manager.add_widget(Player(self.team_name, player_name.text, name=self.team_name + '_' + player_name.text))
		self.manager.current = self.team_name + '_' + player_name.text
		
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


###################################################
class Create_player(Normal_screen):
	def __init__(self, team_name, **args):
		super(Create_player, self).__init__(**args)
		self.team_name = team_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='New player'))
		
		fl = Form_layout()
		
		fl.add_widget(Form_lb(text='Name:'))
		self.ti_name = TextInput(hint_text='Write your player\'s name', multiline=False)
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
				cur.execute('create table if not exists players(name varchar(100), team_name varchar(100),visible integer, foreign key(team_name) references teams(name) on delete cascade on update cascade, primary key(name, team_name));')
				cur.execute('insert into players (name, team_name, visible) values(?, ?, 1);', (self.ti_name.text, self.team_name))
		except Exception as exc:
			print(exc)
			self.ti_name.hint_text = '\"%s\" is already taken, choose another name'%(self.ti_name.text)
			self.ti_name.text = ''
		else:
			self.manager.current = self.team_name
			self.manager.remove_widget(self.manager.get_screen(self.name))
		

	def on_back_pressed(self, *args):
		self.manager.current = self.team_name
		self.manager.remove_widget(self.manager.get_screen(self.name))


###################################################
class Player(Normal_screen):
	def __init__(self, team_name, player_name, **args):
		super(Player, self).__init__(**args)
		self.player_name = player_name
		self.team_name = team_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Player: %s'%(player_name)))

		b_stats = List_btn(text='Statistics', background_color=(1,1,0,1))
		b_stats.bind(on_press=self._go_list_stats)
		bl.add_widget(b_stats)

		b_rename = Nav_btn(text='Rename')
		b_rename.bind(on_press=self._go_rename)
		bl.add_widget(b_rename)

		b_delete = Red_btn(text='Delete')
		b_delete.bind(on_press=self._confirm_popup)
		bl.add_widget(b_delete)
		
		b_back = Back_btn(text='Back')
		b_back.bind(on_press=self.on_back_pressed)
		bl.add_widget(b_back)
		
		root.add_widget(bl)
		self.add_widget(root)

	def _go_list_stats(self, *args):
		if not self.manager.has_screen(self.team_name + '_' + self.player_name + '_list_stats'):
			self.manager.add_widget(List_player_stats(self.team_name, self.player_name, name=self.team_name + '_' + self.player_name + '_list_stats'))
		self.manager.current = self.team_name + '_' + self.player_name + '_list_stats'

	def _confirm_popup(self, *args):
		content = GridLayout(cols=2)
		confirm_btn = Button(text='Confirm', background_color=(1, 0, 0, 1))
		content.add_widget(confirm_btn)
		cancel_btn = Button(text='Cancel')
		content.add_widget(cancel_btn)

		self.popup = Popup(title="Confirm you want to delete %s records" % (self.player_name), content=content, size_hint=(0.8, 0.4))
		cancel_btn.bind(on_press=self.popup.dismiss)
		confirm_btn.bind(on_press=self.delete_player)
		self.popup.open()

	def _go_rename(self, *args):
		if not self.manager.has_screen(self.team_name + self.player_name + '_rename_player'):
			self.manager.add_widget(Rename_player(self.team_name, self.player_name, name=self.team_name + self.player_name + '_rename_player'))
		self.manager.current = self.team_name + self.player_name + '_rename_player'

	def delete_player(self, *args):
		self.popup.dismiss()
		try:
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				cur.execute('select * from teams')
				res = cur.fetchall()
				res = sum([ord(j) for i in res for j in i])
				cur.execute('select * from game_events')
				res2 = cur.fetchall()
				try:
					res += sum([ord(j) for i in res2 for j in i])
				except:
					pass
				rand = random.randint(0, res*1000000)
				print(rand)
				cur.execute('update players set visible=0, name=? where name=? and team_name=?', (self.player_name+'_removed_'+str(rand), self.player_name, self.team_name))
			self.manager.current = self.team_name
			self.manager.remove_widget(self.manager.get_screen(self.name))
		except Exception as exc:
			print(exc)

	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_list_players'
		self.manager.remove_widget(self.manager.get_screen(self.name))
	

class Rename_player(Normal_screen):
	def __init__(self, team_name, player_name, **args):
		super(Rename_player, self).__init__(**args)
		self.team_name = team_name
		self.player_name = player_name
		
		root = ScrollView()
	
		bl = Base_layout()
		bl.bind(minimum_height=bl.setter('height'))
		
		bl.add_widget(Title_lb(text='Rename player'))
		
		fl = Form_layout()
		
		fl.add_widget(Form_lb(text='New name:'))
		self.new_player_name = TextInput(hint_text='Write new player\'s name', multiline=False)
		fl.add_widget(self.new_player_name)
		
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
		self.new_player_name.focus = True
	
	def _confirm(self, *args):
		try:	
			with lite.connect('allsports.db') as conn:
				cur = conn.cursor()
				cur.execute('pragma foreign_keys = on;')
				cur.execute('update players set name=? where name=? and team_name=?;', (self.new_player_name.text, self.player_name, self.team_name))
			self.new_player_name.text = ''
		except Exception as exc:
			print(exc)
			self.new_player_name.hint_text = '\"' + self.new_player_name.text + '\" is already taken, choose another name'
		else:
			self.manager.current = self.team_name + '_list_players'
			self.manager.remove_widget(self.manager.get_screen(self.name))
			
	def on_back_pressed(self, *args):
		self.manager.current = self.team_name + '_list_players'
		self.manager.remove_widget(self.manager.get_screen(self.name))
