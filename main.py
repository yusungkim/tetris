import pygame
from figure import *

# Screen Configs
W, H = 10, 20 # count of tiles
TILE = 45     # pixels for width and height for each tile
GAME_RES = W * TILE, H * TILE # screen pixel size
FPS = 60      # frame per sec

# Game Configs
FALLING_SPEED = 30
FALLING_SPEED_ACCELERATED = FALLING_SPEED * 7 # when key down
FALLING_TRIGGER = 1000                        # falling_count reaches this, fall one unit

# Grid borders
GRID = [
  pygame.Rect(x * TILE, y * TILE, TILE, TILE)
  for x in range(W)
  for y in range(H)
]

# Create figure at the position of (center x, 2nd line from the top)
figures = Figure.all((0, W))

# sample figure
figure = Figure.random((0, W))

def figure_rect(x = 0, y = 0):
  rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
  rect.x = x
  rect.y = y
  return rect

################################### Game start

pygame.init()
screen = pygame.display.set_mode(GAME_RES)
clock = pygame.time.Clock()

falling_count, fast_falling = 0, False
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
        dx = -1
      elif event.key == pygame.K_RIGHT:
        dx = 1
      elif event.key == pygame.K_DOWN:
        fast_falling = True
      elif event.key == pygame.K_UP:
        figure.rotate()

    # move x
    figure.move(Direction.X, dx)

  # move y
  falling_count +=  FALLING_SPEED_ACCELERATED if fast_falling else FALLING_SPEED
  if falling_count > FALLING_TRIGGER:
    falling_count = 0
    figure.move(Direction.Y, dy)

  # draw grid
  [
    pygame.draw.rect(screen, (40, 40, 40), i_rect, 1)
    for i_rect in GRID
  ]

  # draw figure
  for tile in figure.tiles:
    x, y = tile.x * TILE, tile.y * TILE
    pygame.draw.rect(screen, pygame.Color('white'), figure_rect(x, y))

  pygame.display.update() # display Surface全体を更新して画面に描写します
  pygame.display.set_caption("Tetris, FPS=" + str(round(clock.get_fps(), 3)))
  clock.tick(FPS)