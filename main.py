import pygame
from figure import *
from random import choice, randint
from copy import deepcopy
from termcolor import colored, cprint

# Screen Configs
W, H = 10, 20 # count of tiles
TILE = 45     # pixels for width and height for each tile
GAME_RES = W * TILE, H * TILE # screen pixel size
FPS = 60      # frame per sec

# Game Configs
FALLING_SPEED = 20
FALLING_SPEED_ACCELERATED = 400 # when key down
FALLING_TRIGGER = 1000          # falling_count reaches this, fall one unit

# Grid borders
GRID = [
  pygame.Rect(x * TILE, y * TILE, TILE, TILE)
  for x in range(W)
  for y in range(H)
]

# Create figure at the position of (center x, 2nd line from the top)
figures = Figure.all_shapes(initial_pos=(W // 2, 2))
field = [[False for i in range(H)] for j in range(W)]

def figure_rect(x = 0, y = 0):
  return pygame.Rect(x * TILE, y * TILE, TILE - 2, TILE - 2)

################################### Game start

pygame.init()
pygame.display.set_caption("Tetris, YusungKim")
pygame.display.set_icon(pygame.image.load('images/meteor.png'))
screen = pygame.display.set_mode(GAME_RES)
clock = pygame.time.Clock()  

scores = {
  "completed": 0,   # clear one or more line for each figure
  "combo": 0,   # continously completed
  "score": 0,   # total score
}

def new_figure():
  # reset
  if scores["completed"] == 0:
    scores["combo"] = 0
  scores["completed"] = 0

  # create new figure
  figure = deepcopy(choice(figures))
  figure.print()
  return figure

falling_count, fast_falling = 0, False
figure = new_figure()
while True:
  dx, dy = 0, 1
  screen.fill(pygame.Color('black'))

  ################ Control
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      exit()
    if event.type == pygame.KEYDOWN:
      fast_falling = False
      if event.key == pygame.K_LEFT:
        print("L", end=" ")
        dx = -1
      elif event.key == pygame.K_RIGHT:
        print("R", end=" ")
        dx = 1
      elif event.key == pygame.K_DOWN:
        fast_falling = True
      elif event.key == pygame.K_UP:
        if fast_falling:
          fast_falling = False
        else:
          print("U", end=" ")
          # rotate 90 degrees
          figure.rotate(field)

    # move x
    figure.move(Direction.X, dx, field)

  # move y
  falling_count +=  FALLING_SPEED_ACCELERATED if fast_falling else FALLING_SPEED
  if falling_count > FALLING_TRIGGER:
    falling_count = 0
    figure.move(Direction.Y, dy, field)
  
  # hit the ground
  if figure.fallen:
    print(" Fell!")
    # update field
    for tile in figure.tiles:
      field[tile.x][tile.y] = figure.color
    # create new figure
    figure = new_figure()
    fast_falling = False

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
    else:
      rewrite_y -= 1

  # score
  if completed > 0:
    combo_msg, completed_msg, multi_msg = '', '', ''
    combo_bonus, completed_bonus, multi_bonus = 0, 0, 0

    # combo bonus
    combo = scores["combo"] + 1
    if combo > 1:
      combo_bonus = combo * 10
      combo_msg = f" +{combo_bonus} Pts ({combo} Combo!)"

    # complete bonus
    completed_bonus = completed * 2
    completed_msg = f" +{completed_bonus} Pts"

    # multiple complete bonus
    if completed > 1:
      multi_bonus = randint(1, completed) * randint(completed, 5) * completed
      multi_msg = f" +{multi_bonus} Pts ({completed} Multi!)"
      
    score = scores["score"] + completed_bonus + multi_bonus + combo_bonus

    print(
      colored(f"SCORE: {str(score).ljust(5, ' ')}", 'red') \
      + colored(completed_msg, 'yellow') \
      + colored(multi_msg, 'magenta') \
      + colored(combo_msg, 'green')
    )

    # update
    scores["combo"] = combo
    scores["completed"] = completed
    scores["score"] = score

    # update title
    pygame.display.set_caption(f"Tetris, YusungKim   {score} Points")

  ############# Draw

  # draw grid
  [
    pygame.draw.rect(screen, (40, 40, 40), i_rect, 1)
    for i_rect in GRID
  ]

  # draw figure
  for idx, tile in enumerate(figure.tiles):
    # rect
    rect = figure_rect(tile.x, tile.y)
    pygame.draw.rect(screen, figure.color, rect)
    # mark center tile
    if (idx == 0):
      font = pygame.font.SysFont(None, 50)
      lebel = font.render("O", True, (0, 0, 0))
      screen.blit(lebel, (rect.x + 9, rect.y + 9))

  # draw field
  for x, column in enumerate(field):
    for y, filled in enumerate(column):
      if filled:
        pygame.draw.rect(screen, filled, figure_rect(x, y))

  pygame.display.update() # display Surface全体を更新して画面に描写します
  clock.tick(FPS)