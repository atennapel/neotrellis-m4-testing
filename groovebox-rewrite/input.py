class Input:
  def __init__(self, trellis, encoder, encoder_button):
    self.trellis = trellis
    self.encoder = encoder
    self.encoder_button = encoder_button
    self.held = set()
    self.pressed = set()
    self.released = set()
    self.encoder_position = encoder.position
    self.encoder_diff = 0
    self.encoder_button_held = True
    self.encoder_button_pressed = False
    self.encoder_button_released = False

  def update(self):
    next = set(self.trellis.pressed_keys)
    prev = self.held
    self.held = next
    self.pressed = next - prev
    self.released = prev - next

    next_encoder_position = self.encoder.position
    prev_encoder_position = self.encoder_position
    if next_encoder_position != prev_encoder_position:
      self.encoder_diff = next_encoder_position - prev_encoder_position
      self.encoder_position = next_encoder_position

    encoder_next = self.encoder_button.value
    encoder_prev = self.encoder_button_held
    self.encoder_button_held = encoder_next
    if encoder_next != encoder_prev:
      self.encoder_button_pressed = encoder_next
      self.encoder_button_released = not encoder_next
    else:
      self.encoder_button_pressed = False
      self.encoder_button_released = False

  def isHeld(self, button):
    return button in self.held
