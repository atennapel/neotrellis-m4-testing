OFF = 0
RED = 1
REDH = 2
GREEN = 3
GREENH = 4
BLUE = 5
BLUEH = 6
YELLOW = 7
YELLOWH = 8
PINK = 9
PINKH = 10
CYAN = 11
CYANH = 12
WHITE = 13
WHITEH = 14

PAINTER_COLORS = [
  0,
  (255, 0, 0), (255 // 2, 0, 0),
  (0, 255, 0), (0, 255 // 2, 0),
  (0, 0, 255), (0, 0, 255 // 2),
  (255, 255, 0), (255 // 2, 255 // 2, 0),
  (255, 0, 255), (255 // 2, 255 // 2, 0),
  (0, 255, 255), (0, 255 // 2, 255 // 2),
  (255, 255, 255), (255 // 2, 255 // 2, 255 // 2),
]

class Painter:
  def __init__(self, pixels):
    self.pixels = pixels
    self.buffer = [[0] * 32, [0] * 32]
    self.pointer = 0

  def set(self, y, x, color):
    i = y * 8 + x
    self.buffer[self.pointer][i] = color

  def setIndex(self, i, color):
    self.buffer[self.pointer][i] = color

  def draw(self):
    pixels = self.pixels
    pointer = self.pointer
    back = self.buffer[pointer]
    front = self.buffer[1 - pointer]
    self.pointer = 1 - pointer
    for i in range(32):
      b = back[i]
      if front[i] != b:
        pixels[(i // 8, i % 8)] = PAINTER_COLORS[b]
        front[i] = b
