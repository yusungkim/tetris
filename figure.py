import pygame
from random import choice, randint, random
from copy import deepcopy
import math
import numpy as np
from item import Item
from enum import Enum
from shape import *

Direction = Enum('Direction', ['X', 'Y'])

# All tetris figure shape, defined by positions of 4 tiles
FIGURE_SHAPES = [
  (Shape.BAR, 'red', [(-1, 0), (-2, 0), (0, 0), (1, 0)]),
  (Shape.SQUARE, 'blue', [(0, -1), (-1, -1), (-1, 0), (0, 0)]),
  (Shape.Z, 'green', [(-1, 0), (-1, 1), (0, 0), (0, -1)]),
  (Shape.S, 'yellow', [(0, 0), (-1, 0), (0, 1), (-1, -1)]),
  (Shape.L, 'orange', [(0, 0), (0, -1), (0, 1), (-1, -1)]),
  (Shape.L2, 'magenta', [(0, 0), (0, -1), (0, 1), (1, -1)]),
  (Shape.T, 'cyan', [(0, 0), (0, -1), (0, 1), (-1, 0)])
]

DIFFICULT_FIGURE_SHAPES = [
  # (DifficultShape.E, 'white', [(0, 0), (1, 0), (0, 2), (1, 2), (0, -2), (1, -2), (-1, 2), (-1, 1), (-1, 0), (-1, -1), (-1, -2)]),
  (DifficultShape.O, 'white', [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0), (2, -1), (1, -1), (0, -1)]),
  (DifficultShape.U, 'white', [(0, 0), (0, 1), (2, 1), (2, 0), (2, -1), (1, -1), (0, -1)])
]

ANTI_CLOCK_WISE_90 = +math.pi / 2.0
ROTATION_MATRIX = np.array([
  [math.cos(ANTI_CLOCK_WISE_90), -math.sin(ANTI_CLOCK_WISE_90)],
  [math.sin(ANTI_CLOCK_WISE_90), math.cos(ANTI_CLOCK_WISE_90)]
])

class Figure:
  
  def __init__(self, definition: tuple[Shape or DifficultShape, str, list[tuple[int, int]]], initial_pos=(0, 0), item: Item=None):
    """Figure
    Generate Normalized Figure with initial position, the center of x and top of y.

    Args:
        definition: (shape, color, positions)
          positions: (array of positions): upper left postions of tiles, length should be 4
        field_width_and_height (tuple[int, int]): right edge of border and bottom edge of border (width and height of field)
    """
    self.shape, base_color_name, positions = definition
    self.fallen = False
    
    # Initial Position
    if isinstance(self.shape, Shape):
      self.tiles = [pygame.Rect(x + initial_pos[0], y + initial_pos[1], 1, 1) for x, y in positions]
    elif isinstance(self.shape, DifficultShape):
      self.tiles = [pygame.Rect(x + initial_pos[0], y + initial_pos[1] + 1, 1, 1) for x, y in positions]

    # Color
    color = pygame.Color(base_color_name)
    color.r = min(max(color.r + randint(-100, 100), 0), 255)
    color.g = min(max(color.g + randint(-100, 100), 0), 255)
    color.b = min(max(color.b + randint(-100, 100), 0), 255)
    self.color = color
    
    # Item
    self.item = item
  
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

    # skip if the figure shape is SQUARE
    # height_and_width_diff = np.sum(np.max(vectors, axis=0) - np.min(vectors, axis=0) + 1)
    # if height_and_width_diff == 4:
    #   print("rotation make no difference")
    #   return
    if self.shape == Shape.SQUARE:
      if self.item:
        first_tile = self.tiles.pop(0)
        self.tiles.append(first_tile)
      return
    elif self.shape == DifficultShape.U or self.shape == DifficultShape.O:
      if self.item:
        first_tile = self.tiles.pop(0)
        self.tiles.append(first_tile)
        first_tile = self.tiles.pop(0)
        self.tiles.append(first_tile)
      return

    # center tile
    index_of_center_tile = 0
    center = vectors[index_of_center_tile]
    # rotate
    rotated = np.round((vectors - center) @ ROTATION_MATRIX, decimals=0) + center

    # 一旦回す
    old_tiles = deepcopy(self.tiles)
    self.tiles = [pygame.Rect(x, y, 1, 1) for x, y in list(rotated)]

    # 左にはみ出たら
    x_coordinates = rotated[:, 0]
    while x_coordinates[x_coordinates < 0].size > 0:
      # 内側に移動
      rotated = rotated + [1, 0]
      x_coordinates = rotated[:, 0]
      self.tiles = [pygame.Rect(x, y, 1, 1) for x, y in list(rotated)]
      # ぶつかったら回転自体をやめる
      if self.__hit_other_figure(field):
        self.tiles = old_tiles
        return

    # 右にはみ出たら
    border_right = len(field) - 1
    while x_coordinates[x_coordinates > border_right].size > 0:
      # 内側に移動
      rotated = rotated + [-1, 0]
      x_coordinates = rotated[:, 0]
      self.tiles = [pygame.Rect(x, y, 1, 1) for x, y in list(rotated)]
      # 内側に戻して、ぶつかったら回転自体をやめる
      if self.__hit_other_figure(field):
        self.tiles = old_tiles
        return

    # 回せない場合はやめる
    if self.__cannot_move(field):
      self.tiles = old_tiles
      return

  def __cannot_move(self, field):
    border_right = len(field) - 1
    border_bottom = len(field[0]) - 1
    outside_of_x = any([tile.x < 0 or tile.x > border_right for tile in self.tiles])
    outside_of_y = any([tile.y > border_bottom for tile in self.tiles])
    return outside_of_x or outside_of_y or self.__hit_other_figure(field)

  def __hit_other_figure(self, field):
    border_right = len(field) - 1
    border_bottom = len(field[0]) - 1
    return any([field[min(tile.x, border_right)][min(tile.y, border_bottom)] for tile in self.tiles])

  def __fallen(self, field):
    border_bottom = len(field[0]) - 1
    outside_of_y = any([tile.y > border_bottom for tile in self.tiles])
    return outside_of_y or self.__hit_other_figure(field)


class FigureQueue:
  def __init__(self, default_item_presence_ratio: float, initial_pos=(0, 1)):
    self.__default_item_presence_ratio = default_item_presence_ratio
    self.__initial_pos = initial_pos
    self.__queue:list[Figure] = []
    self.add(2)
    
    # figure
    self.previous_figure = None
    self.current_figure = self.__queue[0]
    self.next_figure = self.__queue[1]

  def next(self, num: int = 1):
    number_of_current_figures = len(self.__queue)
    self.previous_figure = None if number_of_current_figures == 0 else self.__queue.pop(0)
    self.add( max(2 - number_of_current_figures, num) )
    self.current_figure = self.__queue[0]
    self.next_figure = self.__queue[1]
    self.print()

  def size(self):
    return len(self.__queue)

  # create new figure and add to queue
  def add(self, num: int = 1, shape:Shape or DifficultShape = None):
    for _ in range(num):
      # shape
      definition = None
      if isinstance(shape, Shape):
        definition = list(filter(lambda s: s[0] == shape, FIGURE_SHAPES))[0]
      elif isinstance(shape, DifficultShape):
        definition = list(filter(lambda s: s[0] == shape, DIFFICULT_FIGURE_SHAPES))[0]
      else:
        definition = choice(FIGURE_SHAPES)

      item = Item.random() if self.__default_item_presence_ratio < random() else None
      figure = Figure(definition, self.__initial_pos, item)
      self.__queue.append(figure)

  def print(self):
    print("SIZE: ", len(self.__queue), end=" ")
    [print(x.shape, end=" ") for x in self.__queue]
    print()
