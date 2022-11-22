from pygame import image, transform
from strenum import LowercaseStrEnum
from enum import auto
from random import choice

# ITEM = Enum('ITEM', ['bolt', 'stop', 'fire', 'bug', 'clock', 'eye', 'dollar', 'star'])

class Item(LowercaseStrEnum):
  BOLT = auto()
  DOLLAR = auto()
  STAR = auto()
  # EYE = auto()
  
  @classmethod
  def all(cls):
    return [member.name.lower() for member in cls]

  @classmethod
  def random(cls):
    random_item_name = choice(Item.all())
    return Item(random_item_name)

  def image(self, size:tuple[int, int] = (40, 40)):
    icon_image = image.load(f"assets/icons/{self.name}.png").convert()
    icon_image = icon_image.convert_alpha()
    # return icon_image
    return transform.smoothscale(icon_image, size)