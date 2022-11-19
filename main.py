import pygame
from figure import *
from random import choice
from copy import deepcopy

# Screen Configs
W, H = 10, 20 # count of tiles
TILE = 45     # pixels for width and height for each tile
GAME_RES = W * TILE, H * TILE # screen pixel size
FPS = 60      # frame per sec

# Game Configs
FALLING_SPEED = 20
FALLING_SPEED_ACCELERATED = 200 # when key down
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

def random_figure():
  figure = deepcopy(choice(figures))
  figure.print()
  return figure

def figure_rect(x = 0, y = 0):
  return pygame.Rect(x * TILE, y * TILE, TILE - 2, TILE - 2)

################################### Game start

pygame.init()
screen = pygame.display.set_mode(GAME_RES)
clock = pygame.time.Clock()

falling_count, fast_falling = 0, False
figure = random_figure()
while True:
  dx, dy = 0, 1
  screen.fill(pygame.Color('black'))

  # Control
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
        print("U", end=" ")
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
    figure = random_figure()
    fast_falling = False

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
  pygame.display.set_caption("Tetris, FPS=" + str(round(clock.get_fps(), 3)))
  clock.tick(FPS)