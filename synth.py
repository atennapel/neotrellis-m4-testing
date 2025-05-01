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

filter = None
mod = 0
octave = 0

a = 2
d = 1
s = 10
r = 8

def updateEnvelope():
  synth.envelope = synthio.Envelope(attack_time = a / 10, decay_time = d / 10, sustain_level = s / 10, release_time = r / 10)

updateEnvelope()

def pos2note(y, x):
  return (60 + x) + y * 4 + mod + octave * 12

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
      prevnote = notes.get(midinote)
      if prevnote != None:
        synth.release(prevnote)
      note = synthio.Note(frequency = synthio.midi_to_hz(midinote), filter = filter)
      synth.press(note)
      notes[midinote] = note
    elif y == 3:
      if x == 4:
        filter = None
      elif x == 5:
        filter = lpf
      elif x == 6:
        filter = hpf
      elif x == 7:
        filter = bpf
    elif y == 2:
      if x == 4:
        if a < 100:
          a = a + 1
          updateEnvelope()
      elif x == 5:
        if d < 100:
          d = d + 1
          updateEnvelope()
      elif x == 6:
        if s < 10:
          s = s + 1
          updateEnvelope()
      elif x == 7:
        if r < 100:
          r = r + 1
          updateEnvelope()
    elif y == 1:
      if x == 4:
        if a > 0:
          a = a - 1
          updateEnvelope()
      elif x == 5:
        if d > 0:
          d = d - 1
          updateEnvelope()
      elif x == 6:
        if s > 0:
          s = s - 1
          updateEnvelope()
      elif x == 7:
        if r > 0:
          r = r - 1
          updateEnvelope()
    elif y == 0:
      if x == 4:
        if mod > -11:
          mod = mod - 1
      elif x == 5:
        if mod < 11:
          mod = mod + 1
      elif x == 6:
        if octave > -5:
          octave = octave - 1
      elif x == 7:
        if octave < 5:
          octave = octave + 1
  for up in pressed - newpressed:
    y = up[0]
    x = up[1]
    if x < 4:
      midinote = pos2note(y, x)
      note = notes.get(midinote)
      if note != None:
        synth.release(note)
  pressed = newpressed
  time.sleep(0.01)
