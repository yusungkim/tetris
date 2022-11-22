from enum import auto
from strenum import StrEnum
from random import choice

class Shape(StrEnum):
  BAR = auto()
  SQUARE = auto()
  Z = auto()
  S = auto()
  L = auto()
  L2 = auto()
  T = auto()

class DifficultShape(StrEnum):
  # E = auto()
  # F = auto()
  O = auto()
  U = auto()

  @classmethod
  def all(cls):
    return [member.name for member in cls]

  @classmethod
  def random(cls):
    return DifficultShape(choice(DifficultShape.all()))