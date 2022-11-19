import pygame
import copy

W, H = 10, 20
TILE = 45
GAME_RES = W * TILE, H * TILE
FPS = 60

# All tetris figure shape, defined by positions of 4 tiles
FIGURE_SHAPES = [
  [(-1, 0), (-2, 0), (0, 0), (1, 0)],
  [(0, -1), (-1, -1), (-1, 0), (0, 0)],
  [(-1, 0), (-1, 1), (0, 0), (0, -1)],
  [(0, 0), (-1, 0), (0, 1), (-1, -1)],
  [(0, 0), (0, -1), (0, 1), (-1, -1)],
  [(0, 0), (0, -1), (0, 1), (1, -1)],
  [(0, 0), (0, -1), (0, 1), (-1, 0)]
]

# Grid borders
GRID = [
  pygame.Rect(x * TILE, y * TILE, TILE, TILE)
  for x in range(W)
  for y in range(H)
]

# Create figure at the position of (center x, 2nd line from the top)
figures = [
  [pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos]
  for fig_pos in FIGURE_SHAPES
]

# sample figure
figure = copy.deepcopy(figures[0])

def out_of_borders(figure):
  return any([tile.x < 0 or tile.x > W -1 for tile in figure])

def figure_rect(x = 0, y = 0):
  rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
  rect.x = x
  rect.y = y
  return rect

################################### Game start

pygame.init()
screen = pygame.display.set_mode(GAME_RES)
clock = pygame.time.Clock()

while True:
  dx = 0
  screen.fill(pygame.Color('black'))

  # Control
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      exit()
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_LEFT:
        dx = -1
      elif event.key == pygame.K_RIGHT:
        dx = 1

    # move x
    figure_old = copy.deepcopy(figure)
    for i in range(4):
      figure[i].x += dx
      if out_of_borders(figure):
        figure = copy.deepcopy(figure_old)
        break

    # draw grid
    [
      pygame.draw.rect(screen, (40, 40, 40), i_rect, 1)
      for i_rect in GRID
    ]

    # draw figure
    for i in range(4):
      x = figure[i].x * TILE
      y = figure[i].y * TILE
      pygame.draw.rect(screen, pygame.Color('white'), figure_rect(x, y))
  
    pygame.display.update() # display Surface全体を更新して画面に描写します
    pygame.display.set_caption("Tetris, FPS=" + str(round(clock.get_fps(), 3)))
    clock.tick(FPS)