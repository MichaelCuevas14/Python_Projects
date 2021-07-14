import random

from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder


Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget
import os

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up, keyboard_closed

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(8)
    perspective_point_y = NumericProperty(0)

    v_nb_lines = 10
    v_lines_spacing =.25 # percentage screen width
    horizontal_lines = []

    h_nb_lines = 15
    h_lines_spacing = .1  # percentage screen height
    vertical_lines = []

    current_offset_y = 0
    speed = 0.5
    speed_x = 3
    current_speed_x = 0
    current_offset_x = 0
    current_y_loop = 0

    nb_tiles = 20
    tiles = []
    tiles_coordinates = []

    ship_width = .1
    ship_height = 0.035
    ship_base_y = 0.04
    ship = None
    ship_coordinates = [(0,0), (0,0), (0,0)]

    state_game_over = False
    state_game_has_started = False

    menu_title = StringProperty("G a l a x y")
    menu_button_title = StringProperty("START")
    score_txt = StringProperty("0")
    high_score = StringProperty("0")
    high_score_txt = StringProperty("")

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart =None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.get_high_score()


        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_impact.volume = .6
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25

    def reset_game(self):
        self.get_high_score()
        self.current_offset_y = 0
        self.current_speed_x = 0
        self.speed = 0.5
        self.current_offset_x = 0
        self.current_y_loop = 0
        self.score_txt = "SCORE: " + str(self.current_y_loop)
        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()

        self.state_game_over = False

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width/2
        base_y = self.ship_base_y * self.height
        ship_half_width = self.ship_width * self.width / 2
        ship_height = self.ship_height * self.height

        self.ship_coordinates[0] = (center_x-ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x+ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y =self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False


    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.nb_tiles):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        for i in range(len(self.tiles_coordinates), self.nb_tiles):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.v_nb_lines / 2) + 1
            end_index = start_index + self.v_nb_lines - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y+=1

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
           # self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.v_nb_lines):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.v_lines_spacing * self.width
        offset = index - 0.5
        line_x = central_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.h_lines_spacing * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.nb_tiles):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)


            # 2  3
            #
            # 1  4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)


            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.v_nb_lines/2)+1

        for i in range(start_index,start_index + self.v_nb_lines):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]


    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.h_nb_lines):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.v_nb_lines / 2) + 1
        end_index = start_index +self.v_nb_lines-1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)


        for i in range(0, self.h_nb_lines):
            line_y =self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if self.current_y_loop > int(self.high_score):
            self.save_highscore()



        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.speed * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.h_lines_spacing * self.height


            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE: " + str(self.current_y_loop)
                if self.speed < 1.3:
                    self.speed += .005

                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:


            self.state_game_over = True
            self.menu_title = "G A M E     O V E R"
            self.menu_button_title = "RESTART?"
            self.menu_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 1.5)


    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()


    def on_menu_button_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0

    def save_highscore(self):
        if self.current_y_loop > int(self.high_score):
            with open('save.txt', 'w') as f:
                    print(self.score_txt)
                    print(self.high_score)
                    f.write(str(self.current_y_loop))
                    f.close()



    def get_high_score(self):
        if os.path.isfile('save.txt'):
            with open('save.txt', 'r') as f:
                self.high_score = str(f.read())
                self.high_score_txt = "HIGH SCORE: " + self.high_score
                f.close()



class GalaxyApp(App):
    pass


GalaxyApp().run()
