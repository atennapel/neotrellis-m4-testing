from adafruit_macropad import MacroPad, NoteOn, NoteOff

CHANNEL = 15
ENCODER = 12
ENCODER_SWITCH = 13

macropad = MacroPad()
pixels = macropad.pixels
midi = macropad.midi
text = macropad.display_text()

text[0].text = "Starting..."

VELOCITY_COLORS = [
  0,
  (255, 0, 0),
  (255 // 2, 0, 0),
  (0, 255, 0),
  (0, 255 // 2, 0),
  (0, 0, 255),
  (0, 0, 255 // 2),
  (255, 255, 0),
  (255 // 2, 255 // 2, 0),
  (255, 0, 255),
  (255 // 2, 0, 255 // 2),
  (0, 255, 255),
  (0, 255 // 2, 255 // 2),
  (255, 255, 255),
  (255 // 2, 255 // 2, 255 // 2),
]
VELOCITY_COLORS_LEN = len(VELOCITY_COLORS)
def vel2color(vel):
  if vel >= VELOCITY_COLORS_LEN:
    return 0
  return VELOCITY_COLORS[vel]

text[0].text = "Started"
text[1].text = "Encoder: 0"
text.show()

last_enc = 0
last_switch = False
while True:
  enc = macropad.encoder
  if enc != last_enc:
    diff = enc - last_enc
    midi.send(NoteOn(ENCODER, velocity = 100 + diff, channel = CHANNEL))
    last_enc = enc
    text[1].text = "Encoder: " + str(enc)
    text.show()

  switch = macropad.encoder_switch
  if switch != last_switch:
    if switch:
      midi.send(NoteOn(ENCODER_SWITCH, channel = CHANNEL))
    else:
      midi.send(NoteOff(ENCODER_SWITCH, channel = CHANNEL))
    last_switch = switch

  key_event = macropad.keys.events.get()
  if key_event:
    if key_event.pressed:
      key = key_event.key_number
      midi.send(NoteOn(key, channel = CHANNEL))
    else:
      key = key_event.key_number
      midi.send(NoteOff(key, channel = CHANNEL))

  msg = macropad.midi.receive()
  if msg:
    if isinstance(msg, NoteOn):
      note = msg.note
      if note < 12:
        pixels[note] = vel2color(msg.velocity)
    elif isinstance(msg, NoteOff):
      note = msg.note
      if note < 12:
        pixels[note] = 0
