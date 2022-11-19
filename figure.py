import pygame
from enum import Enum
import copy
import random
import math
import numpy as np

Direction = Enum('Direction', ['X', 'Y'])

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

CLOCK_WISE_90 = -math.pi / 2.0
ROTATION_MATRIX = np.array([
  [math.cos(CLOCK_WISE_90), -math.sin(CLOCK_WISE_90)],
  [math.sin(CLOCK_WISE_90), math.cos(CLOCK_WISE_90)]
])

class Figure:

  @classmethod
  def all(cls, border):
    return [Figure(shape, border) for shape in FIGURE_SHAPES]

  @classmethod
  def random(cls, border):
    return Figure(FIGURE_SHAPES[random.randrange(len(FIGURE_SHAPES))], border)
  
  def __init__(self, positions, border: tuple[int, int], color: pygame.Color = pygame.Color('white')):
    """Figure
    Generate Normalized Figure with initial position, the center of x and top of y.

    Args:
        positions (array of positions): upper left postions of tiles, length should be 4
        border (tuple[int, int]): left and right edge of border
    """    
    if len(positions) != 4:
      raise ValueError("Number of positions should be 4")

    self.color = color
    self.border_left, self.border_right = border
    self.tiles = [
      pygame.Rect(
        x + self.border_right // 2, # x
        y + 2,                      # y
        1,                          # width
        1                           # height
      )
      for x, y in positions
    ]
  
  def move(self, direction: Direction, distance: int):
    old_tiles = copy.deepcopy(self.tiles)
    
    # move x
    if direction == Direction.X:
      for tile in self.tiles:
        tile.x += distance
        # cancel if it moves to out side of border
        if self.__out_of_border():
          self.tiles = copy.deepcopy(old_tiles)

    # move y
    elif direction == Direction.Y:
      for tile in self.tiles:
        tile.y += distance
        # cancel if it moves to out side of border
        if self.__out_of_border():
          self.tiles = copy.deepcopy(old_tiles)

  def rotate(self):
    # prepare np.array vectors for calculation
    vectors = np.array([[tile.x, tile.y] for tile in self.tiles])

    # skip if the figure shape is square
    height_and_width_diff = np.sum(np.max(vectors, axis=0) - np.min(vectors, axis=0) + 1)
    if height_and_width_diff == 4:
      print("rotation make no difference")
      return

    # center tile
    index_of_center_tile = 0
    center = vectors[index_of_center_tile]

    # rotate
    rotated = np.round((vectors - center) @ ROTATION_MATRIX, decimals=0) + center

    # if it crosses border then move to inside.
    while rotated[rotated < self.border_left].size > 0:
      rotated = rotated + [1, 0]
    while rotated[rotated >= self.border_right].size > 0:
      rotated = rotated + [-1, 0]

    self.tiles = [pygame.Rect(x, y, 1, 1) for x, y in list(rotated)]

  def __out_of_border(self):
    return any([tile.x < self.border_left or tile.x > self.border_right -1 for tile in self.tiles])

  def __print_position(self, label: str, vectors):
    print(label.rjust(10, ' ') + ': ' + ' '.join([','.join([str(e) for e in v]) for v in list(vectors)]))