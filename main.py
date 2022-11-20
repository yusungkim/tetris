import pygame
from figure import *
from random import choice, randint
from copy import deepcopy
from termcolor import colored
from util import *

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
FALLING_SPEED_INCREASE = 2
FALLING_SPEED_ACCELERATED = 500 # when key down
FALLING_TRIGGER = 1000          # falling_count reaches this, fall one unit

# Grid borders
GRID = [
  pygame.Rect(x * TILE, y * TILE, TILE, TILE)
  for x in range(W)
  for y in range(H)
]

# Create figure at the position of (center x, 2nd line from the top)
FIGURES = Figure.all_shapes(initial_pos=(W // 2, 1))

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

def new_figure():
  # create new figure
  figure = deepcopy(choice(FIGURES))
  figure.color.r = min(max(figure.color.r + randint(-100, 100), 0), 255)
  figure.color.g = min(max(figure.color.g + randint(-100, 100), 0), 255)
  figure.color.b = min(max(figure.color.b + randint(-100, 100), 0), 255)
  figure.print()
  return figure

# initialize new game
falling_speed = FALLING_SPEED_INITIAL
falling_count, fast_falling = 0, False
figure, next_figure = new_figure(), new_figure()
field = [[False for i in range(H)] for j in range(W)]
scores = {
  "previously_completed_lines": 0,   # storage for remember previous completion
  "combo": 0,   # continously completed
  "score": 0,   # total score
  "total_lines": 0  # total completed lines
}
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
        print("L", end=" ")
        dx = -1
      elif event.key == pygame.K_RIGHT:
        print("R", end=" ")
        dx = 1
      elif event.key == pygame.K_DOWN:
        fast_falling = True
      elif event.key == pygame.K_UP:
        print("U", end=" ")
        # rotate 90 degrees (clock wise)
        figure.rotate(field)

    if event.type == pygame.KEYUP:
      fast_falling = False

    # move x
    figure.move(Direction.X, dx, field)

  # move y
  falling_count +=  FALLING_SPEED_ACCELERATED if fast_falling else falling_speed
  if falling_count > FALLING_TRIGGER:
    falling_count = 0
    figure.move(Direction.Y, dy, field)
  
  # hit the ground
  if figure.fallen:
    print(" Fallen!")
    pygame.mixer.Sound.play(sound_falled)
    # update field
    for tile in figure.tiles:
      field[tile.x][tile.y] = figure.color
    # create new figure and reset
    figure = next_figure
    next_figure = new_figure()
    if not scores["previously_completed_lines"]:
      scores["combo"] = 0
    scores["previously_completed_lines"] = 0

  # check completed lines
  # if completed, rewrite that line with above line
  completed = 0
  rewrite_y = H - 1
  for source_y in range(H - 1, -1, -1):
    filled = 0
    for x in range(W):
      if field[x][source_y]:
        filled += 1
      field[x][rewrite_y] = field[x][source_y]
    if filled == W:
      completed += 1
      falling_speed = min(falling_speed + FALLING_SPEED_INCREASE, FALLING_SPEED_ACCELERATED)
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

  ############# Draw

  # draw grid
  [
    pygame.draw.rect(game_screen, pygame.Color(40, 40, 40), i_rect, 1)
    for i_rect in GRID
  ]

  # draw figure
  for idx, tile in enumerate(figure.tiles):
    # rect
    rect = figure_rect(tile.x, tile.y)
    pygame.draw.rect(game_screen, figure.color, rect)
    # mark center tile
    if figure.name != 'Square' and (idx == 0):
      pygame.draw.circle(game_screen, pygame.Color('orange'), rect.center, radius=rect.width // 6)

  # draw field
  for x, column in enumerate(field):
    for y, filled in enumerate(column):
      if filled:
        pygame.draw.rect(game_screen, filled, figure_rect(x, y))
  
  # draw board
  screen.blit(text_title, (MARGIN + 10, MARGIN + 10))
  screen.blit(text_record, (MARGIN + 40, BOARD_RES[1] - MARGIN - 270))
  screen.blit(font.render(str(record).rjust(6, ' '), True, pygame.Color('yellow')), (MARGIN + 40, BOARD_RES[1] - MARGIN - 200))
  screen.blit(text_score, (MARGIN + 30, BOARD_RES[1] - MARGIN -100))
  screen.blit(font.render(str(scores["score"]).rjust(6, ' '), True, pygame.Color('white')), (MARGIN + 40, BOARD_RES[1] - MARGIN - 30))
  
  # draw next figure
  for idx, tile in enumerate(next_figure.tiles):
    # rect
    rect = figure_rect(tile.x, tile.y)
    rect.x += BOARD_RES[0] // 2 + MARGIN - W * TILE // 2
    rect.y += BOARD_RES[1] // 6 + MARGIN
    pygame.draw.rect(screen, next_figure.color, rect)

  # game over
  for x in range(W):
    if field[x][0]:
      pygame.mixer.Sound.play(sound_gameover)
      set_record(record, scores["score"])
      # initialize new game
      falling_speed = FALLING_SPEED_INITIAL
      falling_count, fast_falling = 0, False
      figure, next_figure = new_figure(), new_figure()
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