from enum import auto
from strenum import StrEnum
from random import choice

class Shape(StrEnum):
  BAR = 'BAR'
  SQUARE = 'SQUARE'
  Z = 'Z'
  S = 'S'
  L = 'L'
  L2 = 'L2'
  T = 'T'

class DifficultShape(StrEnum):
  # E = 'E'
  # F = 'F'
  O = 'O'
  U = 'U'

  @classmethod
  def all(cls):
    return [member.name for member in cls]

  @classmethod
  def random(cls):
    return DifficultShape(choice(DifficultShape.all()))