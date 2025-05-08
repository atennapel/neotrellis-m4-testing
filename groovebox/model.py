class Step:
  def __init__(self, instrument, note):
    self.instrument = instrument
    self.note = note

class Pattern:
  def __init__(self, id):
    self.id = id
    self.steps = [None] * 16

  def __len__(self):
    return len(self.steps)

  def __getitem__(self, i):
    return self.steps[i]

  def __setitem__(self, i, step):
    self.steps[i] = step

class Synth:
  def __init__(self, id, voice):
    self.id = id
    self.voice = voice

class Sample:
  MODE_HOLD = 0
  MODE_ONESHOT = 1
  MODE_LOOP = 2

  def __init__(self, path, id, note, voice):
    self.path = path
    self.id = id
    self.note = note
    self.voice = voice
    self.mode = Sample.MODE_HOLD

  def nextMode(self):
    self.mode = (self.mode + 1) % 3

class Kit:
  def __init__(self, path, id, samples):
    self.path = path
    self.id = id
    self.samples = samples

  def __len__(self):
    return len(self.samples)
  
  def __getitem__(self, i):
    return self.samples[i]

class Model:
  def __init__(self):
    self.instruments = [None] * 16
    self.patterns = [None] * 16
    self.bpm = 120
