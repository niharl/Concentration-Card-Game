##################################################
# Memory Card Game                               #
# Nihar Lohan                                    #
# Images taken from:                             #
# http://acbl.mybigcommerce.com/52-playing-cards/#
##################################################
# Requirements:                                  #
# Python 3.8.2, Pygame 2.0.0.dev6                #
##################################################

import pygame
import random
import copy

# Graphics window dimensions
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 750
BACKGROUND_COLOR = (12,112,16)
CARD_OFFSET_X = 8
CARD_OFFSET_Y = 12
OFFSET_X = 25
OFFSET_Y = 25
DISPLAY_GAME_INFO_SPACE = 125
ARENA_X = SCREEN_WIDTH - 2 * OFFSET_X
ARENA_Y = SCREEN_HEIGHT - OFFSET_Y - DISPLAY_GAME_INFO_SPACE


# Pygame initialisation
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Game")
clock = pygame.time.Clock()
medium_font = pygame.font.SysFont("Comic Sans MS", 30)
major_info_font = pygame.font.SysFont("Comic Sans MS", 60)
major_font = pygame.font.SysFont("Comic Sans MS", 100)
instruction_font = pygame.font.SysFont("Comic Sans MS", 40)


# Red Back of Card Image
red_back = pygame.image.load('red_back.png').convert_alpha()
home_icon = pygame.transform.scale(pygame.image.load('House Icon.png').convert_alpha(), (50,50))
fanned_out = pygame.image.load('honor_diamond.png').convert_alpha()

# Storing information about levels:
# structure is: [number of columns of cards, time_limit,moves_limit]
levels = [[4,10,10], [6,45,20] , [8,90,50], [10,120,100]]
speeds = [2000,1000,750,500,250,100]
#both of these list can be updated on their own to alter number of levels/speeds available


#Generating the list of potential cards
suits = ['C','D','H','S']
ranks = [str(i) for i in range(2,11)] + ['A','J','Q','K']
deck = []
for suit in suits:
    for rank in ranks:
        card = rank + suit + '.png'
        deck.append(card)


class Game_Mode:
    def __init__(self,level_id,mode,speed):
        self.level_id = level_id
        self.mode = mode
        self.columns = levels[level_id][0]
        self.rows = self.columns // 2
        self.time_to_see =  speeds[speed]
        self.cards_required = (self.columns * self.rows) // 2
        self.states = [[0 for c in range(self.columns)] for r in range(self.rows)]
        self.generate_board()
        self.flipped_cards = []
        self.moves = 0
        if self.mode == 1:
            self.max_moves = levels[level_id][2]
        elif self.mode == 2:
            self.start_time = pygame.time.get_ticks()
            self.end_time = self.start_time + levels[level_id][1]*1000
    
    def generate_board(self):
        random.shuffle(deck)
        self.cards_used = deck[:self.cards_required]
        self.first_deck = copy.deepcopy(self.cards_used)
        self.second_deck = copy.deepcopy(self.cards_used)
        random.shuffle(self.second_deck)
        self.board = []
        for row in range(self.rows):
            row = []
            for column in range(self.columns//2):
                row.append(self.first_deck.pop())
                row.append(self.second_deck.pop())
            self.board.append(row)
    
    def draw_state(self,surface):
        surface.fill(BACKGROUND_COLOR)
        for row in range(self.rows):
            for column in range(self.columns):
                if self.states[row][column] == -1:
                    continue
                elif self.states[row][column] == 0:
                    current_surface.draw_red_back(surface,row,column)
                else:
                    card_name = self.board[row][column]
                    current_surface.draw_card(card_name,surface,row,column)

    def check_if_game_over(self,surface):
        if self.check_if_won():
            text = major_font.render("YOU WON!",1,(255,255,255))
            surface.blit(text,(295,350))
            return True
        else:
            if self.mode == 1:
                if self.moves == self.max_moves:
                    surface.fill(BACKGROUND_COLOR)
                    self.display_game_info(surface)
                    self.display_mode(surface)
                    text = major_font.render("OUT OF MOVES",1,(255,255,255))
                    surface.blit(text,(212,350))
                    current_surface.display_home_icon(surface)
                    return True
            elif self.mode == 2:
                if pygame.time.get_ticks() >= self.end_time:
                    surface.fill(BACKGROUND_COLOR)
                    self.end_time = pygame.time.get_ticks()
                    self.display_game_info(surface)
                    self.display_mode(surface)
                    text = major_font.render("OUT OF TIME",1,(255,255,255))
                    surface.blit(text,(252,350))
                    current_surface.display_home_icon(surface)
                    return True
        return False
    
    def check_if_won(self):
        if set([state for sublist in self.states for state in sublist]) == {-1}:
            return True

    def handle_mouse_press(self,event):
        position = pygame.mouse.get_pos()
        row,column = current_surface.convert_to_row_column(position[0],position[1])
        if row != -1 and column != -1:
            if self.states[row][column] == 1 or self.states[row][column] == -1:
                pass
            else:
                self.deal_with_flipping(row,column)
                
    def deal_with_flipping(self,row,column):
        self.already_flipped = len(self.flipped_cards)
        if self.already_flipped == 0:
            self.flipped_cards = [Flipped_card(row,column)]
            self.states[row][column] = 1
        elif self.already_flipped == 1:
            self.flipped_cards.append(Flipped_card(row,column))
            self.moves += 1
            self.deal_with_two_flipped()
        elif self.already_flipped == 2:
            self.do_delayed_moves()
            self.flipped_cards = [Flipped_card(row,column)]
            self.states[row][column] = 1

    def deal_with_two_flipped(self):
        if self.flipped_cards[0].type == self.flipped_cards[1].type:
            self.flipped_cards[0].next_state = -1
            self.flipped_cards[1].next_state = -1
        else:
            self.flipped_cards[0].next_state = 0
            self.flipped_cards[1].next_state = 0
        self.states[self.flipped_cards[1].row][self.flipped_cards[1].column] = 1

        self.end_viewing = self.time_to_see + pygame.time.get_ticks()

    def check_if_time(self):
        if len(self.flipped_cards) == 2:
            if pygame.time.get_ticks() >= self.end_viewing and len(self.flipped_cards) == 2:
                return True
            else:
                return False

    def do_delayed_moves(self):
        self.states[self.flipped_cards[0].row][self.flipped_cards[0].column] = self.flipped_cards[0].next_state
        self.states[self.flipped_cards[1].row][self.flipped_cards[1].column] = self.flipped_cards[1].next_state
        self.flipped_cards = []

    def display_game_info(self,surface):
        if self.mode == 1:    
            text = "Remaining Moves: " + str(self.max_moves-self.moves)
            text = medium_font.render(text,1,(255,255,255))
            surface.blit(text,(25,50))
        elif self.mode == 2:
            text = "Remaining Time: " + str((self.end_time-pygame.time.get_ticks())//1000) + " s"
            text = medium_font.render(text,1,(255,255,255))
            surface.blit(text,(25,50))

    def display_mode(self,surface):
        if self.mode == 0:
            text = "UNLIMITED MODE"
            text = major_info_font.render(text,1,(255,255,255))
            surface.blit(text,(290,40))
        elif self.mode == 1:
            text = "LIMITED MOVES MODE"
            text = major_info_font.render(text,1,(255,255,255))
            surface.blit(text,(250,40))
        elif self.mode == 2:
            text = "TIMED MODE"
            text = major_info_font.render(text,1,(255,255,255))
            surface.blit(text,(340,40))
        


class Flipped_card:
    def __init__(self,row,column):
        self.row = row
        self.column = column
        self.type = current_game.board[row][column]



class Playing_surface:
    def __init__(self,game,red_back):
        self.board_size_x = ARENA_X
        self.board_size_y = ARENA_Y
        self.pure_size_x = (ARENA_X//game.columns)
        self.pure_size_y = (ARENA_Y//game.rows)
        self.card_size_x = self.pure_size_x - CARD_OFFSET_X
        self.card_size_y = self.pure_size_y - CARD_OFFSET_Y
        self.offset_x = OFFSET_X
        self.offset_y = DISPLAY_GAME_INFO_SPACE
        self.red_back = pygame.transform.scale(red_back, (self.card_size_x, self.card_size_y))
    
    def convert_to_pixel_coordinates(self,row,column):
        x = column * self.pure_size_x + self.offset_x
        y = row * self.pure_size_y + self.offset_y
        return x,y

    def convert_to_row_column(self,x,y):
        x -= self.offset_x
        y -= self.offset_y
        if x < 0 or y < 0:
            return [-1,-1]
        remainder_x = x % self.pure_size_x
        remainder_y = y % self.pure_size_y
        if remainder_x > (self.card_size_x) or remainder_y > (self.card_size_y):
            return [-1,-1]
        column = x // self.pure_size_x
        row = y // self.pure_size_y
        if column >= current_game.columns or row >= current_game.rows:
            return [-1,-1]
        return [row,column]

    def draw_card(self,card_name,surface,row,column):
        x,y = self.convert_to_pixel_coordinates(row,column)
        card = pygame.image.load(card_name).convert_alpha()
        card = pygame.transform.scale(card, (self.card_size_x, self.card_size_y))
        surface.blit(card, [x,y])

    def draw_red_back(self,surface,row,column):
        x,y = self.convert_to_pixel_coordinates(row,column)
        surface.blit(self.red_back, [x,y])
    
    def display_home_icon(self,surface):
        surface.blit(home_icon, [850,30])
    
class Home_Screen:
    def __init__(self,levels,speeds):
        self.levels = levels
        self.speeds = speeds
        self.chosen_size = -1
        self.size_selected = False
        self.chosen_speed = -1
        self.speed_selected = False
        self.chosen_mode = -1
        self.mode_selected = False
        self.modes = ["Unlimited", "Limited Moves", "Timed"]
        self.start_game = False
    
    def display_title_text(self,surface):
        text = "MEMORY GAME"
        text = major_font.render(text,1,(255,255,255))
        surface.blit(text,(220,40))
    
    def display_fanned_out(self,surface):
        surface.blit(fanned_out,(225,100))
    
    def display_level_options(self,surface):
        instruction = instruction_font.render("Select level (i.e. board size):",1,(255,255,255))
        surface.blit(instruction,(30,420))
        length = len(self.levels)
        max_distance = (SCREEN_WIDTH - 500)
        offset = max_distance//length
        position = 410 + offset
        self.level_positions = []
        self.level_height_range = []
        for i in range(length):
            color = (255,255,255)
            if i == self.chosen_size:
                color = (255,0,0)
            num = instruction_font.render(str(i+1),1,(color))
            surface.blit(num,(position,420))
            width = num.get_width()
            height = num.get_height()
            self.level_positions.append([position,position+width])
            position += offset
        self.level_height_range = [420,420+height]

    def display_speed_options(self,surface):
        instruction = instruction_font.render("Select speed (i.e. time to see cards):",1,(255,255,255))
        surface.blit(instruction,(30,500))
        length = len(self.speeds)
        max_distance = (SCREEN_WIDTH - 520)
        offset = max_distance//length
        position = 470 + offset
        self.speed_positions = []
        for i in range(length):
            color = (255,255,255)
            if i == self.chosen_speed:
                color = (255,0,0)
            num = instruction_font.render(str(i+1),1,(color))
            surface.blit(num,(position,500))
            width = num.get_width()
            height = num.get_height()
            self.speed_positions.append([position,position+width])
            position += offset
        self.speed_height_range = [500,500+height]

    def display_mode_options(self,surface):
        instruction = instruction_font.render("Select mode:",1,(255,255,255))
        surface.blit(instruction,(30,580))
        positions = [300,500,750]
        self.mode_positions = []
        for i in range(3):
            position = positions[i]
            color = (255,255,255)
            if self.chosen_mode == i:
                color = (255,0,0)
            mode = instruction_font.render(self.modes[i],1,(color))
            width = mode.get_width()
            height = mode.get_height()
            self.mode_positions.append([position,position+width])
            surface.blit(mode,(position,580))
        self.mode_height_range = [580,580+height]

    def display_start_button(self,surface):
        start = major_font.render("START GAME",1,(255,255,255))
        surface.blit(start,(250,660))
        width = start.get_width()
        height = start.get_height()
        self.start_game_position = [250,250+width,660,660+height]

    def handle_mouse_press(self,event):
        x,y = pygame.mouse.get_pos()
        if self.level_height_range[0] <= y <= self.level_height_range[1]:
            for i in range(len(self.level_positions)):
                if self.level_positions[i][0] <= x <= self.level_positions[i][1]:
                    self.size_selected = True
                    self.chosen_size = i
                    break
        elif self.speed_height_range[0] <= y <= self.speed_height_range[1]:
            for i in range(len(self.speed_positions)):
                if self.speed_positions[i][0] <= x <= self.speed_positions[i][1]:
                    self.speed_selected = True
                    self.chosen_speed = i
                    break
        elif self.mode_height_range[0] <= y <= self.mode_height_range[1]:
            for i in range(3):
                if self.mode_positions[i][0] <= x <= self.mode_positions[i][1]:
                    self.mode_selected = True
                    self.chosen_mode = i
                    break
        elif self.start_game_position[0] <= x <= self.start_game_position[1] and self.start_game_position[2] <= y <= self.start_game_position[3]:
            if self.size_selected and self.speed_selected and self.mode_selected:
                self.start_game = True
    

    def display_whole_screen(self,surface):
        self.display_title_text(surface)
        self.display_fanned_out(surface)
        self.display_level_options(surface)
        self.display_speed_options(surface)
        self.display_mode_options(surface)
        self.display_start_button(surface)
        
def check_if_home_button_pressed(event):
    x,y = pygame.mouse.get_pos()        
    if 850 <= x <= 900 and 30 <= y <= 80:
        return True
    return False


currently_playing = False
homepage = Home_Screen(levels,speeds)
display_home = True

while True:
    clock.tick(40)
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not display_home:
                if check_if_home_button_pressed(event):
                    currently_playing = False
                    display_home = True
                    homepage = Home_Screen(levels,speeds)
                elif currently_playing:
                    current_game.handle_mouse_press(event)
            elif display_home:
                homepage.handle_mouse_press(event)
    
    if homepage.start_game:
        currently_playing = True
        current_game = Game_Mode(homepage.chosen_size,homepage.chosen_mode,homepage.chosen_speed)
        current_surface = Playing_surface(current_game,red_back)
        homepage.start_game = False
        display_home = False

    if not currently_playing and display_home:
        screen.fill(BACKGROUND_COLOR)
        homepage.display_whole_screen(screen)

    elif currently_playing:
        screen.fill(BACKGROUND_COLOR)
        if current_game.check_if_time():
            current_game.do_delayed_moves()

        current_game.draw_state(screen)
        
        current_game.display_game_info(screen)
        current_game.display_mode(screen)
        current_surface.display_home_icon(screen)

        if current_game.check_if_game_over(screen):
            currently_playing = False


    pygame.display.update()