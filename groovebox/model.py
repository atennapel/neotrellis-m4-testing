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

class Kit:
  def __init__(self, path, id, samples):
    self.path = path
    self.id = id
    self.samples = samples

  def __len__(self):
    return len(self.samples)

class Model:
  def __init__(self):
    self.instruments = [None] * 16
    self.patterns = [None] * 16
    self.bpm = 120
