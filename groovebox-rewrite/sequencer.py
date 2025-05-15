class Sequencer:
  def __init__(self, length, bpm, triggerable):
    self.length = length or 16
    self.bpm = bpm or 120
    self.buffer = 0
    self.step = 0
    self.playing = False
    self.triggerable = triggerable

  @property
  def bpm(self):
    return self._bpm

  @bpm.setter
  def bpm(self, v):
    self._bpm = v
    self.bpmDelta = 60000000000 / (v * 4)

  def update(self, delta):
    if self.playing:
      self.buffer += delta
      bpmDelta = self.bpmDelta
      if self.buffer >= bpmDelta:
        self.buffer -= bpmDelta
        self.trigger()
        self.step = (self.step + 1) % self.length

  def start(self):
    self.playing = True

  def stop(self):
    self.step = 0
    self.playing = False

  def trigger(self):
    self.triggerable.trigger(self.step)
