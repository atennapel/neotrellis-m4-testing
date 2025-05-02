from util import *

class KitScreen:
  def __init__(self, trellis, kits):
    self.trellis = trellis
    self.kits = kits
    self.selected = 0

  def draw(self):
    for y in range(4):
      for x in range(4):
        i = ix4x4b(y, x)
        color = OFF
        if self.kits.available(self.selected, i):
          color = BLUEH
        self.trellis.pixels[(y, x)] = color

  def drawSelection(self):
    kit_count = len(self.kits)
    for y in range(4):
      for x in range(4):
        i = ix4x4(y, x)
        color = OFF
        if self.selected == i:
          color = GREEN
        elif i < kit_count:
          color = BLUEH
        self.trellis.pixels[(y, x)] = color

  def select(self, i):
    if i != self.selected and i < len(self.kits):
      self.trellis.pixels[pos4x4(self.selected)] = BLUEH
      self.selected = i
      self.trellis.pixels[pos4x4(self.selected)] = GREEN
