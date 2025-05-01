# Left 4x4 to control notes, right 4x4 to control synth settings

import time
import board
import audioio
import audiomixer
import adafruit_trellism4
import synthio

trellis = adafruit_trellism4.TrellisM4Express(rotation = 90)
trellis.pixels.brightness = 0.05

audio = audioio.AudioOut(board.A1)
mixer = audiomixer.Mixer(channel_count=1, sample_rate = 22050, buffer_size = 2048)
synth = synthio.Synthesizer(channel_count = 1, sample_rate = 22050)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 0.2

frequency = 2000
resonance = 1.5
lpf = synth.low_pass_filter(frequency, resonance)
hpf = synth.high_pass_filter(frequency, resonance)
bpf = synth.band_pass_filter(frequency, resonance)

RED = (255, 0, 0)
REDH = (255 // 2, 0, 0)
GREEN = (0, 255, 0)
GREENH = (0, 255 // 2, 0)
BLUE = (0, 0, 255)
BLUEH = (0, 0, 255 // 2)
WHITE = (255, 255, 255)
WHITEH = (255 // 2, 255 // 2, 255 // 2)
OFF = 0

filter = None
mod = 0
octave = 0

trellis.pixels[(3, 4)] = BLUE

a = 2
d = 1
s = 10
r = 8

def updateEnvelope():
  synth.envelope = synthio.Envelope(attack_time = a / 10, decay_time = d / 10, sustain_level = s / 10, release_time = r / 10)

updateEnvelope()

def pos2note(y, x):
  return (60 + x) + y * 4 + mod + octave * 12

def isNatural(note):
  octnote = note % 12
  return not (octnote == 1 or octnote == 3 or octnote == 6 or octnote == 8 or octnote == 10)

def updateNoteColors():
  for y in range(4):
    for x in range(4):
      note = pos2note(y, x)
      trellis.pixels[(y, x)] = GREENH if isNatural(note) else REDH

updateNoteColors()

print("ready")

notes = {}
pressed = set()

while True:
  newpressed = set(trellis.pressed_keys)
  for down in newpressed - pressed:
    y = down[0]
    x = down[1]
    if x < 4:
      midinote = pos2note(y, x)
      trellis.pixels[(y, x)] = GREEN if isNatural(midinote) else RED
      prevnote = notes.get(midinote)
      if prevnote != None:
        synth.release(prevnote)
      note = synthio.Note(frequency = synthio.midi_to_hz(midinote), filter = filter)
      synth.press(note)
      notes[midinote] = note
    elif y == 3:
      trellis.pixels[(y, x)] = BLUE
      if x == 4:
        filter = None
      elif x == 5:
        filter = lpf
      elif x == 6:
        filter = hpf
      elif x == 7:
        filter = bpf
      for xx in range(4, 8):
        trellis.pixels[(y, xx)] = OFF
      trellis.pixels[(3, x)] = BLUEH
    elif y == 2:
      if x == 4:
        if a < 100:
          trellis.pixels[(y, x)] = BLUE
          a = a + 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
      elif x == 5:
        if d < 100:
          trellis.pixels[(y, x)] = BLUE
          d = d + 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
      elif x == 6:
        if s < 10:
          trellis.pixels[(y, x)] = BLUE
          s = s + 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
      elif x == 7:
        if r < 100:
          trellis.pixels[(y, x)] = BLUE
          r = r + 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
    elif y == 1:
      if x == 4:
        if a > 0:
          trellis.pixels[(y, x)] = BLUE
          a = a - 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
      elif x == 5:
        if d > 0:
          trellis.pixels[(y, x)] = BLUE
          d = d - 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
      elif x == 6:
        if s > 0:
          trellis.pixels[(y, x)] = BLUE
          s = s - 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
      elif x == 7:
        if r > 0:
          trellis.pixels[(y, x)] = BLUE
          r = r - 1
          updateEnvelope()
          trellis.pixels[(y, x)] = OFF
    elif y == 0:
      if x == 4:
        if mod > -11:
          trellis.pixels[(y, x)] = BLUE
          mod = mod - 1
          updateNoteColors()
          trellis.pixels[(y, x)] = BLUEH if mod < 0 else OFF
          trellis.pixels[(y, 5)] = BLUEH if mod > 0 else OFF
      elif x == 5:
        if mod < 11:
          trellis.pixels[(y, x)] = BLUE
          mod = mod + 1
          updateNoteColors()
          trellis.pixels[(y, 4)] = BLUEH if mod < 0 else OFF
          trellis.pixels[(y, x)] = BLUEH if mod > 0 else OFF
      elif x == 6:
        if octave > -5:
          trellis.pixels[(y, x)] = BLUE
          octave = octave - 1
          trellis.pixels[(y, x)] = BLUEH if octave < 0 else OFF
          trellis.pixels[(y, 7)] = BLUEH if octave > 0 else OFF
      elif x == 7:
        if octave < 5:
          trellis.pixels[(y, x)] = BLUE
          octave = octave + 1
          trellis.pixels[(y, 6)] = BLUEH if octave < 0 else OFF
          trellis.pixels[(y, x)] = BLUEH if octave > 0 else OFF
  for up in pressed - newpressed:
    y = up[0]
    x = up[1]
    if x < 4:
      midinote = pos2note(y, x)
      note = notes.get(midinote)
      if note != None:
        synth.release(note)
        trellis.pixels[(y, x)] = GREENH if isNatural(midinote) else REDH
  pressed = newpressed
  time.sleep(0.01)
