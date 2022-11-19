import pygame
from enum import Enum
from copy import deepcopy
import math
import numpy as np
from termcolor import colored, cprint

Direction = Enum('Direction', ['X', 'Y'])

# All tetris figure shape, defined by positions of 4 tiles
FIGURE_SHAPES = [
  ('Bar', 'green', [(-1, 0), (-2, 0), (0, 0), (1, 0)]),
  ('Square', 'red', [(0, -1), (-1, -1), (-1, 0), (0, 0)]),
  ('Z_Mirr', 'blue', [(-1, 0), (-1, 1), (0, 0), (0, -1)]),
  ('Z', 'yellow', [(0, 0), (-1, 0), (0, 1), (-1, -1)]),
  ('L_Mirr', 'grey', [(0, 0), (0, -1), (0, 1), (-1, -1)]),
  ('L', 'magenta', [(0, 0), (0, -1), (0, 1), (1, -1)]),
  ('T', 'cyan', [(0, 0), (0, -1), (0, 1), (-1, 0)])
]

CLOCK_WISE_90 = -math.pi / 2.0
ROTATION_MATRIX = np.array([
  [math.cos(CLOCK_WISE_90), -math.sin(CLOCK_WISE_90)],
  [math.sin(CLOCK_WISE_90), math.cos(CLOCK_WISE_90)]
])

class Figure:

  @classmethod
  def all_shapes(cls, initial_pos=(0, 0)):
    return [Figure(definition, initial_pos) for definition in FIGURE_SHAPES]
  
  def __init__(self, definition: tuple[str, str, list[tuple[int, int]]], initial_pos=(0, 0)):
    """Figure
    Generate Normalized Figure with initial position, the center of x and top of y.

    Args:
        definition: (name, color, positions)
          positions: (array of positions): upper left postions of tiles, length should be 4
        field_width_and_height (tuple[int, int]): right edge of border and bottom edge of border (width and height of field)
    """
    self.name, self.color_name, positions = definition
    
    if len(positions) != 4:
      raise ValueError("Number of positions should be 4")

    self.fallen = False
    self.color = pygame.Color(self.color_name)
    self.tiles = [pygame.Rect(x + initial_pos[0], y + initial_pos[1], 1, 1) for x, y in positions]
  
  def move(self, direction: Direction, distance: int, field: list[list[int]]):
    old_tiles = deepcopy(self.tiles)
    
    # move x
    if direction == Direction.X:
      for tile in self.tiles:
        tile.x += distance
      if self.__cannot_move(field):
        self.tiles = deepcopy(old_tiles)

    # move y
    elif direction == Direction.Y:
      for tile in self.tiles:
        tile.y += distance
      if self.__cannot_move(field):
        if self.__fallen(field):
          self.fallen = True
        self.tiles = deepcopy(old_tiles)

  def rotate(self, field):
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

    # 左にはみ出たら内側に戻す    
    x_coordinates = rotated[:, 0]
    while x_coordinates[x_coordinates < 0].size > 0:
      print("left out")
      rotated = rotated + [1, 0]
      # 内側に戻して、ぶつかったら回転自体をやめる
      if self.__cannot_move(field):
        return

    # 右にはみ出たら内側に戻す    
    border_right = len(field) - 1
    while x_coordinates[x_coordinates > border_right].size > 0:
      print("right out")
      rotated = rotated + [-1, 0]
      # 内側に戻して、ぶつかったら回転自体をやめる
      if self.__cannot_move(field):
        return

    # 回せない場合はやめる
    if self.__cannot_move(field):
      return

    self.tiles = [pygame.Rect(x, y, 1, 1) for x, y in list(rotated)]

  def print(self, message='', end=' '):
    color_block = colored("■", self.color_name)
    cprint(color_block + f"[{self.name}]".ljust(10, ' ') + message, end=end)

  def __cannot_move(self, field):
    border_right = len(field) - 1
    border_bottom = len(field[0]) - 1
    outside_of_x = any([tile.x < 0 or tile.x > border_right for tile in self.tiles])
    outside_of_y = any([tile.y > border_bottom for tile in self.tiles])
    return outside_of_x or outside_of_y or self.__hit_other_figure(field)

  def __hit_other_figure(self, field):
    border_bottom = len(field[0]) - 1
    return any([field[tile.x][min(tile.y, border_bottom)] for tile in self.tiles])

  def __fallen(self, field):
    border_bottom = len(field[0]) - 1
    outside_of_y = any([tile.y > border_bottom for tile in self.tiles])
    return outside_of_y or self.__hit_other_figure(field)

  def __print_position(self, label: str, vectors):
    print(f"{label.rjust(10, ' ')}: {' '.join([','.join([str(e) for e in v]) for v in list(vectors)])}")