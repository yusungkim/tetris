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
  (Shape.BAR, 'red', [(-1, 0), (-2, 0), (0, 0), (1, 0)], (-1, 0)),
  (Shape.SQUARE, 'blue', [(0, -1), (-1, -1), (-1, 0), (0, 0)], (-0.5, -0.5)),
  (Shape.Z, 'green', [(-1, 0), (-1, 1), (0, 0), (0, -1)], (-1, 0)),
  (Shape.S, 'yellow', [(0, 0), (-1, 0), (0, 1), (-1, -1)], (0, 0)),
  (Shape.L, 'orange', [(0, 0), (0, -1), (0, 1), (-1, -1)], (0, 0)),
  (Shape.L2, 'magenta', [(0, 0), (0, -1), (0, 1), (1, -1)], (0, 0)),
  (Shape.T, 'cyan', [(0, 0), (0, -1), (0, 1), (-1, 0)], (0, 0))
]

DIFFICULT_FIGURE_SHAPES = [
  (DifficultShape.O, 'white', [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0), (2, -1), (1, -1), (0, -1)], (1, 0)),
  (DifficultShape.U, 'white', [(0, 0), (0, 1), (2, 1), (2, 0), (2, -1), (1, -1), (0, -1)], (1, 0))
]

CLOCK_WISE_90 = -math.pi / 2.0

def rotation_matrix(angle=CLOCK_WISE_90):
  return np.array([
    [math.cos(angle), -math.sin(angle)],
    [math.sin(angle), math.cos(angle)]
  ])


class Figure:
  
  def __init__(self, definition: tuple[Shape or DifficultShape, str, list[tuple[int, int]]], initial_pos=(0, 0), item: Item=None):
    """Figure
    Generate Normalized Figure with initial position, the center of x and top of y.

    Args:
        definition: (shape, color, positions, center)
          positions: (array of positions): upper left postions of tiles, length should be 4
          center: rotational center position
        field_width_and_height (tuple[int, int]): right edge of border and bottom edge of border (width and height of field)
    """
    self.shape, base_color_name, positions, (center_x, center_y) = definition
    self.fallen = False
    print("shape: ", self.shape)

    # Initial Position
    (init_x, init_y) = initial_pos
    if not isinstance(self.shape, Shape):
      init_y += 1

    # tiles
    w, h = 1, 1
    self.tiles = [pygame.Rect(init_x + x, init_y + y, w, h) for x, y in positions]
    
    # rotation center as numpy array, because pygameRect can only deal with integers
    self.center = np.array([init_x + center_x, init_y + center_y])

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
    old_center = deepcopy(self.center)
    
    # move x
    if direction == Direction.X:
      for tile in self.tiles:
        tile.x += distance
      self.center += [distance, 0]
      if self.__cannot_move(field):
        self.tiles = deepcopy(old_tiles)
        self.center = old_center

    # move y
    elif direction == Direction.Y:
      for tile in self.tiles:
        tile.y += distance
      self.center += [0, distance]
      if self.__cannot_move(field):
        if self.__fallen(field):
          self.fallen = True
        self.tiles = deepcopy(old_tiles)
        self.center = old_center

  def rotate(self, field):
    # prepare np.array vectors for calculation
    vectors = np.array([[tile.x, tile.y] for tile in self.tiles])
    
    # rotate
    rotated = np.round((vectors - self.center) @ rotation_matrix(-CLOCK_WISE_90) + self.center, decimals=0)

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

  def next(self, num: int = None):
    number_of_current_figures = len(self.__queue)
    self.previous_figure = None if number_of_current_figures == 0 else self.__queue.pop(0)
    if num:
      self.add( max(2 - number_of_current_figures, num) )
    elif number_of_current_figures <= 2:
      self.add( max(2 - number_of_current_figures, 1) )
    self.current_figure = self.__queue[0]
    self.next_figure = self.__queue[1]

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

      item = Item.random() if self.__default_item_presence_ratio > random() else None
      print("self.__default_item_presence_ratio ",  self.__default_item_presence_ratio)
      print("random() ",  random())
      print("item, ", item)
      figure = Figure(definition, self.__initial_pos, item)
      self.__queue.append(figure)
    
    self.__inspect()

  def __inspect(self):
    print("QUEUE: ", ' '.join([fig.shape.ljust(6, ' ') for fig in self.__queue]))
