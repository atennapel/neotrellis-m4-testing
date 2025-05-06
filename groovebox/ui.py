from model import Kit, Synth

RED = (255, 0, 0)
REDH = (255 // 2, 0, 0)
GREEN = (0, 255, 0)
GREENH = (0, 255 // 2, 0)
BLUE = (0, 0, 255)
BLUEH = (0, 0, 255 // 2)
WHITE = (255, 255, 255)
WHITEH = (255 // 2, 255 // 2, 255 // 2)
OFF = 0

def pos2note(y, x, mod, octave):
  return (60 + x) + y * 4 + mod + octave * 12

def isNatural(note):
  octnote = note % 12
  return not (octnote == 1 or octnote == 3 or octnote == 6 or octnote == 8 or octnote == 10)

class InstrumentPage:
  def __init__():
    pass

  def draw(self, pixels, state):
    instrument = state.currentInstrument
    if isinstance(instrument, Kit):
      pass
    elif isinstance(instrument, Synth):
      for y in range(4):
        for x in range(4):
          note = pos2note(y, x, 0, 0)
          pixels[(y, x)] = GREENH if isNatural(note) else REDH

class UI:
  INSTRUMENT_PAGE_BUTTON = (3, 4)

  def __init__(self):
    self.instrumentPage = InstrumentPage()
    self.currentPage = self.instrumentPage

  def beforeStep(self):
    pass

  def step(self):
    pass

  def draw(self, pixels, state):
    self.currentPage.draw(pixels, state)
    pixels[UI.INSTRUMENT_PAGE_BUTTON] = GREENH
