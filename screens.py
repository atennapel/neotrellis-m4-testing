from util import *

PARAM_BUTTON = [(2, 4), (2, 5), (2, 6), (2, 7), (1, 4), (1, 5), (1, 6), (1, 7)]

class KitScreen:
  def __init__(self, trellis, kits):
    self.trellis = trellis
    self.kits = kits
    self.selectedKit = 0
    self.selectedSample = (0, 0)
    self.selectedSampleRef = self.kits[self.selectedSample[0]][self.selectedSample[1]]

  def draw(self):
    for i in range(8):
      self.trellis.pixels[PARAM_BUTTON[i]] = OFF
    self.trellis.pixels[PARAM_BUTTON[0]] = self.selectedSampleRef.modeColor()
    for y in range(4):
      for x in range(4):
        i = ix4x4b(y, x)
        color = OFF
        if self.kits.available(self.selectedKit, i):
          selected = self.selectedSample == (self.selectedKit, i)
          color = GREENH if selected else BLUEH
        self.trellis.pixels[(y, x)] = color

  def drawSelection(self):
    kit_count = len(self.kits)
    for y in range(4):
      for x in range(4):
        i = ix4x4(y, x)
        color = OFF
        if self.selectedKit == i:
          color = GREEN
        elif i < kit_count:
          color = BLUEH
        self.trellis.pixels[(y, x)] = color

  def selectKit(self, i):
    if i != self.selectedKit and i < len(self.kits):
      self.trellis.pixels[pos4x4(self.selectedKit)] = BLUEH
      self.selectedKit = i
      self.trellis.pixels[pos4x4(self.selectedKit)] = GREEN

  def input(self, pressed, downs, ups, page_button_held):
    kits = self.kits
    trellis = self.trellis
    for down in downs:
      y = down[0]
      x = down[1]
      if (y, x) == PARAM_BUTTON[0]:
        self.trellis.pixels[PARAM_BUTTON[0]] = RED
      elif x < 4:
        if page_button_held:
          self.selectKit(ix4x4(y, x))
        else:
          sample_ix = ix4x4b(y, x)
          if kits.available(self.selectedKit, sample_ix):
            kits.play(self.selectedKit, sample_ix)
            trellis.pixels[down] = RED
            oldSelectedKit = self.selectedSample[0]
            oldSelectedSample = self.selectedSample[1]
            oldPos = pos4x4b(oldSelectedSample)
            if oldSelectedKit == self.selectedKit and oldSelectedSample != sample_ix and not (oldPos in pressed):
              trellis.pixels[oldPos] = BLUEH
            self.selectedSample = (self.selectedKit, sample_ix)
            self.selectedSampleRef = self.kits[self.selectedSample[0]][self.selectedSample[1]]
            self.trellis.pixels[PARAM_BUTTON[0]] = self.selectedSampleRef.modeColor()
    for up in ups:
      y = up[0]
      x = up[1]
      if (y, x) == PARAM_BUTTON[0]:
        self.selectedSampleRef.nextMode()
        self.trellis.pixels[PARAM_BUTTON[0]] = self.selectedSampleRef.modeColor()
      elif x < 4:
        if not page_button_held:
          sample_ix = ix4x4b(y, x)
          if kits.available(self.selectedKit, sample_ix):
            kits.stop(self.selectedKit, sample_ix)
            selected = self.selectedSample == (self.selectedKit, sample_ix)
            trellis.pixels[up] = GREENH if selected else BLUEH

class PatternScreen:
  def __init__(self, trellis):
    self.trellis = trellis

  def draw(self):
    for i in range(16):
      self.trellis.pixels[pos4x4(i)] = OFF
    for i in range(8):
      self.trellis.pixels[PARAM_BUTTON[i]] = OFF

  def drawSelection(self):
    pass

  def input(self, pressed, downs, ups, page_button_held):
    pass

KIT_SELECTION_BUTTON = (3, 4)
PATTERN_SELECTION_BUTTON = (3, 5)

class MainScreen:
  def __init__(self, trellis, kits):
    self.trellis = trellis
    self.kitScreen = KitScreen(trellis, kits)
    self.patternScreen = PatternScreen(trellis)
    self.selectedScreen = self.kitScreen

  def draw(self):
    for x in range(2):
      color = BLUEH
      if (self.selectedScreen == self.kitScreen and x == 0) or (self.selectedScreen == self.patternScreen and x == 1):
        color = GREENH
      self.trellis.pixels[(3, x + 4)] = color
    self.selectedScreen.draw()

  def input(self, pressed, downs, ups):
    if KIT_SELECTION_BUTTON in downs:
      self.selectedScreen = self.kitScreen
      self.draw()
      self.trellis.pixels[KIT_SELECTION_BUTTON] = GREEN
      self.selectedScreen.drawSelection()
    elif KIT_SELECTION_BUTTON in ups:
      self.selectedScreen = self.kitScreen
      self.draw()
    elif PATTERN_SELECTION_BUTTON in downs:
      self.selectedScreen = self.patternScreen
      self.draw()
      self.trellis.pixels[PATTERN_SELECTION_BUTTON] = GREEN
      self.selectedScreen.drawSelection()
    elif PATTERN_SELECTION_BUTTON in ups:
      self.selectedScreen = self.patternScreen
      self.draw()
    page_button_held = False
    if self.selectedScreen == self.patternScreen and PATTERN_SELECTION_BUTTON in pressed:
      page_button_held = True
    elif self.selectedScreen == self.kitScreen and KIT_SELECTION_BUTTON in pressed:
      page_button_held = True
    self.selectedScreen.input(pressed, downs, ups, page_button_held)
