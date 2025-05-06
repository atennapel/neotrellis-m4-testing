import time
import board
import audioio
import adafruit_trellism4
from state import State
import synthio

BRIGHTNESS = 0.05

# initialization
trellis = adafruit_trellism4.TrellisM4Express(rotation = 90)
trellis.pixels.brightness = BRIGHTNESS
trellis.pixels.fill(0)

timestamp = time.monotonic()
print("initializing...")
state = State("/samples")
print("total samples: %d" % len(state.voices))

if state.mixer.channel_count == 1:
  audio = audioio.AudioOut(board.A1)
elif state.mixer.channel_count == 2:
  audio = audioio.AudioOut(board.A1, right_channel = board.A0)
else:
  raise RuntimeError("wav files must be mono or stereo")
audio.play(state.mixer)

# Note: synthio.Synthesizer has to be called from code.py, or else it does not seem to play any sound
# and the synths have to be created after the call to audio.play above.
synths = []
for i in range(1):
  synth = synthio.Synthesizer(channel_count = state.mixer.channel_count, sample_rate = state.mixer.sample_rate)
  synths.append(synth)
state.initializeSynths(synths)
print("initialization done, time: %f" % (time.monotonic() - timestamp))

# main loop
pressed = set()
while True:
  newpressed = set(trellis.pressed_keys)
  downs = newpressed - pressed
  ups = pressed - newpressed
  for down in downs:
    y = down[0]
    x = down[1]
    instrumentId = 0 if x < 4 else 8
    note = (3 - y) * 4 + (x % 4)
    if instrumentId >= 8:
      note = note + 60
    state.noteOn(instrumentId, note)
    trellis.pixels[down] = (255, 0, 0)
  for up in ups:
    y = up[0]
    x = up[1]
    instrumentId = 0 if x < 4 else 8
    note = (3 - y) * 4 + (x % 4)
    if instrumentId >= 8:
      note = note + 60
    state.noteOff(instrumentId, note)
    trellis.pixels[up] = 0
  pressed = newpressed
