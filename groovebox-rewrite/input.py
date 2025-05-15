class Input:
  def __init__(self, trellis):
    self.trellis = trellis
    self.prevheld = set()
    self.held = set()
    self.pressed = set()
    self.released = set()

  def update(self):
    prev = self.prevheld
    next = set(self.trellis.pressed_keys)
    self.prevheld = self.held
    self.held = next
    self.pressed = next - prev
    self.released = prev - next
