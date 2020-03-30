#-*- coding:utf-8 -*-
#导入需要的包
import curses #curses库提供了控制字符屏幕的独立于终端的方法
from random import randrange,choice
from collections import defaultdict

#定义用户行为
letter_codes=[ord(ch)for ch in 'WASDRQwasdrq']
actions=['Up','Left','Down','Right','Restart','Exit']
actions_dict=dict(zip(letter_codes,actions*2))

#阻塞+循环，直到获得用户有效输入才返回对应行为
def get_user_action(keyboard):
    char='N'
    while char not in actions_dict:
        char=keyboard.getch()
    return  actions_dict[char]
#矩阵转置
def transpose(field):
    return [list(row) for row in zip(*field)]
#矩阵的每一行倒序
def invert(field):
    return [row[::-1]for row in field]
#创建棋盘
class Gamefiled(object):
    def __init__(self,height=4,width=4,win=2048):
        self.height = height
        self.width = width
        self.win_value = 2048
        self.score = 0
        self.highscore = 0
        self.reset()
    #重置棋盘
    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field=[[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()#随机对两个空位赋值
    #棋盘走一步
    def move(self,direction):
    #一行向左合并
        def move_row_left(row):
            def tighten(row):
                # 将非零元素拿出来加到新列表
                # 给新列表后面补零
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):
                # 对邻近元素合并
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        # 判断邻近元素能否合并
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
            return tighten(merge(tighten(row)))
        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))
        # 判断棋盘操作是否存在且可行
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False
    def is_win(self):
        return any(any(i>=self.win_value for i in row)for row in self.field)
    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)
    #绘制界面
    def draw(self,screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '      (R)Restart (Q)Exit'
        gameover_string = " GAME  OVER"
        win_string = '     YOU WIN'

        def cast(string):
            #addstr()方法将传入的内容展示到终端
            try:
                screen.addstr(string + '\n')
            except:
                pass
        #绘制水平分割线
        def draw_hor_separator():
            line = '+'+('+------'*self.width + '+')[1:]
            cast(line)
        #绘制竖直分割线
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')
        #清空屏幕
        screen.clear()
        #绘制分数和最高分
        cast('SCORE:'+str(self.score))
        if 0 !=self.highscore:
            cast('HIGHSCORE:'+str(self.highscore))

        #绘制行列边框分割线
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        #绘制提示文字
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)
    #随机生成一个2或4
    def spawn(self):
        new_element=4 if randrange(100)>89 else 2
        (i,j)=choice([(i,j)for i in range(self.width)for j in range(self.height) if self.field[i][j]==0])
        self.field[i][j]=new_element
    #判断是否能移动
    def move_is_possible(self,direction):
        #判断一行里面是否能有元素进行左移动或合并
        def row_is_left_moveable(row):
            def change(i):
                if row[i]==0 and row[i+1]!=0:
                    return True
                if row[i]!=0 and row[i+1]==row[i]:
                    return True
                return False
            return any(change(i)for i in range(len(row)-1))
        check={}
        check['Left']=lambda field:any(row_is_left_moveable(row)for row in field)
        check['Right']=lambda field:check['Left'](invert(field))
        check['Up']=lambda field:check['Left'](transpose(field))
        check["Down"]=lambda  field:check["Right"](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False
def main(stdscr):
    def init():
        game_field.reset()
        return 'Game'
    def not_game(state):
        #画出游戏界面
        game_field.draw(stdscr)
        #读取用户输入
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]
    def game():
        game_field.draw(stdscr)
        action=get_user_action(stdscr)
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'
    state_actions={'Init':init,'Win':lambda :not_game('Win'),'Gameover':lambda :not_game('Gameover'),'Game':game}
    #使用游戏配置默认值
    curses.use_default_colors()
    #实例化游戏界面对象并设置游戏获胜条件为2048
    game_field=Gamefiled(win=64)
    state='Init'
    #状态机开始循环
    while state !='Exit':
        state = state_actions[state]()
curses.wrapper(main)
