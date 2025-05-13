import time
import adafruit_trellism4
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

MIDI_IN_CHANNEL = 0
MIDI_OUT_CHANNEL = 0
VELOCITY = 127

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
MIDI2POS = []
for y in range(4):
  for x in range(8):
    MIDI2POS.append((x, y))

trellis = adafruit_trellism4.TrellisM4Express()

midi = adafruit_midi.MIDI(
  midi_in = usb_midi.ports[0],
  midi_out = usb_midi.ports[1],
  in_channel = MIDI_IN_CHANNEL,
  out_channel = MIDI_OUT_CHANNEL
)

def vel2color(vel):
  if vel >= VELOCITY_COLORS_LEN:
    return 0
  return VELOCITY_COLORS[vel]

def pos2midi(x, y):
  return y * 8 + x

def midi2pos(midi):
  return MIDI2POS[midi]

pressed = set()
while True:
  newpressed = set(trellis.pressed_keys)
  downs = newpressed - pressed
  ups = pressed - newpressed

  for down in downs:
    x, y = down
    midi.send(NoteOn(pos2midi(x, y), VELOCITY))

  for up in ups:
    x, y = up
    midi.send(NoteOff(pos2midi(x, y), 0))

  msg = midi.receive()
  if msg:
    if isinstance(msg, NoteOn):
      note = msg.note
      if note < 32:
        x, y = midi2pos(note)
        trellis.pixels[x, y] = vel2color(msg.velocity)
    elif isinstance(msg, NoteOff):
      note = msg.note
      if note < 32:
        x, y = midi2pos(note)
        trellis.pixels[x, y] = 0

  pressed = newpressed