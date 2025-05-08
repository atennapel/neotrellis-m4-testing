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

PAINTER_POSITIONS = []
for y in range(4):
  for x in range(8):
    PAINTER_POSITIONS.append((y, x))

class Painter:
  def __init__(self, pixels):
    self.pixels = pixels
    self.front = [0] * 32
    self.back = [0] * 32
    pixels.fill(0)
    pixels.auto_write = False

  def set(self, y, x, color):
    i = y * 8 + x
    self.back[i] = color

  def setIndex(self, i, color):
    self.back[i] = color

  def draw(self):
    pixels = self.pixels
    front = self.front
    back = self.back
    for i in range(32):
      b = back[i]
      if front[i] != b:
        pixels[PAINTER_POSITIONS[i]] = PAINTER_COLORS[b]
        front[i] = b
    pixels.show()
