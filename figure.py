import pygame
from enum import Enum
import copy
import random

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

class Figure:

  @classmethod
  def all(cls, border):
    return [Figure(shape, border) for shape in FIGURE_SHAPES]

  @classmethod
  def random(cls, border):
    return Figure(FIGURE_SHAPES[random.randrange(len(FIGURE_SHAPES))], border)
  
  def __init__(self, tiles, border: tuple[int, int]):
    """Figure
    Generate Normalized Figure within border (x) space

    Args:
        tiles (array of positions): tiles, length of 4 with positions of tuple
        border (tuple[int, int]): left and right edge of border
    """    
    if len(tiles) <= 2:
      raise ValueError("Number of tiles should be greater then 2")

    self.border_left, self.border_right = border
    self.tiles = [
      pygame.Rect(
        x + self.border_right // 2, # x
        y + 1,                      # y
        1,                          # width
        1                           # height
      )
      for x, y in tiles
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
    old_tiles = copy.deepcopy(self.tiles)
    position_of_center_tile = len(self.self.tiles) // 2
    center = self.tiles[position_of_center_tile]

  def __out_of_border(self):
    return any([tile.x < self.border_left or tile.x > self.border_right -1 for tile in self.tiles])
