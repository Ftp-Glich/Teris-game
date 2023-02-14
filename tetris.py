from ursina import *
import datetime
app = Ursina()


class PAudio(object):
    def __init__(self, p_sound):
        self.sound = p_sound
        self.s = Audio(volume=5)

    def play_sound(self):
        self.s = Audio(self.sound, volume=5)

    def p_pause(self):
        self.s.pause()

    def p_resume(self):
        self.s.resume()


class Counter(object):
    def __init__(self):
        self.text = dedent('<scale:1.5>0').strip()
        self.score_field = Text()
        self.score = 0

    def set_score(self, lines_amount):
        if lines_amount == 1:
            self.score += 100
        elif lines_amount == 0:
            return 0
        elif lines_amount == 2:
            self.score += 300
        elif lines_amount == 3:
            self.score += 700
        else:
            self.score += 1500
        self.update_text()

    def update_text(self):
        self.text = dedent('<scale:1.5>' + str(self.score)).strip()

    def show_text(self):
        self.score_field.enabled = False
        self.score_field = Text(text=self.text, origin=(-1, -15), background=False)


class Border(object):
    def __init__(self, b_width, b_high, b_box_coord):
        self.width = b_width
        self.high = b_high
        self.box_coord = b_box_coord
        self.border_elements = [], [], [], []

    def building(self):
        for v_l in range(self.high + 3):
            self.border_elements[0].append(Sprite(model='quad', color=color.red, texture='Cube'))
            self.border_elements[0][v_l].position = (self.box_coord[0], v_l * .25 - 4)
        for v_r in range(self.high + 3):
            self.border_elements[1].append(Sprite(model='quad', color=color.red, texture='Cube'))
            self.border_elements[1][v_r].position = (self.box_coord[0] + self.width * .25, v_r * .25 - 4)
        for h_b in range(self.width):
            self.border_elements[2].append(Sprite(model='quad', color=color.red, texture='Cube'))
            self.border_elements[2][h_b].position = (self.box_coord[0] + h_b * .25, self.box_coord[1])
        for h_u in range(self.width):
            self.border_elements[3].append(Sprite(model='quad', color=color.red, texture='Cube'))
            self.border_elements[3][h_u].position = (self.box_coord[0] + .25 + h_u * .25,
                                                     self.box_coord[1] + (self.high + 2) * .25)


class Row(object):
    def __init__(self, r_width):
        self.elements = []
        self.width = r_width
        self.x_pos = []
        for p in range(self.width):
            self.elements.append(Sprite(model='square', visible=False, scale_y=0.25, scale_x=0.25))

    def set_pos(self, x, y):
        for u in range(len(self.elements)):
            self.elements[u].position = (x + u * .25, y)
            self.x_pos.append(x + u * .25)

    def is_complete(self):
        for r in range(len(self.elements)):
            if not self.elements[r].visible:
                return False
        return True

    def can_move(self, x_p):
        return not self.elements[self.x_pos.index(x_p)].visible

    def draw_a_fig(self, sprite):
        self.elements[self.x_pos.index(sprite.x)].visible = True
        self.elements[self.x_pos.index(sprite.x)].color = sprite.color
        self.elements[self.x_pos.index(sprite.x)].texture = sprite.texture


class Stack(object):
    def __init__(self, start_position, rows_amount, width_of_row):
        self.start_pos = start_position
        self.amount_rows = rows_amount
        self.rows_width = width_of_row
        self.rows = []
        self.y_pos = []

    def append_rows(self):
        for y in range(self.amount_rows):
            self.rows.append(Row(self.rows_width))
            self.rows[y].set_pos(self.start_pos[0], y/4 + self.start_pos[1])
            self.y_pos.append(y/4 + self.start_pos[1])

    def check_rows(self, d_sound, p_sound):
        rows_amount = 0
        is_deleted = False
        for o in range(self.amount_rows - 1, -1, -1):
            if self.rows[o].is_complete():
                self.move_row(o)
                is_deleted = True
                rows_amount += 1
        if is_deleted:
            p_sound.p_pause()
            d_sound.play_sound()
            p_sound.p_resume()
        return rows_amount

    def move_row(self, row_num):
        for r in range(row_num, len(self.rows) - 1):
            for u in range(len(self.rows[r].elements)):
                self.rows[r].elements[u].visible = self.rows[r + 1].elements[u].visible
                if self.rows[r].elements[u].visible:
                    self.rows[r].elements[u].color = self.rows[r + 1].elements[u].color
        self.rows[19] = Row(10)
        self.rows[19].set_pos(self.start_pos[0], 1)

    def can_move(self, sprite_position):
        return self.rows[self.y_pos.index(sprite_position[1] - .25)].can_move(sprite_position[0])

    def can_move_hor_l(self, sprite_position):
        return self.rows[self.y_pos.index(sprite_position[1])].can_move(sprite_position[0] - .25)

    def can_move_hor_r(self, sprite_position):
        return self.rows[self.y_pos.index(sprite_position[1])].can_move(sprite_position[0] + .25)

    def draw_in_a_row(self, elements):
        for o in range(len(elements[0])):
            self.rows[self.y_pos.index(elements[0][o].y)].draw_a_fig(elements[0][o])


class Figure(object):
    def __init__(self, p_angle, p_x, p_y, p_color, p_speed):
        self.angle = p_angle
        self.x_position = p_x
        self.y_position = p_y
        self.update_timestamp = datetime.datetime.now()
        self.rotate_timestamp = datetime.datetime.now()
        self.move_timestamp = datetime.datetime.now()
        self.elements = []
        self.high = 0
        self.row_num = 0
        self.color = p_color
        self.speed = p_speed
        for o in range(4):
            self.elements.append(Sprite(model='quad', color=self.color, texture='Cube'))
        self.calc()

    def update(self, levels, score, p_sound, d_sound):
        if datetime.datetime.now() - self.update_timestamp >= datetime.timedelta(milliseconds=self.speed):
            if self.can_move(levels):
                self.move()
            else:
                levels.draw_in_a_row([self.elements])
                score.set_score(levels.check_rows(d_sound, p_sound))
                generation()
            score.show_text()
            self.update_timestamp = datetime.datetime.now()

    def update_speed(self):
        if self.speed >= 100:
            self.speed -= 10
        return self.speed

    def movement(self, vec, border_left, border_right):
        if vec == "+":
            self.move_right(border_right)
        else:
            self.move_left(border_left)

    def move_right(self, border_right):
        pass

    def move_left(self, border_left):
        pass

    def can_move0(self, levels):
        pass

    def can_move90(self, levels):
        pass

    def can_move180(self, levels):
        pass

    def can_move270(self, levels):
        pass

    def can_move(self, levels):
        if self.angle == 0:
            return self.can_move0(levels)
        elif self.angle == 90:
            return self.can_move90(levels)
        elif self.angle == 180:
            return self.can_move180(levels)
        else:
            return self.can_move270(levels)

    def calc_0(self):
        pass

    def calc_90(self):
        pass

    def calc_180(self):
        pass

    def calc_270(self):
        pass

    def calc(self):
        if self.angle == 0:
            self.calc_0()
        elif self.angle == 90:
            self.calc_90()
        elif self.angle == 180:
            self.calc_180()
        else:
            self.calc_270()

    def move(self):
        self.y_position -= .25
        self.calc()

    def rotation(self):
        if datetime.datetime.now() - self.rotate_timestamp >= datetime.timedelta(milliseconds=500):
            self.angle += 90
            self.angle %= 360
            self.calc()
            self.rotate_timestamp = datetime.datetime.now()


class Cube(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.update_timestamp = datetime.datetime.now()
        self.rotate_timestamp = datetime.datetime.now()
        self.high = 2

    def can_move0(self, levels):
        return self.can_move_cube(levels)

    def can_move90(self, levels):
        return self.can_move_cube(levels)

    def can_move180(self, levels):
        return self.can_move_cube(levels)

    def can_move270(self, levels):
        return self.can_move_cube(levels)

    def can_move_cube(self, levels):
        if self.elements[3].y == -3.75:
            return False
        elif levels.can_move([self.elements[2].x, self.elements[2].y]):
            if levels.can_move([self.elements[3].x, self.elements[3].y]):
                return True
        return False

    def calc_0(self):
        self.calc_cube()

    def calc_90(self):
        self.calc_cube()

    def calc_180(self):
        self.calc_cube()

    def calc_270(self):
        self.calc_cube()

    def calc_cube(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position + .25, self.y_position)
        self.elements[2].position = (self.x_position, self.y_position - .25)
        self.elements[3].position = (self.x_position + .25, self.y_position - .25)

    def move_left(self, border_left):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.x_position >= border_left + .5:
                self.x_position -= .25
                self.calc_cube()

            self.move_timestamp = datetime.datetime.now()

    def move_right(self, border_right):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.x_position <= border_right - .75:
                self.x_position += .25
                self.calc_cube()
            self.move_timestamp = datetime.datetime.now()


class Stick(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.high = 1

    def can_move0(self, levels):
        return self.can_move_ver(levels)

    def can_move90(self, levels):
        return self.can_move_hor(levels)

    def can_move180(self, levels):
        return self.can_move_ver(levels)

    def can_move270(self, levels):
        return self.can_move_hor(levels)

    def can_move_ver(self, levels):
        if self.elements[3].y == -3.75:
            return False
        return levels.can_move([self.elements[3].x, self.elements[3].y])

    def can_move_hor(self, levels):
        if self.elements[3].y == -3.75:
            return False
        for t in range(len(self.elements)):
            if not levels.can_move([self.elements[t].x, self.elements[t].y]):
                return False
        return True

    def calc_0(self):
        self.calc_vertical()

    def calc_90(self):
        self.calc_horizontal()

    def calc_180(self):
        self.calc_vertical()

    def calc_270(self):
        self.calc_horizontal()

    def calc_vertical(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position, self.y_position - .25)
        self.elements[2].position = (self.x_position, self.y_position - .5)
        self.elements[3].position = (self.x_position, self.y_position - .75)
        self.high = 4

    def calc_horizontal(self):
        self.elements[0].position = (self.x_position - .5, self.y_position)
        self.elements[1].position = (self.x_position - .25, self.y_position)
        self.elements[2].position = (self.x_position, self.y_position)
        self.elements[3].position = (self.x_position + .25, self.y_position)
        self.high = 1

    def move_left(self, border_left):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[3].x >= border_left + .5:
                self.x_position -= .25
                self.calc()
        self.move_timestamp = datetime.datetime.now()

    def move_right(self, border_right):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[3].x <= border_right - .5:
                self.x_position += .25
                self.calc()
            self.move_timestamp = datetime.datetime.now()


class Angle(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.high = 1

    def can_move0(self, levels):
        if self.elements[3].y == -3.75:
            return False
        if not levels.can_move([self.elements[2].x, self.elements[2].y]):
            return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        return True

    def can_move90(self, levels):
        if self.elements[2].y == -3.75:
            return False
        for u in range(3):
            if not levels.can_move([self.elements[u].x, self.elements[u].y]):
                return False
        return True

    def can_move180(self, levels):
        if self.elements[0].y == -3.75:
            return False
        if not levels.can_move([self.elements[0].x, self.elements[0].y]):
            return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        return True

    def can_move270(self, levels):
        if self.elements[3].y == -3.75:
            return False
        for u in range(2):
            if not levels.can_move([self.elements[u].x, self.elements[u].y]):
                return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        return True

    def calc_0(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position, self.y_position - .25)
        self.elements[2].position = (self.x_position, self.y_position - .5)
        self.elements[3].position = (self.x_position + .25, self.y_position - .5)
        self.high = 3

    def calc_90(self):
        self.elements[0].position = (self.x_position - .5, self.y_position)
        self.elements[1].position = (self.x_position - .25, self.y_position)
        self.elements[2].position = (self.x_position, self.y_position)
        self.elements[3].position = (self.x_position, self.y_position + .25)
        self.high = 2

    def calc_180(self):
        self.elements[0].position = (self.x_position, self.y_position - 1)
        self.elements[1].position = (self.x_position, self.y_position - .5)
        self.elements[2].position = (self.x_position, self.y_position - .75)
        self.elements[3].position = (self.x_position - .25, self.y_position - .5)
        self.high = 3

    def calc_270(self):
        self.elements[0].position = (self.x_position + .5, self.y_position - .25)
        self.elements[1].position = (self.x_position + .25, self.y_position - .25)
        self.elements[2].position = (self.x_position, self.y_position - .25)
        self.elements[3].position = (self.x_position, self.y_position - .5)
        self.high = 2

    def move_left(self, border_left):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[0].x >= border_left + .5 and self.angle < 180:
                self.x_position -= .25
                self.calc()
            if self.elements[3].x >= border_left + .5 and self.angle >= 180:
                self.x_position -= .25
                self.calc()
        self.move_timestamp = datetime.datetime.now()

    def move_right(self, border_right):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[3].x <= border_right - .5 and self.angle < 180:
                self.x_position += .25
                self.calc()
            if self.elements[0].x <= border_right - .5 and self.angle >= 180:
                self.x_position += .25
                self.calc()
            self.move_timestamp = datetime.datetime.now()


class TFigure(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.high = 1
        self.update_timestamp = datetime.datetime.now()
        self.rotate_timestamp = datetime.datetime.now()

    def can_move0(self, levels):
        if self.elements[2].y == -3.75:
            return False
        for o in range(3):
            if not levels.can_move([self.elements[o].x, self.elements[o].y]):
                return False
        return True

    def can_move90(self, levels):
        if self.elements[2].y == -3.75:
            return False
        if not levels.can_move([self.elements[2].x, self.elements[2].y]):
            return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        return True

    def can_move180(self, levels):
        if self.elements[0].y == -3.75:
            return False
        if not levels.can_move([self.elements[0].x, self.elements[0].y]):
            return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        if not levels.can_move([self.elements[2].x, self.elements[2].y]):
            return False
        return True

    def can_move270(self, levels):
        if self.elements[2].y == -3.75:
            return False
        if not levels.can_move([self.elements[2].x, self.elements[2].y]):
            return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        return True

    def move_left(self, border_left):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[0].x >= border_left + .5 and self.angle == 0 or self.angle == 180:
                self.x_position -= .25
                self.calc()
            if self.elements[2].x >= border_left + .5 and self.angle == 90 or self.angle == 270:
                self.x_position -= .25
                self.calc()
        self.move_timestamp = datetime.datetime.now()

    def move_right(self, border_right):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[2].x <= border_right - .5 and self.angle == 0 or self.angle == 180:
                self.x_position += .25
                self.calc()
            if self.elements[3].x <= border_right - .5 and self.angle == 90 or self.angle == 270:
                self.x_position += .25
                self.calc()
            self.move_timestamp = datetime.datetime.now()

    def calc_0(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position + .25, self.y_position)
        self.elements[2].position = (self.x_position + .5, self.y_position)
        self.elements[3].position = (self.x_position + .25, self.y_position + .25)
        self.high = 2

    def calc_90(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position, self.y_position - .25)
        self.elements[2].position = (self.x_position, self.y_position - .5)
        self.elements[3].position = (self.x_position - .25, self.y_position - .25)
        self.high = 3

    def calc_180(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position + .25, self.y_position)
        self.elements[2].position = (self.x_position + .5, self.y_position)
        self.elements[3].position = (self.x_position + .25, self.y_position - .25)
        self.high = 2

    def calc_270(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position, self.y_position - .25)
        self.elements[2].position = (self.x_position, self.y_position - .5)
        self.elements[3].position = (self.x_position + .25, self.y_position - .25)
        self.high = 3


class Snake(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.high = 2

    def calc_0(self):
        self.calc_horizontal()

    def calc_90(self):
        self.calc_vertical()

    def calc_180(self):
        self.calc_horizontal()

    def calc_270(self):
        self.calc_vertical()

    def can_move0(self, levels):
        return self.can_move_horizontal(levels)

    def can_move90(self, levels):
        return self.can_move_vertical(levels)

    def can_move180(self, levels):
        return self.can_move_horizontal(levels)

    def can_move270(self, levels):
        return self.can_move_vertical(levels)

    def can_move_horizontal(self, levels):
        if self.elements[0].y == -3.75:
            return False
        if not levels.can_move([self.elements[0].x, self.elements[0].y]):
            return False
        if not levels.can_move([self.elements[1].x, self.elements[1].y]):
            return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        return True

    def can_move_vertical(self, levels):
        if self.elements[0].y == -3.75:
            return False
        if not levels.can_move([self.elements[1].x, self.elements[1].y]):
            return False
        if not levels.can_move([self.elements[3].x, self.elements[3].y]):
            return False
        return True

    def move_left(self, border_left):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[0].x >= border_left + .5 and self.angle == 0 or self.angle == 180:
                self.x_position -= .25
                self.calc()
            if self.elements[3].x >= border_left + .5 and self.angle == 90 or self.angle == 270:
                self.x_position -= .25
                self.calc()
        self.move_timestamp = datetime.datetime.now()

    def move_right(self, border_right):
        if datetime.datetime.now() - self.move_timestamp >= datetime.timedelta(milliseconds=250):
            if self.elements[3].x <= border_right - .5 and self.angle == 0 or self.angle == 180:
                self.x_position += .25
                self.calc()
            if self.elements[0].x <= border_right - .5 and self.angle == 90 or self.angle == 270:
                self.x_position += .25
                self.calc()
            self.move_timestamp = datetime.datetime.now()

    def calc_horizontal(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position + .25, self.y_position)
        self.elements[2].position = (self.x_position + .25, self.y_position + .25)
        self.elements[3].position = (self.x_position + .5, self.y_position + .25)
        self.high = 2

    def calc_vertical(self):
        self.elements[0].position = (self.x_position, self.y_position)
        self.elements[1].position = (self.x_position, self.y_position - .25)
        self.elements[2].position = (self.x_position + .25, self.y_position - .25)
        self.elements[3].position = (self.x_position + .25, self.y_position - .5)
        self.high = 3


counter = Counter()
stack = Stack([-.75, -3.75], 20, 10)
row = Row(10)
stack.append_rows()
border = Border(11, 19, [-1, -4])
border.building()
fig = Cube(0, 0, 0, color.yellow, 500)
sound = PAudio('06-2-player-mode-danger')
sound.play_sound()
del_sound = PAudio('07-stage-clear.mp3')
sound_timestamp = datetime.datetime.now()


def generation():
    temp = random.randint(0, 4)
    temp_x = (random.randint(-3, 5)/4) - .25
    global fig
    speed = fig.update_speed()
    print(fig.speed)
    for i in range(len(fig.elements)):
        fig.elements[i].disable()
    if temp == 0:
        fig = Cube(0, temp_x, .5, color.yellow, speed)
    elif temp == 1:
        fig = Stick(0, temp_x, .5, color.red, speed)
    elif temp == 2:
        fig = Angle(0, temp_x, .5, color.green, speed)
    elif temp == 3:
        fig = TFigure(0, temp_x, .5, color.magenta, speed)
    elif temp == 4:
        fig = Snake(0, temp_x, .5, color.brown, speed)


def keyboard_input(bord_left, bord_right):
    if held_keys['w']:
        fig.rotation()
    if held_keys['a']:
        fig.movement('-', bord_left, bord_right)
    if held_keys['d']:
        fig.movement('+', bord_left, bord_right)


def update():
    if datetime.datetime.now() - sound_timestamp == datetime.timedelta(minutes=3):
        sound.play_sound()
    fig.update(stack, counter, sound, del_sound)
    keyboard_input(border.border_elements[0][0].x, border.border_elements[1][0].x)


app.run()
