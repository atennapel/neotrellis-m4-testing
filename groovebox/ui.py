from model import Kit, Sample, Synth, Step, Pattern
from painter import *

naturals = [True, False, True, False, True, True, False, True, False, True, False, True]

def isNatural(note):
  return naturals[note % 12]

def noteColor(note, bright = False):
  if bright:
    return WHITE if isNatural(note) else CYAN
  return WHITEH if isNatural(note) else CYANH

def pos2note(y, x):
  return y * 4 + x

def note2pos(note):
  return (note // 4, note % 4)

class PatternPage:
  def __init__(self, painter, state, pageButton):
    self.painter = painter
    self.state = state
    self.pageButton = pageButton
    self.pageButtonHeld = False

  def draw(self):
    painter = self.painter
    state = self.state
    if self.pageButtonHeld:
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
            painter.set(y, x, color)
          else:
            painter.set(y, x, OFF)
    else:
      pattern = state.currentPattern
      if pattern:
        for y in range(4):
          for x in range(4):
            i = (3 - y) * 4 + x
            step = pattern[i]
            isStep = state.playing and state.step == i
            if step:
              painter.set(y, x, CYAN if isStep else BLUEH)
            else:
              painter.set(y, x, WHITE if isStep else OFF)
      else:
        for y in range(4):
          for x in range(4):
            i = (3 - y) * 4 + x
            isStep = state.playing and state.step == i
            painter.set(y, x, WHITE if isStep else OFF)
      for y in range(3):
        for x in range(4):
          painter.set(y, x + 4, OFF)

  def input(self, pressed, downs, ups):
    state = self.state
    for down in downs:
      y = down[0]
      x = down[1]
      if x < 4:
        i = (3 - y) * 4 + x
        if self.pageButtonHeld:
          pattern = state.model.patterns[i]
          if not pattern:
            pattern = Pattern(i)
            state.model.patterns[i] = pattern
          state.currentPattern = pattern
        else:
          pattern = state.currentPattern
          if pattern:
            step = pattern[i]
            if step:
              pattern[i] = None
            elif state.selectedInstrument and state.selectedNote != None:
              pattern[i] = Step(state.selectedInstrument, state.selectedNote)

  def pageButtonPressed(self):
    self.pageButtonHeld = True

  def pageButtonReleased(self):
    self.pageButtonHeld = False

  def step(self):
    state = self.state
    pattern = state.currentPattern
    if pattern:
      step = pattern[state.step]
      if step:
        state.noteOnInstrument(step.instrument, step.note)

  def beforeStep(self):
    state = self.state
    pattern = state.currentPattern
    if pattern:
      step = pattern[state.step]
      if step:
        state.noteOffInstrument(step.instrument, step.note)

  def stopPlaying(self):
    self.beforeStep()

class InstrumentPage:
  PARAM1_BUTTON = (2, 4)
  DEC_PLUS_BUTTON = (0, 4)
  DEC_BUTTON = (0, 5)
  INC_BUTTON = (0, 6)
  INC_PLUS_BUTTON = (0, 7)

  def __init__(self, painter, state, pageButton):
    self.painter = painter
    self.state = state
    self.pageButton = pageButton
    self.pageButtonHeld = False
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

  def drawKeyboard(self):
    painter = self.painter
    state = self.state
    instrument = state.currentInstrument
    if isinstance(instrument, Kit):
      count = len(instrument)
      for y in range(4):
        for x in range(4):
          note = pos2note(y, x)
          if note < count:
            isSelected = state.selectedInstrument == instrument and state.selectedNote == note
            if state.isNoteOn(instrument, note):
              painter.set(y, x, GREEN if isSelected else RED)
            else:
              painter.set(y, x, GREENH if isSelected else BLUEH)
          else:
            painter.set(y, x, OFF)
    elif isinstance(instrument, Synth):
      for y in range(4):
        for x in range(4):
          note = self.modNote(instrument, pos2note(y, x))
          if state.selectedInstrument == instrument and state.selectedNote == note:
            painter.set(y, x, GREENH)
          elif state.isNoteOn(instrument, note):
            painter.set(y, x, RED)
          else:
            painter.set(y, x, noteColor(note, False))
    else:
      for y in range(4):
        for x in range(4):
          painter.set(y, x, OFF)

  def draw(self):
    painter = self.painter
    state = self.state
    if self.pageButtonHeld:
      for y in range(4):
        for x in range(4):
          i = (3 - y) * 4 + x
          instrument = state.model.instruments[i]
          if not instrument:
            painter.set(y, x, OFF)
          elif state.currentInstrument == instrument:
            painter.set(y, x, GREENH)
          elif isinstance(instrument, Kit):
            painter.set(y, x, BLUEH)
          elif isinstance(instrument, Synth):
            painter.set(y, x, CYANH)
    else:
      instrument = state.currentInstrument
      self.drawKeyboard()
      if isinstance(instrument, Kit):
        painter.setTuple(InstrumentPage.DEC_PLUS_BUTTON, OFF)
        painter.setTuple(InstrumentPage.DEC_BUTTON, OFF)
        painter.setTuple(InstrumentPage.INC_BUTTON, OFF)
        painter.setTuple(InstrumentPage.INC_PLUS_BUTTON, OFF)
        if state.selectedInstrument == instrument:
          mode = instrument[state.selectedNote].mode
          if mode == Sample.MODE_HOLD:
            painter.setTuple(InstrumentPage.PARAM1_BUTTON, PINKH)
          elif mode == Sample.MODE_ONESHOT:
            painter.setTuple(InstrumentPage.PARAM1_BUTTON, CYANH)
          elif mode == Sample.MODE_LOOP:
            painter.setTuple(InstrumentPage.PARAM1_BUTTON, YELLOWH)
          else:
            painter.setTuple(InstrumentPage.PARAM1_BUTTON, OFF)
        else:
          painter.setTuple(InstrumentPage.PARAM1_BUTTON, OFF)
      elif isinstance(instrument, Synth):
        painter.setTuple(InstrumentPage.PARAM1_BUTTON, GREENH)
        cur = self.getNoteMod(instrument)
        painter.setTuple(InstrumentPage.DEC_PLUS_BUTTON, BLUEH if cur >= 12 else OFF)
        painter.setTuple(InstrumentPage.DEC_BUTTON, BLUEH if cur > 0 else OFF)
        painter.setTuple(InstrumentPage.INC_BUTTON, BLUEH if cur < 127 else OFF)
        painter.setTuple(InstrumentPage.INC_PLUS_BUTTON, BLUEH if cur <= 115 else OFF)
      else:
        painter.setTuple(InstrumentPage.PARAM1_BUTTON, OFF)
        painter.setTuple(InstrumentPage.DEC_PLUS_BUTTON, OFF)
        painter.setTuple(InstrumentPage.DEC_BUTTON, OFF)
        painter.setTuple(InstrumentPage.INC_BUTTON, OFF)
        painter.setTuple(InstrumentPage.INC_PLUS_BUTTON, OFF)

  def input(self, pressed, downs, ups):
    state = self.state
    for down in downs:
      y = down[0]
      x = down[1]
      instrument = state.currentInstrument
      if isinstance(instrument, Synth):
        cur = self.getNoteMod(instrument)
        mod = 0
        if (y, x) == InstrumentPage.DEC_PLUS_BUTTON:
          if cur >= 12:
            mod = mod - 12
        elif (y, x) == InstrumentPage.DEC_BUTTON:
          if cur > 0:
            mod = mod - 1
        elif (y, x) == InstrumentPage.INC_BUTTON:
          if cur < 127:
            mod = mod + 1
        elif (y, x) == InstrumentPage.INC_PLUS_BUTTON:
          if cur <= 115:
            mod = mod + 12
        self.noteMods[instrument.id] = cur + mod
      elif isinstance(instrument, Kit):
        if state.selectedInstrument == instrument:
          if (y, x) == InstrumentPage.PARAM1_BUTTON:
            instrument[state.selectedNote].nextMode()
      if x < 4:
        if self.pageButtonHeld:
          i = (3 - y) * 4 + x
          newInstrument = state.model.instruments[i]
          if newInstrument:
            state.currentInstrument = newInstrument
        else:
          if instrument:
            note = self.modNote(instrument, pos2note(y, x))
            if state.noteSafeCurrent(note):
              state.noteOnCurrent(note)
              state.selectedInstrument = instrument
              state.selectedNote = note
    for up in ups:
      y = up[0]
      x = up[1]
      if x < 4 and not self.pageButtonHeld:
        instrument = state.currentInstrument
        if instrument:
          note = self.modNote(instrument, pos2note(y, x))
          if state.noteSafeCurrent(note):
            state.noteOffCurrent(note)

  def pageButtonPressed(self):
    self.pageButtonHeld = True

  def pageButtonReleased(self):
    self.pageButtonHeld = False

class UI:
  INSTRUMENT_PAGE_BUTTON = (3, 4)
  PATTERN_PAGE_BUTTON = (3, 5)
  PLAY_BUTTON = (3, 7)

  def __init__(self):
    pass

  def init(self, painter, state):
    self.painter = painter
    self.state = state
    self.instrumentPage = InstrumentPage(painter, state, UI.INSTRUMENT_PAGE_BUTTON)
    self.patternPage = PatternPage(painter, state, UI.PATTERN_PAGE_BUTTON)
    self.currentPage = self.instrumentPage
    self.instrumentPageButtonHeld = False
    self.patternPageButtonHeld = False

  def beforeStep(self):
    self.patternPage.beforeStep()

  def step(self):
    self.patternPage.step()

  def draw(self):
    painter = self.painter
    self.currentPage.draw()
    painter.setTuple(UI.PLAY_BUTTON, REDH if self.state.playing else OFF)
    if self.currentPage == self.instrumentPage:
      painter.setTuple(UI.INSTRUMENT_PAGE_BUTTON, GREEN if self.instrumentPageButtonHeld else GREENH)
      painter.setTuple(UI.PATTERN_PAGE_BUTTON, BLUEH)
    elif self.currentPage == self.patternPage:
      painter.setTuple(UI.INSTRUMENT_PAGE_BUTTON, BLUEH)
      painter.setTuple(UI.PATTERN_PAGE_BUTTON, GREEN if self.patternPageButtonHeld else GREENH)

  def input(self, pressed, downs, ups):
    if UI.PLAY_BUTTON in downs:
      newPlaying = not self.state.playing
      self.state.startPlaying = newPlaying
      if not newPlaying:
        self.state.stopPlaying()
        self.patternPage.stopPlaying()
    elif UI.INSTRUMENT_PAGE_BUTTON in downs:
      self.instrumentPageButtonHeld = True
      self.currentPage = self.instrumentPage
      self.currentPage.pageButtonPressed()
    elif UI.INSTRUMENT_PAGE_BUTTON in ups:
      self.instrumentPageButtonHeld = False
      self.currentPage.pageButtonReleased()
    elif UI.PATTERN_PAGE_BUTTON in downs:
      self.patternPageButtonHeld = True
      self.currentPage = self.patternPage
      self.currentPage.pageButtonPressed()
    elif UI.PATTERN_PAGE_BUTTON in ups:
      self.patternPageButtonHeld = False
      self.currentPage.pageButtonReleased()
    self.currentPage.input(pressed, downs, ups)
