import pygame
from figure import FigureQueue, Direction
from shape import Shape, DifficultShape
from random import choice, randint
from copy import deepcopy
from termcolor import colored
from util import *
from item import Item

# Screen Configs
W, H = 10, 20 # count of tiles
TILE = 45     # pixels for width and height for each tile
MARGIN = 20
GAME_W, GAME_H = W * TILE, H * TILE # screen pixel size
GAME_RES = GAME_W, GAME_H
BOARD_RES = GAME_W * 3 // 5, GAME_H
SCREEN_RES = GAME_W + BOARD_RES[0] + MARGIN * 3, GAME_H + MARGIN * 2
FPS = 60      # frame per sec

# Game Configs
FALLING_SPEED_INITIAL = 10
FALLING_SPEED_INCREASE = 1
FALLING_SPEED_ACCELERATED = 500 # when key down
FALLING_TRIGGER = 1000          # falling_count reaches this, fall one unit
DEFAULT_ITEM_PRESENCE_RATIO = 0.2               # item presence in every n figures

# Grid borders
GRID = [
  pygame.Rect(x * TILE, y * TILE, TILE, TILE)
  for y in range(H)
  for x in range(W)
]

def figure_rect(x = 0, y = 0):
  return pygame.Rect(x * TILE + 1, y * TILE + 1, TILE - 2, TILE - 2)

################################### Game start

pygame.init()
pygame.display.set_caption("Tetris, YusungKim")
pygame.display.set_icon(pygame.image.load('assets/images/meteor.png'))
screen = pygame.display.set_mode(SCREEN_RES)
game_screen = pygame.Surface(GAME_RES)
bg_screen = pygame.image.load('assets/images/bg_screen.png').convert()
bg_game = pygame.image.load('assets/images/bg_game.jpg').convert()
main_font = pygame.font.Font('assets/font.ttf', 65)
font = pygame.font.Font('assets/font.ttf', 45)
text_title = main_font.render('TETRIS', True, pygame.Color('darkorange'))
text_score = font.render(' Score:', True, pygame.Color('green'))
text_record = font.render('Record:', True, pygame.Color('purple'))
sound_completed = pygame.mixer.Sound('assets/sounds/Interference_06_SP.wav')
sound_falled = pygame.mixer.Sound('assets/sounds/WhipFoley_02_644.wav')
sound_multiple = pygame.mixer.Sound('assets/sounds/PlasticSheetWhipFoley_02_609.wav')
sound_combo = pygame.mixer.Sound('assets/sounds/25_MediumSnare_SP_356_99.wav')
sound_gameover = pygame.mixer.Sound('assets/sounds/HeavyWhooshes_39_342.wav')
bgms = [pygame.mixer.Sound(filepath) for filepath in filenames('assets/music/*.wav')]
clock = pygame.time.Clock()

effects = []

scores = {
  "previously_completed_lines": 0,   # storage for remember previous completion
  "combo": 0,   # continously completed
  "score": 0,   # total score
  "total_lines": 0  # total completed lines
}

# convert svg to png
try:
  svg_icons = [path[:-4] for path in filenames('assets/icons/*.svg')]
  png_icons = [path[:-4] for path in filenames('assets/icons/*.png')]
  [svg2png(path) for path in svg_icons if path not in png_icons]
except:
  print("Effor: cannot convert svg2png")

def enque_for_drawing_completion_effect(height):
  global effects

  r = randint(30, 200)
  for x in range(W):
    target_tile_rect = GRID[height * W + x]
    target_tile_rect.x += 1
    target_tile_rect.y += 1
    target_tile_rect.size = (target_tile_rect.width - 2, target_tile_rect.height - 2)
    g = int((H - height) / H * 200)
    b = int((W - x) / H * 200)
    effects.append([(r, g, b), target_tile_rect])

def draw_item(item, rect, screen):
  screen.blit(item.image(), rect)

def draw_field(field):
  for x, column in enumerate(field):
    for y, tile in enumerate(column):
      if tile:
        rect = figure_rect(x, y)
        color, item = tile
        pygame.draw.rect(game_screen, color, rect)
        if item:
          draw_item(item, rect, game_screen)


def draw_figure(figure):
  for idx, tile in enumerate(figure.tiles):
    # rect
    rect = figure_rect(tile.x, tile.y)
    pygame.draw.rect(game_screen, figure.color, rect)
    # # mark center tile
    # if figure.name != 'Square' and (idx == 0):
    #   pygame.draw.circle(game_screen, pygame.Color('orange'), rect.center, radius=rect.width // 6)
    # item
    if figure.item and (idx == 0):
      draw_item(figure.item, rect, game_screen)

def deal_with_items(items: list[Item]):
  global scores
  for item in items:
    if item == Item.DOLLAR:
      scores["score"] += 100
      print("ITEM: Money")
    elif item == Item.BOLT:
      print("ITEM: Thunder bolt, Add Difficult Figure")
      figures.add(1, DifficultShape.random())
    elif item == Item.STAR:
      print("ITEM: star, add three bar figure")
      figures.add(3, Shape.BAR)
    elif item == Item.EYE:
      print("ITEM: eye, show next of next figure")
    else:
      print(item)
  pass

# initialize new game
falling_speed = FALLING_SPEED_INITIAL
falling_count, fast_falling = 0, False
# Create figure at the position of (center x, 2nd line from the top)
figures = FigureQueue(DEFAULT_ITEM_PRESENCE_RATIO, initial_pos=(W // 2, 1))
field = [[False for i in range(H)] for j in range(W)]
previous_field = deepcopy(field)
record = get_record()

# Background music
bgm = choice(bgms)
bgm.set_volume(0.5)
pygame.mixer.Sound.play(bgm, loops=-1)

while True:
  dx, dy = 0, 1
  screen.blit(bg_screen, (0, 0))
  screen.blit(game_screen, (BOARD_RES[0] + MARGIN * 2, MARGIN))
  game_screen.blit(bg_game, (0, 0))

  ################ Control
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      exit()
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_LEFT:
        dx = -1
      elif event.key == pygame.K_RIGHT:
        dx = 1
      elif event.key == pygame.K_DOWN:
        fast_falling = True
      elif event.key == pygame.K_UP:
        # rotate 90 degrees (clock wise)
        figures.current_figure.rotate(field)

    if event.type == pygame.KEYUP:
      fast_falling = False

    # move x
    figures.current_figure.move(Direction.X, dx, field)

  # move y
  falling_count +=  FALLING_SPEED_ACCELERATED if fast_falling else falling_speed
  if falling_count > FALLING_TRIGGER:
    falling_count = 0
    figures.current_figure.move(Direction.Y, dy, field)
  
  # hit the ground
  if figures.current_figure.fallen:
    previous_field = deepcopy(field)
    scores["score"] +=1
    pygame.mixer.Sound.play(sound_falled)
    # update field
    for idx, tile in enumerate(figures.current_figure.tiles):
      field[tile.x][tile.y] = (figures.current_figure.color, figures.current_figure.item if idx == 0 else None)
    # create new figure and reset
    figures.next()
    if not scores["previously_completed_lines"]:
      scores["combo"] = 0
    scores["previously_completed_lines"] = 0

  # check completed lines
  # if completed, rewrite that line with above line
  completed = 0
  rewrite_y = H - 1
  for source_y in range(H - 1, -1, -1):
    filled_count = 0
    items = []
    for x in range(W):
      tile_filled = field[x][source_y]
      if tile_filled:
        filled_count += 1
        _, item = tile_filled
        if item:
          items.append(item)
      field[x][rewrite_y] = tile_filled
      
    if filled_count == W:
      completed += 1
      falling_speed = min(falling_speed + FALLING_SPEED_INCREASE, FALLING_SPEED_ACCELERATED)
      # draw completion effect
      enque_for_drawing_completion_effect(source_y)
      deal_with_items(items)
    else:
      rewrite_y -= 1

  # score
  if completed > 0:
    pygame.mixer.Sound.play(sound_completed)

    combo_msg, completed_msg, multi_msg = '', '', ''
    combo_bonus, completed_bonus, multi_bonus = 0, 0, 0

    # combo bonus
    combo = scores["combo"] + 1
    if combo > 1:
      pygame.mixer.Sound.play(sound_combo)
      combo_bonus = combo * 10
      combo_msg = f" +{combo_bonus} Pts ({combo} Combo!)"

    # complete bonus
    completed_bonus = completed * 2
    completed_msg = f" +{completed_bonus} Pts"

    # multiple complete bonus
    if completed > 1:
      pygame.mixer.Sound.play(sound_multiple)
      multi_bonus = randint(1, completed) * randint(completed, 5) * completed
      multi_msg = f" +{multi_bonus} Pts ({completed} Multi!)"
      
    score = scores["score"] + completed_bonus + multi_bonus + combo_bonus

    print(
      colored(f"SCORE: {str(score).ljust(5, ' ')}", 'red') \
      + colored(completed_msg, 'yellow') \
      + colored(multi_msg, 'magenta') \
      + colored(combo_msg, 'green')
    )

    # delay for completed lines
    for i in range(completed):
      pygame.time.wait(200)

    # update
    scores["combo"] = combo
    scores["previously_completed_lines"] = completed
    scores["score"] = score
    scores["total_lines"] += completed

    # update title
    pygame.display.set_caption(f"Tetris, YusungKim   {score} Points")

  ########################################## Draw

  ######################## GAME SCREEN
  # draw grid
  [pygame.draw.rect(game_screen, pygame.Color(40, 40, 40), i_rect, 1) for i_rect in GRID]

  # draw field(fallen figures) and figure
  if len(effects) > 0:
    draw_field(previous_field)
    draw_figure(figures.previous_figure)

    # draw effects
    effect = effects.pop(0)
    pygame.draw.rect(game_screen, effect[0], effect[1])
    screen.blit(game_screen, (BOARD_RES[0] + MARGIN * 2, MARGIN))
    pygame.display.flip()
    clock.tick(1000)

  else:
    draw_field(field)
    draw_figure(figures.current_figure)
  
  ######################## BOARD SCREEN
  screen.blit(text_title, (MARGIN + 10, MARGIN + 10))
  screen.blit(text_record, (MARGIN + 40, BOARD_RES[1] - MARGIN - 270))
  screen.blit(font.render(str(record).rjust(6, ' '), True, pygame.Color('yellow')), (MARGIN + 40, BOARD_RES[1] - MARGIN - 200))
  screen.blit(text_score, (MARGIN + 30, BOARD_RES[1] - MARGIN -100))
  screen.blit(font.render(str(scores["score"]).rjust(6, ' '), True, pygame.Color('white')), (MARGIN + 40, BOARD_RES[1] - MARGIN - 30))
  
  # draw next figure
  next_figure = figures.next_figure
  for idx, tile in enumerate(next_figure.tiles):
    # rect
    rect = figure_rect(tile.x, tile.y)
    rect.x += BOARD_RES[0] // 2 + MARGIN - W * TILE // 2
    rect.y += BOARD_RES[1] // 6 + MARGIN
    pygame.draw.rect(screen, next_figure.color, rect)
    if next_figure.item and (idx == 0):
      draw_item(next_figure.item, rect, screen)

  # game over
  for x in range(W):
    if field[x][0]:
      pygame.mixer.Sound.play(sound_gameover)
      set_record(record, scores["score"])
      # initialize new game
      falling_speed = FALLING_SPEED_INITIAL
      falling_count, fast_falling = 0, False
      figures = FigureQueue(DEFAULT_ITEM_PRESENCE_RATIO, initial_pos=(W // 2, 1))
      field = [[False for i in range(H)] for j in range(W)]
      scores = {
        "previously_completed_lines": 0,   # storage for remember previous completion
        "combo": 0,   # continously completed
        "score": 0,   # total score
        "total_lines": 0  # total completed lines
      }
      record = get_record()
      for rect in GRID:
        pygame.draw.rect(game_screen, (randint(30, 255), randint(30, 255), randint(30, 255)), rect)
        screen.blit(game_screen, (BOARD_RES[0] + MARGIN * 2, MARGIN))
        pygame.display.flip()
        clock.tick(100)
      pygame.mixer.pause()
      bgm = choice(bgms)
      bgm.set_volume(0.5)
      pygame.mixer.Sound.play(bgm, loops=-1)
      break

  pygame.display.update() # display Surface全体を更新して画面に描写します
  clock.tick(FPS)