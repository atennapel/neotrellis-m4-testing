from util import *

KIT_SELECTION_BUTTON = (3, 4)

PARAM_BUTTON = [(2, 4), (2, 5), (2, 6), (2, 7), (1, 4), (1, 5), (1, 6), (1, 7)]

class KitScreen:
  def __init__(self, trellis, kits):
    self.trellis = trellis
    self.kits = kits
    self.selectedKit = 0
    self.selectedSample = (0, 0)
    self.selectedSampleRef = self.kits[self.selectedSample[0]][self.selectedSample[1]]

  def init(self):
    self.draw()

  def draw(self):
    self.trellis.pixels[PARAM_BUTTON[0]] = BLUEH
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

  def input(self, pressed, downs, ups):
    kits = self.kits
    trellis = self.trellis
    for down in downs:
      y = down[0]
      x = down[1]
      if (y, x) == PARAM_BUTTON[0]:
        self.trellis.pixels[PARAM_BUTTON[0]] = RED
      elif x < 4:
        if KIT_SELECTION_BUTTON in pressed:
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
        if not (KIT_SELECTION_BUTTON in pressed):
          sample_ix = ix4x4b(y, x)
          if kits.available(self.selectedKit, sample_ix):
            kits.stop(self.selectedKit, sample_ix)
            selected = self.selectedSample == (self.selectedKit, sample_ix)
            trellis.pixels[up] = GREENH if selected else BLUEH

class MainScreen:
  def __init__(self, trellis, kits):
    self.trellis = trellis
    self.kitScreen = KitScreen(trellis, kits)
    self.selectedScreen = 0

  def init(self):
    self.draw()
    self.kitScreen.draw()

  def draw(self):
    for x in range(1):
      color = BLUEH
      if x == self.selectedScreen:
        color = GREENH
      self.trellis.pixels[(3, x + 4)] = color

  def input(self, pressed, downs, ups):
    if KIT_SELECTION_BUTTON in downs:
      self.trellis.pixels[KIT_SELECTION_BUTTON] = GREEN
      self.kitScreen.drawSelection()
    elif KIT_SELECTION_BUTTON in ups:
      self.trellis.pixels[KIT_SELECTION_BUTTON] = GREENH
      self.kitScreen.draw()
    self.kitScreen.input(pressed, downs, ups)
