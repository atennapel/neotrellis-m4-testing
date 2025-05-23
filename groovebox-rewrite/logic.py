from sequencer import Sequencer
from painter import *
from model import Kit, Synth

class Logic:
  def __init__(self, input, painter, model, instruments):
    self.model = model
    self.input = input
    self.painter = painter
    self.instruments = instruments
    self.sequencer = Sequencer(64, 120, self)
    self.state = [False] * 32
    self.instrument = None

  def update(self, delta):
    self.sequencer.update(delta)

    model = self.model
    input = self.input
    for button in input.pressed:
      x, y = button
      self.state[x + y * 8] = True
      if x < 4:
        instrument_id = y * 4 + x
        new_instrument = model.instruments[instrument_id]
        if new_instrument:
          self.instrument = new_instrument
      elif isinstance(self.instrument, Synth):
        note = (3 - y) * 4 + (x - 4) + 60
        self.instruments.noteOn(self.instrument.id, note)
      elif isinstance(self.instrument, Kit):
        note = (3 - y) * 4 + (x - 4)
        if note < len(self.instrument):
          self.instruments.noteOn(self.instrument.id, note)

    for button in input.released:
      x, y = button
      self.state[x + y * 8] = False
      if x >= 4:
        if isinstance(self.instrument, Synth):
          note = (3 - y) * 4 + (x - 4) + 60
          self.instruments.noteOff(self.instrument.id, note)
        if isinstance(self.instrument, Kit):
          note = (3 - y) * 4 + (x - 4)
          if note < len(self.instrument):
            self.instruments.noteOff(self.instrument.id, note)

  def draw(self):
    model = self.model
    painter = self.painter
    for y in range(4):
      for x in range(8):
        if x < 4:
          instrument_id = y * 4 + x
          instrument = model.instruments[instrument_id]
          if instrument == None:
            painter.set(x, y, OFF)
          elif instrument == self.instrument:
            painter.set(x, y, RED)
          elif isinstance(instrument, Kit):
            painter.set(x, y, BLUEH)
          elif isinstance(instrument, Synth):
            painter.set(x, y, GREENH)
        else:
          instrument = self.instrument
          if instrument == None:
            painter.set(x, y, OFF)
          elif isinstance(instrument, Synth):
            if self.state[x + y * 8]:
              painter.set(x, y, RED)
            else:
              note = (3 - y) * 4 + (x - 4) + 60
              mask = [True, False, True, False, True, True, False, True, False, True, False, True]
              is_natural = mask[note % 12]
              painter.set(x, y, GREENH if is_natural else BLUEH)
          elif isinstance(instrument, Kit):
            i = (3 - y) * 4 + (x - 4)
            if i < len(instrument):
              painter.set(x, y, RED if self.state[x + y * 8] else GREENH)
            else:
              painter.set(x, y, OFF)

  def trigger(self, step):
    pass
