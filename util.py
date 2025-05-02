RED = (255, 0, 0)
REDH = (255 // 2, 0, 0)
GREEN = (0, 255, 0)
GREENH = (0, 255 // 2, 0)
BLUE = (0, 0, 255)
BLUEH = (0, 0, 255 // 2)
WHITE = (255, 255, 255)
WHITEH = (255 // 2, 255 // 2, 255 // 2)
OFF = 0

def ix4x4(y, x):
  return (3 - y) * 4 + x

def pos4x4(i):
  return (3 - (i // 4), i % 4)

def ix4x4b(y, x):
  return y * 4 + x

def pos4x4b(i):
  return (i // 4, i % 4)
