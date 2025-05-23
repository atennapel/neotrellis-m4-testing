OFF = 0
RED = 1
REDH = 2
GREEN = 3
GREENH = 4
BLUE = 5
BLUEH = 6
YELLOW = 7
YELLOWH = 8
PURPLE = 9
PURPLEH = 10
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
  def __init__(self, pixels, encoder_pixel):
    self.pixels = pixels
    self.encoder_pixel = encoder_pixel
    self.front = [0] * 32
    self.back = [0] * 32
    self.encoder_front = 0
    self.encoder_back = 0
    pixels.auto_write = False
    encoder_pixel.auto_write = False
    pixels.fill(0)
    encoder_pixel.fill(0)
    pixels.show()
    encoder_pixel.show()

  def setBrightness(self, value):
    self.pixels.brightness = value

  def setEncoderBrightness(self, value):
    self.encoder_pixel.brightness = value
  
  def setEncoder(self, color):
    self.encoder_back = color

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

    encoder_pixel = self.encoder_pixel
    encoder_back = self.encoder_back
    if self.encoder_front != encoder_back:
      encoder_pixel.fill(PAINTER_COLORS[encoder_back])
      self.encoder_front = encoder_back

    pixels.show()
    encoder_pixel.show()
