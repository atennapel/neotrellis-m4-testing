from model import Kit, Synth, Step, Pattern

RED = (255, 0, 0)
REDH = (255 // 2, 0, 0)
GREEN = (0, 255, 0)
GREENH = (0, 255 // 2, 0)
BLUE = (0, 0, 255)
BLUEH = (0, 0, 255 // 2)
YELLOW = (255, 255, 0)
YELLOWH = (255 // 2, 255 // 2, 0)
PINK = (255, 0, 255)
PINKH = (255 // 2, 255 // 2, 0)
CYAN = (0, 255, 255)
CYANH = (0, 255 // 2, 255 // 2)
WHITE = (255, 255, 255)
WHITEH = (255 // 2, 255 // 2, 255 // 2)
OFF = 0

naturals = [True, False, True, False, True, True, False, True, False, True, False, True]

def isNatural(note):
  return naturals[note % 12]

def noteColor(note):
  return WHITEH if isNatural(note) else CYANH

def pos2note(y, x):
  return y * 4 + x

def note2pos(note):
  return (note // 4, note % 4)

class PatternPage:
  def __init__(self, pixels, state, pageButton):
    self.pixels = pixels
    self.state = state
    self.pageButton = pageButton

  def draw(self):
    pixels = self.pixels
    state = self.state
    pattern = state.currentPattern
    if pattern:
      for y in range(4):
        for x in range(4):
          i = (3 - y) * 4 + x
          step = pattern[i]
          if step:
            pixels[(y, x)] = BLUEH
          else:
            pixels[(y, x)] = OFF
    else:
      for y in range(4):
        for x in range(4):
          pixels[(y, x)] = OFF
    for y in range(3):
      for x in range(4):
        pixels[(y, x + 4)] = OFF

  def input(self, pressed, downs, ups):
    pixels = self.pixels
    state = self.state
    pattern = state.currentPattern
    for down in downs:
      y = down[0]
      x = down[1]
      if x < 4:
        i = (3 - y) * 4 + x
        if self.pageButton in pressed:
          pattern = state.model.patterns[i]
          if not pattern:
            pattern = Pattern(i)
            state.model.patterns[i] = pattern
          prevPattern = state.currentPattern
          state.currentPattern = pattern
          if prevPattern:
            id = prevPattern.id
            pos = (3 - (id // 4), id % 4)
            pixels[pos] = OFF if prevPattern.empty else BLUEH
          pixels[down] = GREENH
        else:
          if pattern:
            step = pattern[i]
            if step:
              pattern[i] = None
              pixels[down] = OFF
            elif state.selectedInstrument and state.selectedNote != None:
              pattern[i] = Step(state.selectedInstrument, state.selectedNote)
              pixels[down] = BLUEH

  def pageButtonPressed(self):
    pixels = self.pixels
    state = self.state
    patterns = state.model.patterns
    for y in range(4):
      for x in range(4):
        i = (3 - y) * 4 + x
        pattern = patterns[i]
        if pattern:
          color = BLUEH
          if state.currentPattern == pattern:
            color = GREENH
          elif pattern.empty:
            color = OFF
          pixels[(y, x)] = color
        else:
          pixels[(y, x)] = OFF

  def pageButtonReleased(self):
    self.draw()

  def step(self, isVisible):
    pixels = self.pixels
    state = self.state
    pattern = state.currentPattern
    if pattern:
      i = state.step
      pos = (3 - (i // 4), i % 4)
      step = pattern[i]
      if step:
        state.noteOnInstrument(step.instrument, step.note)
      if isVisible:
        pixels[pos] = BLUE if step else WHITE # TODO: BUG should not draw if pagebutton is active

  def beforeStep(self, isVisible):
    pixels = self.pixels
    state = self.state
    pattern = state.currentPattern
    if pattern:
      i = state.step
      pos = (3 - (i // 4), i % 4)
      step = pattern[i]
      if step:
        state.noteOffInstrument(step.instrument, step.note)
      if isVisible:
        pixels[pos] = BLUEH if step else OFF

  def stopPlaying(self, isVisible):
    self.beforeStep(isVisible)

class InstrumentPage:
  OCTAVE_BUTTON = (2, 4)
  DEC_PLUS_BUTTON = (0, 4)
  DEC_BUTTON = (0, 5)
  INC_BUTTON = (0, 6)
  INC_PLUS_BUTTON = (0, 7)

  def __init__(self, pixels, state, pageButton):
    self.pixels = pixels
    self.state = state
    self.pageButton = pageButton
    self.noteMods = {}

  def getNoteMod(self, instrument):
    value = self.noteMods.get(instrument.id)
    if value == None:
      default = 0
      if isinstance(instrument, Synth):
        default = 60
      self.noteMods[instrument.id] = default
      return default
    return value
  
  def modNote(self, instrument, note):
    return note + self.getNoteMod(instrument)

  def modNoteUndo(self, instrument, note):
    return note - self.getNoteMod(instrument)

  def drawKeyboard(self):
    pixels = self.pixels
    state = self.state
    instrument = state.currentInstrument
    if isinstance(instrument, Kit):
      count = len(instrument)
      for y in range(4):
        for x in range(4):
          note = pos2note(y, x)
          if note < count:
            isSelected = state.selectedInstrument == instrument and state.selectedNote == note
            pixels[(y, x)] = GREENH if isSelected else BLUEH
          else:
            pixels[(y, x)] = OFF
    elif isinstance(instrument, Synth):
      for y in range(4):
        for x in range(4):
          note = self.modNote(instrument, pos2note(y, x))
          isSelected = state.selectedInstrument == instrument and state.selectedNote == note
          pixels[(y, x)] = GREENH if isSelected else noteColor(note)
    else:
      for y in range(4):
        for x in range(4):
          pixels[(y, x)] = OFF

  def draw(self):
    pixels = self.pixels
    state = self.state
    instrument = state.currentInstrument
    self.drawKeyboard()
    if isinstance(instrument, Kit):
      pixels[InstrumentPage.OCTAVE_BUTTON] = OFF
      pixels[InstrumentPage.DEC_PLUS_BUTTON] = OFF
      pixels[InstrumentPage.DEC_BUTTON] = OFF
      pixels[InstrumentPage.INC_BUTTON] = OFF
      pixels[InstrumentPage.INC_PLUS_BUTTON] = OFF
    elif isinstance(instrument, Synth):
      pixels[InstrumentPage.OCTAVE_BUTTON] = GREENH
      pixels[InstrumentPage.DEC_PLUS_BUTTON] = BLUEH
      pixels[InstrumentPage.DEC_BUTTON] = BLUEH
      pixels[InstrumentPage.INC_BUTTON] = BLUEH
      pixels[InstrumentPage.INC_PLUS_BUTTON] = BLUEH
    else:
      pixels[InstrumentPage.OCTAVE_BUTTON] = OFF
      pixels[InstrumentPage.DEC_PLUS_BUTTON] = OFF
      pixels[InstrumentPage.DEC_BUTTON] = OFF
      pixels[InstrumentPage.INC_BUTTON] = OFF
      pixels[InstrumentPage.INC_PLUS_BUTTON] = OFF

  def input(self, pressed, downs, ups):
    pixels = self.pixels
    state = self.state
    isSynth = isinstance(state.currentInstrument, Synth)
    for down in downs:
      y = down[0]
      x = down[1]
      if isSynth:
        cur = self.getNoteMod(state.currentInstrument)
        mod = 0
        if (y, x) == InstrumentPage.OCTAVE_BUTTON:
          pixels[down] = GREEN
        elif (y, x) == InstrumentPage.DEC_PLUS_BUTTON:
          if cur >= 12:
            pixels[down] = BLUE
            mod = mod - 12
        elif (y, x) == InstrumentPage.DEC_BUTTON:
          if cur > 0:
            pixels[down] = BLUE
            mod = mod - 1
        elif (y, x) == InstrumentPage.INC_BUTTON:
          if cur < 127:
            pixels[down] = BLUE
            mod = mod + 1
        elif (y, x) == InstrumentPage.INC_PLUS_BUTTON:
          if cur <= 115:
            pixels[down] = BLUE
            mod = mod + 12
        if mod != 0:
          self.noteMods[state.currentInstrument.id] = cur + mod
          self.drawKeyboard()
      if x < 4:
        if self.pageButton in pressed:
          i = (3 - y) * 4 + x
          instrument = state.model.instruments[i]
          if instrument:
            pixels[down] = RED
        else:
          instrument = state.currentInstrument
          if instrument:
            note = self.modNote(instrument, pos2note(y, x))
            if state.noteSafeCurrent(note):
              state.noteOnCurrent(note)
              pixels[down] = RED
    for up in ups:
      y = up[0]
      x = up[1]
      if isSynth:
        if (y, x) == InstrumentPage.OCTAVE_BUTTON:
          pixels[up] = GREENH
        elif (y, x) == InstrumentPage.DEC_PLUS_BUTTON or (y, x) == InstrumentPage.DEC_BUTTON or (y, x) == InstrumentPage.INC_BUTTON or (y, x) == InstrumentPage.INC_PLUS_BUTTON:
          cur = self.getNoteMod(state.currentInstrument)
          pixels[InstrumentPage.DEC_PLUS_BUTTON] = BLUEH if cur >= 12 else OFF
          pixels[InstrumentPage.DEC_BUTTON] = BLUEH if cur > 0 else OFF
          pixels[InstrumentPage.INC_BUTTON] = BLUEH if cur < 127 else OFF
          pixels[InstrumentPage.INC_PLUS_BUTTON] = BLUEH if cur <= 115 else OFF
      if x < 4:
        if self.pageButton in pressed:
          i = (3 - y) * 4 + x
          newInstrument = state.model.instruments[i]
          if newInstrument:
            if state.currentInstrument:
              prevId = state.currentInstrument.id
              pos = (3 - prevId // 4, prevId % 4)
              pixels[pos] = BLUEH if isinstance(state.currentInstrument, Kit) else CYANH
            state.currentInstrument = newInstrument
            pixels[up] = GREENH
        else:
          instrument = state.currentInstrument
          if instrument:
            note = self.modNote(instrument, pos2note(y, x))
            if state.noteSafeCurrent(note):
              state.noteOffCurrent(note)
              pixels[up] = GREENH
              prevInstrument = state.selectedInstrument
              if prevInstrument == instrument and state.selectedNote != note:
                prevPos = note2pos(self.modNoteUndo(instrument, state.selectedNote))
                if prevPos[0] >= 0 and prevPos[0] < 4 and prevPos[1] >= 0 and prevPos[1] < 4:
                  pixels[prevPos] = BLUEH if isinstance(prevInstrument, Kit) else noteColor(state.selectedNote)
              state.selectedInstrument = instrument
              state.selectedNote = note

  def pageButtonPressed(self):
    pixels = self.pixels
    state = self.state
    for y in range(4):
      for x in range(4):
        i = (3 - y) * 4 + x
        instrument = state.model.instruments[i]
        if not instrument:
          pixels[(y, x)] = OFF
        elif state.currentInstrument == instrument:
          pixels[(y, x)] = GREENH
        elif isinstance(instrument, Kit):
          pixels[(y, x)] = BLUEH
        elif isinstance(instrument, Synth):
          pixels[(y, x)] = CYANH

  def pageButtonReleased(self):
    self.draw()

class UI:
  INSTRUMENT_PAGE_BUTTON = (3, 4)
  PATTERN_PAGE_BUTTON = (3, 5)
  PLAY_BUTTON = (3, 7)

  def __init__(self):
    pass

  def init(self, pixels, state):
    self.pixels = pixels
    self.state = state
    self.instrumentPage = InstrumentPage(pixels, state, UI.INSTRUMENT_PAGE_BUTTON)
    self.patternPage = PatternPage(pixels, state, UI.PATTERN_PAGE_BUTTON)
    self.currentPage = self.instrumentPage

  def beforeStep(self):
    self.patternPage.beforeStep(self.currentPage == self.patternPage)

  def step(self):
    self.patternPage.step(self.currentPage == self.patternPage)

  def draw(self):
    pixels = self.pixels
    self.currentPage.draw()
    pixels[UI.INSTRUMENT_PAGE_BUTTON] = GREENH
    pixels[UI.PATTERN_PAGE_BUTTON] = BLUEH

  def input(self, pressed, downs, ups):
    if UI.PLAY_BUTTON in downs:
      newPlaying = not self.state.playing
      self.state.playing = not self.state.playing
      self.pixels[UI.PLAY_BUTTON] = REDH if newPlaying else OFF
      if not newPlaying:
        self.patternPage.stopPlaying(self.currentPage == self.patternPage)
      self.state.step = 15
    elif UI.INSTRUMENT_PAGE_BUTTON in downs:
      self.pixels[UI.INSTRUMENT_PAGE_BUTTON] = GREEN
      self.pixels[UI.PATTERN_PAGE_BUTTON] = BLUEH
      self.currentPage = self.instrumentPage
      self.currentPage.pageButtonPressed()
    elif UI.INSTRUMENT_PAGE_BUTTON in ups:
      self.pixels[UI.INSTRUMENT_PAGE_BUTTON] = GREENH
      self.currentPage.pageButtonReleased()
    elif UI.PATTERN_PAGE_BUTTON in downs:
      self.pixels[UI.INSTRUMENT_PAGE_BUTTON] = BLUEH
      self.pixels[UI.PATTERN_PAGE_BUTTON] = GREEN
      self.currentPage = self.patternPage
      self.currentPage.pageButtonPressed()
    elif UI.PATTERN_PAGE_BUTTON in ups:
      self.pixels[UI.PATTERN_PAGE_BUTTON] = GREENH
      self.currentPage.pageButtonReleased()
    self.currentPage.input(pressed, downs, ups)
