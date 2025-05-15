class Input:
  def __init__(self, trellis):
    self.trellis = trellis
    self.held = set()
    self.pressed = set()
    self.released = set()

  def update(self):
    next = set(self.trellis.pressed_keys)
    prev = self.held
    self.held = next
    self.pressed = next - prev
    self.released = prev - next
