# Midi controller

import time
import board
import audioio
import audiomixer
import adafruit_trellism4
import synthio
import usb_midi
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn

trellis = adafruit_trellism4.TrellisM4Express(rotation = 90)
trellis.pixels.brightness = 0.05

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

mod = 0
octave = 0

def pos2note(y, x):
  return (60 + x) + y * 5 + mod + octave * 12

def isNatural(note):
  octnote = note % 12
  return not (octnote == 1 or octnote == 3 or octnote == 6 or octnote == 8 or octnote == 10)

RED = (255, 0, 0)
REDH = (255 // 2, 0, 0)
GREEN = (0, 255, 0)
GREENH = (0, 255 // 2, 0)
BLUE = (0, 0, 255)
BLUEH = (0, 0, 255 // 2)
WHITE = (255, 255, 255)
WHITEH = (255 // 2, 255 // 2, 255 // 2)
OFF = 0

def updateNoteColors():
  for y in range(4):
    for x in range(7):
      note = pos2note(y, x)
      trellis.pixels[(y, x)] = GREENH if isNatural(note) else REDH

updateNoteColors()

pressed = set()

while True:
  newpressed = set(trellis.pressed_keys)
  for down in newpressed - pressed:
    y = down[0]
    x = down[1]
    if x < 7:
      note = pos2note(y, x)
      midi.send(NoteOn(note))
      trellis.pixels[(y, x)] = GREEN if isNatural(note) else RED
    else:
      if y == 0:
        if mod > -11:
          trellis.pixels[(y, x)] = BLUE
          mod = mod - 1
          updateNoteColors()
          trellis.pixels[(y, x)] = BLUEH if mod < 0 else OFF
          trellis.pixels[(1, x)] = BLUEH if mod > 0 else OFF
      elif y == 1:
        if mod < 11:
          trellis.pixels[(y, x)] = BLUE
          mod = mod + 1
          updateNoteColors()
          trellis.pixels[(0, x)] = BLUEH if mod < 0 else OFF
          trellis.pixels[(y, x)] = BLUEH if mod > 0 else OFF
      elif y == 2:
        if octave > -5:
          trellis.pixels[(y, x)] = BLUE
          octave = octave - 1
          trellis.pixels[(y, x)] = BLUEH if octave < 0 else OFF
          trellis.pixels[(3, x)] = BLUEH if octave > 0 else OFF
      elif y == 3:
        if octave < 5:
          trellis.pixels[(y, x)] = BLUE
          octave = octave + 1
          trellis.pixels[(2, x)] = BLUEH if octave < 0 else OFF
          trellis.pixels[(y, x)] = BLUEH if octave > 0 else OFF
  for up in pressed - newpressed:
    y = up[0]
    x = up[1]
    if x < 7:
      note = pos2note(y, x)
      midi.send(NoteOff(note))
      trellis.pixels[(y, x)] = GREENH if isNatural(note) else REDH
  pressed = newpressed
  time.sleep(0.01)
