from kivy.utils import platform
if platform == 'android':
    import android

import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.filechooser import FileChooser, FileChooserIconLayout, FileChooserListLayout
from kivy.core.window import Window

from style import *
from teams import Create_team, List_teams

###################################################


class Menu(Normal_screen):
    def __init__(self, **args):
        super(Menu, self).__init__(**args)

                root = ScrollView()

                bl = Base_layout()
                bl.bind(minimum_height=bl.setter('height'))


                bl.add_widget(Title_lb(text='AllSports'))

                self.warning = Title_lb(text='')
                bl.add_widget(self.warning)

                create = New_btn(text='Create team')
                create.bind(on_press=self._go_create)
                bl.add_widget(create)

                choose = Nav_btn(text='Choose team')
                choose.bind(on_press=self._go_choose)
                bl.add_widget(choose)

                save = List_btn(text='Save database', background_color=(1,1,0,1))
                save.bind(on_press=partial(self.filechooser, True))
                bl.add_widget(save)

                load = List_btn(text='Load database',background_color=(1,1,0,1))
                load.bind(on_press=partial(self.filechooser, False))
                bl.add_widget(load)

                b_exit = Back_btn(text='Exit')
                b_exit.bind(on_press=sys.exit)
                bl.add_widget(b_exit)

                root.add_widget(bl)
                self.add_widget(root)


        def on_back_pressed(self, *args):
            sys.exit()

        def _go_create(self, *args):
            self.warning.text = ''
                self.manager.current = 'createteam'

        def _go_choose(self, *args):
            self.warning.text = ''
                self.manager.current = 'list_teams'

        def _save(self, *args):
            self.pp.dismiss()
                try:
                    #sd_path = App.get_running_app().user_data_dir
                        #sd_path_file = os.path.join(sd_path, 'allsports_backup.db')
                        sd_path_file = str(self.fc.path) + '/allsports_backup.db'
                        print(self.fc.path,sd_path_file)
                        with open('allsports.db', 'rb') as r:
                            with open(sd_path_file, 'wb') as w:
                                for i in r:
                                    w.write(i)
                except Exception as exc:
                    print(exc)
                        self.warning.text = 'Error saving database. Is it empty?'
                        self.warning.color = (1,0,0,1)
                else:
                    self.warning.text = 'Database successfuly saved'
                        self.warning.color = (0,1,0,1)

        def _load(self, *args):
            try:
                #sd_path = App.get_running_app().user_data_dir
                        #sd_path_file = os.path.join(sd_path, 'allsports_backup.db')
                        sd_path_file = self.fc.selection[0].encode('utf-8')
                        print(sd_path_file)
                        with open(sd_path_file, 'rb') as r:
                            with open('allsports.db', 'wb') as w:
                                self.pp.dismiss()
                                        for i in r:
                                            w.write(i)
            except Exception as exc:
                print(exc)
                        self.pp.title = 'You have to select an AllSports\' database file'
                        self.warning.text = 'Error loading database.'
                        self.warning.color = (1,0,0,1)
                else:
                    self.warning.text = 'Database successfuly loaded'
                        self.warning.color = (0,1,0,1)

        def filechooser(self, save_flag, *args):
            self.warning.text = ''
                root = BoxLayout(orientation='vertical')
                bl = BoxLayout(size_hint_y=.1)


                self.fc = FileChooser(multiselect=True, dirselect=True)

                b_open = Button(text='Confirm', size_hint_x=0.1)
                bl.add_widget(b_open)

                b_cancel = Button(text='Cancel', size_hint_x=0.1)
                bl.add_widget(b_cancel)

                b_view = Button(text='List/Icon View', size_hint_x=0.1)
                bl.add_widget(b_view)
                root.add_widget(bl)

                b_view.bind(on_press=self.change_view)

                self.fc.add_widget(FileChooserListLayout())
                self.fc.add_widget(FileChooserIconLayout())
                root.add_widget(self.fc)

                if save_flag:
                    title = 'Get inside the destination folder'
                else:
                    title = 'Select your backup file'

                self.pp = Popup(title=title, content=root)
                if save_flag:
                    b_open.bind(on_press=self._save)
                else:
                    b_open.bind(on_press=self._load)
                b_cancel.bind(on_press=self.exit_popup)
                self.pp.open()

        def exit_popup(self, *args):
            self.warning.text = ''
                self.pp.dismiss()

        def change_view(self, *args):
            if self.fc.view_mode == 'list':
                self.fc.view_mode = 'icon'
            else:
                self.fc.view_mode = 'list'



###################################################

sm = ScreenManager(transition = NoTransition())
sm.add_widget(Menu(name='menu'))
sm.add_widget(Create_team(name='createteam'))
sm.add_widget(List_teams(name='list_teams'))


class AllSports(App):
    Window.clearcolor = (0,0,0,0)

        def build(self):
            self.icon = 'icon.png'
                self.bind(on_start=self._post_build_init)
                return sm

        def _post_build_init(self, ev):
            if platform == 'android':
                android.map_key(android.KEYCODE_BACK, 1000)
                        android.map_key(android.KEYCODE_MENU, 1001)
                win = self._app_window
                win.bind(on_keyboard=self._key_handler)

        def _key_handler(self, window, key, *args):
            if key in (1000, 27):
                sm.current_screen.dispatch("on_back_pressed")
                        return True
                elif key == 1001:
                    sm.current_screen.dispatch("on_menu_pressed")
                        return True

        def on_pause(self, *args):
            return True

if __name__ == '__main__':
    AllSports().run()
