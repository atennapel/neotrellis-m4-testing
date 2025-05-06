class Step:
  def __init__(self, instrument, note):
    self.enabled = True
    self.instrument = instrument
    self.note = note

class Pattern:
  def __init__(self):
    self.steps = [None] * 16

  def __len__(self):
    return len(self.steps)

  def __getitem__(self, i):
    return self.steps[i]

class Song:
  def __init__(self):
    self.patterns = [None] * 16

class Instrument:
  def __init__(self, id):
    self.id = id

class State:
  def __init__(self):
    self.instruments = [None] * 16
    self.songs = [None] * 16
