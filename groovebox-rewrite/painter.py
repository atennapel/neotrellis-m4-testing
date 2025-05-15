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
  (255, 0, 255), (255 // 2, 0, 255 // 2),
  (0, 255, 255), (0, 255 // 2, 255 // 2),
  (255, 255, 255), (255 // 2, 255 // 2, 255 // 2),
]

PAINTER_POSITIONS = []
for y in range(4):
  for x in range(8):
    PAINTER_POSITIONS.append((x, y))

class Painter:
  def __init__(self, pixels):
    self.pixels = pixels
    self.front = [0] * 32
    self.back = [0] * 32
    pixels.auto_write = False
    pixels.fill(0)
    pixels.show()

  def set(self, x, y, color):
    i = x + y * 8
    self.back[i] = color

  def setTuple(self, t, color):
    i = t[0] + t[1] * 8
    self.back[i] = color

  def setIndex(self, i, color):
    self.back[i] = color

  def show(self):
    pixels = self.pixels
    front = self.front
    back = self.back
    for i in range(32):
      b = back[i]
      if front[i] != b:
        pixels[PAINTER_POSITIONS[i]] = PAINTER_COLORS[b]
        front[i] = b
    pixels.show()
